
class FPSCalculator(object):
    """ Simple class to compute the number of frame by second. The result is
        smoothed according the number of frames to smooth in parameter.
    """

    def __init__(self, smoothness=20):
        self.saved_times = [0.0]
        self.smoothness = smoothness

    def get(self, current_time):
        self.saved_times.append(current_time)
        if self.saved_times[-1] - self.saved_times[0] <= 0:
            self.saved_times = [0.0]
            return 0.0
        fps = int((len(self.saved_times) - 1) / (self.saved_times[-1] - self.saved_times[0]))
        if len(self.saved_times) == self.smoothness:
            self.saved_times.pop(0)
        return fps