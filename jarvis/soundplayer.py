import subprocess
import pyaudio
import wave
import time
import os
# also require PortAudio and ffmpeg

MAX_TMP_WAVEFILE = 5
TMP_WAV_EXTENSION = "_tmp.wav"

class BufferSegment(object):
    """ useful object to be able to map the stream time of pyaudio to the index of the sample being played"""    
    def __init__(self, start_time_reference=None, start_index_reference=0, end_time_reference=None, end_index_reference=None):
        self.set_start(start_time_reference, start_index_reference)
        self.set_end(end_time_reference, end_index_reference)

    def __repr__(self):
        return "(%s : %s) - (%s : %s)" % (repr(self.start_time_reference), repr(self.start_index_reference), repr(self.end_time_reference), repr(self.end_index_reference))

    def set_start(self, start_time_reference, start_index_reference):
        self.start_time_reference = start_time_reference
        self.start_index_reference = start_index_reference

    def set_end(self, end_time_reference, end_index_reference):
        self.end_time_reference = end_time_reference
        self.end_index_reference = end_index_reference

    def is_playing(self, stream_time):
        if self.is_incomplete():
            return False
        else:
            return (self.start_time_reference <= stream_time <= self.end_time_reference)

    def is_past(self, stream_time):
        if self.is_incomplete():
            return False
        else:
            return stream_time > self.end_time_reference

    def is_incomplete(self):
        return self.end_time_reference is None

    def get_current_index(self, stream_time):
        if self.is_playing(stream_time):
            ratio = (stream_time - self.start_time_reference) / (self.end_time_reference - self.start_time_reference)
            return int(round((1.0 - ratio) * self.start_index_reference + ratio * self.end_index_reference, 0))
        else:
            return None

