
class FPSCalculator(object):
    """ Simple class to compute the number of frame by second. The result is
        smoothed according the number of frames to smooth in parameter.
    """

    def __init__(self, start_time=0.0, smoothness=20):
        self.smoothness = smoothness
        self.reset(start_time=start_time)

    def reset(self, start_time=0.0):
        self.saved_times = [start_time]

    def get(self, current_time):
        self.saved_times.append(current_time)
        if len(self.saved_times) == 1:
            return 0.0
        frames_nb = len(self.saved_times) - 1
        elapsed_time = self.saved_times[-1] - self.saved_times[0]
        fps = int(frames_nb / elapsed_time)
        if len(self.saved_times) == self.smoothness:
            self.saved_times.pop(0)
        return fps