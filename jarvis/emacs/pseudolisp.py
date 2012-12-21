class Lisp(object):
    def __init__(self):
        pass

    def buffer_file_name(self):
        return raw_input("input filename:")

    def completing_read(self, message, options):
        ret = None
        while ret not in options:
            ret = raw_input(message + " Available options are: " + ",".join(options) + "  \n")
            if ret in options:
                return ret
            else:
                print "Invalid option"
                    
    def find_file(self, filename):
        print "File was created at\n %s" % filename

    def j_test_filename_function_set(self, *args, **kwargs):
        pass

    def insert(self, s):
        print s
