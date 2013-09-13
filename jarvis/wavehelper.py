import numpy
import wave

class WaveReader():
    def __init__(self, filename):
        self.filename = filename
        self.reader = wave.open(filename)

    def read(self, length):
        out = self.reader.readframes(length)
        return numpy.fromstring(out, dtype=numpy.dtype('<i2'))

class WaveSink(object):
    # max is used to renormalize audio from float stream to short int stream
    def __init__(self, input, outputFileName, duration, skip = 0.0, framerate = 44100, channels = 2):
        self.framerate = framerate
        self.channels = channels
        self.input = input
        self.duration = duration
        self.skip = skip
        self.bufferSamples = int(self.channels * self.framerate * self.duration)

        output = wave.open(outputFileName, "w")
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(framerate)

        self.output = output

    def sizeToTime(self, size):
        return float(size) / float(self.framerate * self.channels * 2)

    def timeToSize(self, time):
        return int(time * self.framerate * self.channels * 2)

    def run(self):
        previousTotalRead = 0
        totalRead = 0

        BLOCK_SIZE = int(min(1.0, self.duration / 3.0) * self.framerate)

        skipSize = self.timeToSize(self.skip)
        totalSize = self.timeToSize(self.skip + self.duration)        
        
        while(True):            
            out = self.input.read(BLOCK_SIZE)

            if out == None:
                break
            
            ar = numpy.array(out, dtype=numpy.dtype('<i2'))
            outStr = ar.tostring()
            
            if len(outStr) == 0:
                break

            previousTotalRead = totalRead
            totalRead += len(outStr)
            
            if totalRead <= skipSize:
                continue
            if previousTotalRead > totalSize:
                break
            if previousTotalRead < skipSize and totalRead > skipSize:
                outStr = outStr[skipSize - previousTotalRead:]                
            if totalRead > totalSize:
                outStr = outStr[: - (totalRead - totalSize)]
                
            self.output.writeframes(outStr)
            
        self.output.close()


    def close(self):
        try:
            self.output.close()
        finally:
            self.input.close()            