class SoundPlayer(object):
    """ Sound player based on PyAudio to achieve a good sync"""

    def __init__(self, input_data, tmp_dir, frames_per_buffer=1024, start_time=0.0, end_time=None, loop_nb=1, start=False, blocking=True):
        self.tmp_dir = tmp_dir
        self.frames_per_buffer = frames_per_buffer

        if isinstance(input_data, wave.Wave_read):
            self.wavefile = input_data
        elif isinstance(input_data, str) and input_data.endswith(".wav"):
            self.wavefile = wave.open(input_data, 'rb')
        elif isinstance(input_data, str):
            name = os.path.basename(input_data)
            name, ext = os.path.splitext(name)
            tmp_file_name = os.path.join(self.tmp_dir, name + TMP_WAV_EXTENSION)

            if os.path.exists(tmp_file_name):
                wavefile_name = tmp_file_name
            else:
                wavefile_name = self._convert_file_to_wavfile(input_data, tmp_file_name, overwrite=True)
            self.wavefile = wave.open(wavefile_name, 'rb')
        else:
            raise Exception("Unsupported input_data")
        
        # PyAudio init
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(self.wavefile.getsampwidth()),
                                        channels=self.wavefile.getnchannels(),
                                        rate=self.wavefile.getframerate(),
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self._callback,
                                        output=True, start=False)

        # usefull silent sound sample
        self.empty_frame = chr(0) * self.wavefile.getsampwidth() * self.wavefile.getnchannels()
        self.empty_buffer = self.empty_frame * self.frames_per_buffer

        # sync init
        self.last_chunk_time_reference = None
        self.buffer_segments = []
        self.in_call_back = False

        # state for starting
        self.will_be_playing = False
        self.start_time = None
        self.end_time = None
        self.set_start_time(start_time)
        self.set_end_time(end_time)
        self.set_time(start_time)
        self.loop_nb = loop_nb if loop_nb is not None else 1
        self.loop_index = 0
        
        # starting stream
        self.stream.start_stream()
        
        # start playing audio
        if start:
            self.play(blocking=blocking)

    def terminate(self):
        """ stop PyAudio """
        self._check_tmp_dir()
        self.stream.stop_stream()
        self.stream.close()
        self.wavefile.close()
        self.pyaudio.terminate()

    def _check_tmp_dir(self):
        """ clean tmp dir if required starting with the oldest accessed file"""
        files = os.listdir(self.tmp_dir)
        files = filter(lambda x: x.endswith(TMP_WAV_EXTENSION), files)
        files = map(lambda name: os.path.join(self.tmp_dir, name), files)
        dates = map(os.path.getatime, files)
        files_dates = zip(files, dates)
        files_dates = sorted(files_dates, key=lambda x: x[1], reverse=True)

        while len(files_dates) > MAX_TMP_WAVEFILE:
            file, date = files_dates.pop()
            os.remove(file)
    
    def _convert_file_to_wavfile(self, input_file_name, output_file_name, overwrite=False,
                                        nchannels=None, framerate=None,
                                        no_log=True, remove_meta=False):
        """ conversion to WAV using ffmepg"""
        parameters = []
        if overwrite:
            parameters.append("-y")
        if nchannels is not None:
            parameters.extend(["-ac", str(nchannels)])
        if framerate is not None:
            parameters.extend(["-ar", str(framerate)])
        # to wav 16 bits
        parameters.extend(["-c:a", "pcm_s16le"])
        if remove_meta:
            parameters.extend(["-map_metadata", "-1", "-map", "a:0"])
        if no_log:
            parameters.extend(["-v", "fatal"])

        output_file_name = output_file_name
        print "Start ffmpeg conversion..."
        subprocess.check_call(["ffmpeg", "-i", input_file_name] + parameters + [output_file_name])
        print "ffmpeg conversion OK"
        return output_file_name

    def _get_sample_index(self, time):
        return max(0, min(self.wavefile.getnframes() - 1, int(round(self.wavefile.getframerate() * time, 0))))
    
    def _get_sample_time(self, index):
        return index / float(self.wavefile.getframerate())

    def _callback(self, in_data, frame_count, time_info, status):
        self.in_call_back = True
        output_buffer_dac_time = time_info["output_buffer_dac_time"]

        # might be a good idea to lock/mutex buffer_segments
        self.clean_buffer_segments(nb_to_keep=1)
        last_buffer_segment = self.buffer_segments[-1]

        if self.will_be_playing:

            if last_buffer_segment.is_incomplete():
                self.wavefile.setpos(last_buffer_segment.start_index_reference)
                last_buffer_segment.start_time_reference = output_buffer_dac_time

            current_sample = self.wavefile.tell()

            if self.end_time is not None:
                end_sample_index = self._get_sample_index(self.end_time)
            else:
                end_sample_index = self.wavefile.getnframes() - 1

            frame_count_to_end = max(0, end_sample_index - current_sample + 1)
            if frame_count_to_end >= self.frames_per_buffer:
                # enough data to fill the buffer
                data = self.wavefile.readframes(self.frames_per_buffer)
                self.buffer_segments[-1].set_end(output_buffer_dac_time + self._get_sample_time(self.frames_per_buffer), current_sample + self.frames_per_buffer)
            else:
                # not enough data to fill the buffer
                # fill with end of data
                data = self.wavefile.readframes(frame_count_to_end)
                self.buffer_segments[-1].set_end(output_buffer_dac_time + self._get_sample_time(frame_count_to_end), current_sample + frame_count_to_end)
                self.loop_index += 1

                start_sample_index = self._get_sample_index(self.start_time)
                loop_size = end_sample_index - start_sample_index + 1
                # fill with loop
                while (self.loop_nb == 0 or self.loop_index < self.loop_nb) and frame_count_to_end < self.frames_per_buffer:
                    self.wavefile.setpos(start_sample_index)
                    start_time_reference = output_buffer_dac_time + self._get_sample_time(frame_count_to_end)
    
                    feeding_size = min(loop_size, self.frames_per_buffer - frame_count_to_end)
                
                    start_index_reference = self.wavefile.tell()
                    data += self.wavefile.readframes(feeding_size)
                    frame_count_to_end += feeding_size
                    end_index_reference = self.wavefile.tell()
                    end_time_reference = start_time_reference + self._get_sample_time(feeding_size)
                    new_buffer_segment = BufferSegment(start_time_reference, start_index_reference, end_time_reference, end_index_reference)
                    self.buffer_segments.append(new_buffer_segment)

                    if frame_count_to_end < self.frames_per_buffer:
                        self.loop_index += 1
                # fill with silence
                if frame_count_to_end < self.frames_per_buffer:
                    self.will_be_playing = False
                    padding = self.empty_frame * (self.frames_per_buffer - frame_count_to_end)
                    data = data + padding

        else:
            # silent buffer
            data = self.empty_buffer
            if not last_buffer_segment.is_incomplete():
                current_sample = self.wavefile.tell()
                self.queue_segment(current_sample)

        self.last_chunk_time_reference = output_buffer_dac_time
        self.in_call_back = False        
        return (data, pyaudio.paContinue)

    def clean_buffer_segments(self, nb_to_keep=1):
        if len(self.buffer_segments) > 0:
            stream_time = self.stream.get_time()
            while len(self.buffer_segments) > nb_to_keep and self.buffer_segments[0].is_past(stream_time):
                self.buffer_segments.pop(0)

    def queue_segment(self, sample_index_to_play):
        new_buffer_segment = BufferSegment(start_index_reference=sample_index_to_play)
        if len(self.buffer_segments) > 0:
            last_buffer_segment = self.buffer_segments[-1]
            if last_buffer_segment.is_incomplete():
                self.buffer_segments.pop()
        self.buffer_segments.append(new_buffer_segment)

    def play(self, start_time=None, end_time=None, loop_nb=None, blocking=True):
        if loop_nb is not None:
            self.loop_nb = loop_nb
            self.loop_index = 0

        if self.loop_nb==0 and blocking:
            raise Exception("loop_nb can't be 0 (=infinite) when blocking is true")

        if end_time is not None:
            self.set_end_time(end_time)

        if start_time is not None:
            self.set_time(start_time)        

        self.will_be_playing = True

        while blocking and (self.will_be_playing or self.is_playing):
            time.sleep(0.1)

    def pause(self):
        self.will_be_playing = False

    stop = pause

    def _is_playing(self):
        stream_time = self.stream.get_time()        
        for buffer_segment in self.buffer_segments:
            if buffer_segment.is_playing(stream_time):
                return True
        return False
    is_playing = property(_is_playing)

    def get_time(self):
        # get_time cannot return value during callback (buffer segments are changing)
        while self.in_call_back:
            time.sleep(0.01)

        if len(self.buffer_segments) == 0:
            return self._get_sample_time(self.wavefile.tell())

        stream_time = self.stream.get_time()
        
        for buffer_segment in self.buffer_segments:
            if buffer_segment.is_playing(stream_time):
                current_index = buffer_segment.get_current_index(stream_time)
                return self._get_sample_time(current_index)

        first_buffer_segment = self.buffer_segments[0]
        if first_buffer_segment.is_past(stream_time):
            current_index = first_buffer_segment.end_index_reference
        else:
            current_index = first_buffer_segment.start_index_reference
        return self._get_sample_time(current_index)

    def set_time(self, t, compensate_buffer=False):
        if compensate_buffer and self.last_chunk_time_reference is not None:
            next_feeding_time = self.last_chunk_time_reference + self._get_sample_time(self.frames_per_buffer)
            offset_to_next_feeding_time =  next_feeding_time - self.stream.get_time()
        else:
            offset_to_next_feeding_time = 0.0
        sample_index = self._get_sample_index(t + offset_to_next_feeding_time)
        
        self.queue_segment(sample_index)

    def set_start_time(self, t):
        if t is None:
            self.start_time = 0.0
            return
        if not (0.0 <= t <= self.get_duration()):
            print "Warning : start_time (%.3f) clamped between 0.0 and sound duration (%.3f)" % (t, self.get_duration())
            t = max(0.0, min(t, self.get_duration()))
        if self.end_time is not None and t >= self.end_time:
            raise Exception("start_time (%.3f) must be lower than end_time (%.2f)" % (t, self.end_time))
        self.start_time = t

    def set_end_time(self, t):
        if t is None:
            self.end_time = None
            return
        if not (0.0 <= t <= self.get_duration()):
            print "Warning : end_time (%.3f) clamped between 0.0 and sound duration (%.3f)" % (t, self.get_duration())
            t = max(0.0, min(t, self.get_duration()))
        if self.start_time is not None and t <= self.start_time:
            raise Exception("end_time (%.3f) must be lower than start_time (%.3f)" % (t, self.start_time))
        self.end_time = t

    def set_loop_time(self, start_time, end_time):
        self.set_end_time(None)
        self.set_start_time(start_time)
        self.set_end_time(end_time)
        if not (start_time <= self.get_time() <= end_time):
            self.set_time(start_time)

    def get_duration(self):
        return self._get_sample_time(self.wavefile.getnframes())

# tests
if __name__ == "__main__":
    TMP_DIR = "/Users/perenono/test/tmp/"
    FILE = "/Users/perenono/Music/iTunes/iTunes Media/Music/Daft Punk/Random Access Memories/08 Get Lucky (feat. Pharrell Williams & Nile Rodgers).m4a"

    print "Default mode (no auto-start, blocking)"
    s = SoundPlayer(FILE, TMP_DIR, start_time=0.0, end_time=2.0)
    s.play()
    s.terminate()

    time.sleep(1)

    print "Auto-start"
    s = SoundPlayer(FILE, TMP_DIR, start_time=0.0, end_time=2.0, start=True)
    s.terminate()

    time.sleep(1)

    print "Loop"
    s = SoundPlayer(FILE, TMP_DIR, start_time=0.0, end_time=0.5, start=True, loop_nb=4)
    s.terminate()

    time.sleep(1)

    print "Non-blocking mode"
    s = SoundPlayer(FILE, TMP_DIR, start_time=0.0, end_time=2.0, start=True, blocking=False)
    while s.is_playing or s.will_be_playing:
        print "%.1f / %.1f" % (s.get_time(), s.get_duration())
        time.sleep(0.1)
    s.terminate()