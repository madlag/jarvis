if 'arg' in globals():
    from Pymacs import lisp

    # Retrieve current buffer file name
    filename = lisp.buffer_file_name()
    
    # Sample code : break on whitespace
    start, end = lisp.point(), lisp.mark(True)
    words = lisp.buffer_substring(start, end).split("\n")

    words = map(lambda x : x.rstrip(" "), words)
    lisp.delete_region(start, end)        
    lisp.insert('\n'.join(words))
