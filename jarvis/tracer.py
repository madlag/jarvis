"""This module is intended for tracing code and doing 'post mortem' inspection of objects.
Typical usage is
  - create Tracer object 'tracer'
  - tracer.install()
  - RUN YOUR CODE
  - tracer.uninstall()
  - tracer.inspect(file, line)

KNOWN ISSUE : RUN YOUR CODE cannot be at the same level than install / uninstall, it must be in a function call. I don't know why yet.
"""

import sys
import inspect
import copy
import time
import traceback

class Tracer(object):
    def __init__(self, file_white_list = None):
        self.run_info = {}
        self.last_trace_data_stack = [{}]
        self.file_white_list = file_white_list

    def istracing(self, filename):
        return filename in self.file_white_list

    def create_new_run_info(self, file, line, data, dedupCheck):
        # Create the record for this file / line
        if file not in self.run_info:
            self.run_info[file] = {}
        if line not in self.run_info[file]:
            self.run_info[file][line] = []
        if not dedupCheck or len(self.run_info[file][line]) == 0:
            # Record time, and append the information to the set of track (getting through a line may happen several time !)
            self.run_info[file][line] += [(time.time() - self.start_time, data)]
        # Record the last data for comparison at next step
        self.last_trace_data_stack[-1] = data

    def print_exception(self, msg):
        return
        print msg, "\n", traceback.format_exc()

    def object_repr(self, object):
        return repr(object)

    def trace_frame(self, frame, event, arg):
        """Trace a single frame.
        This try to determine which var changed, and at which time.
        This then allows to sort the variables by younger change to older one."""
        if event.startswith("c_"):
            return self.trace_frame

        if event == "call":
            # Push empty last_trace data
            self.last_trace_data_stack += [{}]


        try:
            # Get the current file name and current line number
            filename = inspect.getfile(frame)

            if self.file_white_list != None:
                if filename not in self.file_white_list:
                    return self.trace_frame

            linenumber = frame.f_lineno
            # Get the right trace_data
            last_trace_data = self.last_trace_data_stack[-1]

            # Compare the locals with the previous ones
            new_trace_data = {}

            # Enumerate the locals
            for k, v in frame.f_locals.iteritems():
                try:
                    # Check if the values are the same as in the previous frame info
                    same = False

                    # Check if i
                    if k in last_trace_data:
                        # You may try different object representation, that explains the enumeration
                        for vv in [self.object_repr(v)]:
                            try:
                                # Check if last data is the same (object at index 0 is "framestamp")
                                if last_trace_data[k][1] == vv:
                                    same = True
                                break
                            except:
                                self.print_exception("CASE 1")

                    if not same:
                        # Not same: store the new version
                        for vv in [self.object_repr(v)]:
                            try:
                                # Store the record ("framestamp", data)
                                new_trace_data[k] = [self.frame_counter, vv]
                                # Increment frame_counter
                                self.frame_counter += 1
                            except:
                                self.print_exception("CASE 2")
                    else:
                        # It's the same : keep the last ("framestamp", data) record
                        new_trace_data[k] = last_trace_data[k]

                except:
                    self.print_exception("CASE 3")

            # Create the record for this frame
            self.create_new_run_info(filename, linenumber, new_trace_data, event == "return")
        except:
            self.print_exception("CASE 4")

        if event == "return":
            self.last_trace_data_stack = self.last_trace_data_stack[:-1]

        return self.trace_frame

    def install(self):
        """Install the tracer"""
        self.start_time = time.time()
        self.frame_counter = 0
        sys.settrace(self.trace_frame)

    def uninstall(self):
        """Uninstall the tracer"""
        sys.settrace(None)

    def inspect(self, file, line):
        """Inspect a single line in a file"""

        for i in range(0, 10):
            ret = self.run_info.get(file, {}).get(line + i)
            if ret:
                return ret

        return ret

    def inspect_all(self):
        """Dump all the information stored"""
        for k,v in self.run_info.iteritems():
            print "file=", k
            keys = v.keys()
            keys.sort()

            for k in keys:
                print "line = %s, data =%s" % (k, v[k])
