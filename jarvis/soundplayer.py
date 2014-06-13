import subprocess
import pyaudio
import wave
import time
import os
# also require PortAudio and ffmpeg

MAX_TMP_WAVEFILE = 5
TMP_WAV_EXTENSION = "_tmp.wav"

class SoundPlayer(object):

    def __init__(self, input_file_name, tmp_dir, start_time=0.0, end_time=None, start=True, blocking=False, chunk_size=1024):
        self.chunk_size = chunk_size
        self.is_playing = False

        if input_file_name.endswith(".wav"):
            self.wavefile = wave.open(input_file_name, 'rb')
        else:
            name = os.path.basename(input_file_name)
            name, ext = os.path.splitext(name)
            tmp_file_name = os.path.join(tmp_dir, name + TMP_WAV_EXTENSION)

            if os.path.exists(tmp_file_name):
                wavefile_name = tmp_file_name
            else:
                self._check_tmp_dir(tmp_dir)
                wavefile_name = self._convert_file_to_wavfile(input_file_name, tmp_file_name, overwrite=True)
            self.wavefile = wave.open(wavefile_name, 'rb')
        
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=self.pyaudio.get_format_from_width(self.wavefile.getsampwidth()),
                                        channels=self.wavefile.getnchannels(),
                                        rate=self.wavefile.getframerate(),
                                        frames_per_buffer=self.chunk_size,
                                        stream_callback=self._callback,
                                        output=True, start=False)

        self.last_time_feeding = self.stream.get_time()
        self.set_time(start_time)
        self.set_end_time(end_time)
        self.stream.start_stream()
        if start:
            self.play(blocking=blocking)

    def _check_tmp_dir(self, tmp_dir):
        files = os.listdir(tmp_dir)
        files = filter(lambda x: x.endswith(TMP_WAV_EXTENSION), files)
        files = map(lambda name: os.path.join(tmp_dir, name), files)
        dates = map(os.path.getatime, files)
        files_dates = zip(files, dates)
        files_dates = sorted(files_dates, key=lambda x: x[1], reverse=True)

        while len(files_dates) > MAX_TMP_WAVEFILE:
            file, date = files_dates.pop()
            os.remove(file)

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wavefile.close()
        self.pyaudio.terminate()
    
    def _convert_file_to_wavfile(self, input_file_name, output_file_name, overwrite=False,
                                        nchannels=None, framerate=None,
                                        no_log=True, remove_meta=False):
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
        subprocess.check_call([ "/usr/local/bin/ffmpeg", "-i", input_file_name] + parameters + [output_file_name])
        print "ffmpeg OK"
        return output_file_name

    def _get_sample_index(self, t):
        return max(0, min(self.wavefile.getnframes() - 1, int(round(self.wavefile.getframerate() * t, 0))))

    def _callback(self, in_data, frame_count, time_info, status):
        self.last_time_feeding = self.stream.get_time()

        sample_size = self.wavefile.getnchannels() * self.wavefile.getsampwidth()
        empty_sample = chr(0) * sample_size
        
        if self.is_playing:
            
            if self.end_time is not None:
                end_sample_index = self._get_sample_index(self.end_time)
            else:
                end_sample_index = self.wavefile.getnframes() - 1

            current_sample = self.wavefile.tell()        
            frame_count_to_end = max(0, end_sample_index - current_sample + 1)

            if frame_count_to_end <= self.chunk_size:
                data = self.wavefile.readframes(frame_count_to_end) + empty_sample * (self.chunk_size - frame_count_to_end)
                self.is_playing = False
            else:
                data = self.wavefile.readframes(frame_count)
        else:
            data = empty_sample * self.chunk_size
        return (data, pyaudio.paContinue)

    def play(self, start_time=None, end_time=None, blocking=False):
        if end_time is not None:
            self.set_end_time(end_time)

        if start_time is not None:
            self.set_time(start_time)        

        self.is_playing = True

        while blocking and self.is_playing:
            time.sleep(0.1)

    def pause(self):
        self.is_playing = False

    stop = pause

    def get_time(self):
        elapsed_time = self.stream.get_time() - self.last_time_feeding
        return (self.wavefile.tell() - self.chunk_size) / float(self.wavefile.getframerate()) + elapsed_time

    def set_time(self, t):
        elapsed_time = self.stream.get_time() - self.last_time_feeding
        offset_to_next_feeding_time = self.chunk_size / self.wavefile.getframerate() - elapsed_time
        sample_index = self._get_sample_index(t + offset_to_next_feeding_time)
        self.wavefile.setpos(sample_index)

    def set_end_time(self, t):
        self.end_time = t

    def get_duration(self):
        return self.wavefile.getnframes() / float(self.wavefile.getframerate())

# tests
if __name__ == "__main__":
    s = SoundPlayer("/Users/perenono/test/Akashic_Records_-_Feel_Good_Acoustic_Ukulele.mp3", "/Users/perenono/test/tmp2.wav", start_time=205, start=True, blocking=False)
    print s.get_duration()
    time.sleep(1)
    s.terminate()

    print "new init"
    s = SoundPlayer("/Users/perenono/test/Akashic_Records_-_Feel_Good_Acoustic_Ukulele.mp3", "/Users/perenono/test/tmp2.wav", start_time=205, start=True, blocking=False)
    time.sleep(1)
    # s.set_time(0)
    # s.set_end_time(5)
    # time.sleep(1)
    # s.play(blocking=False)
    # while s.is_playing:
    #     print s.get_time()
    #     time.sleep(0.01)

    # time.sleep(6)
    # s.play(0.0, 2.0)
    # print time.time()
    s.terminate()