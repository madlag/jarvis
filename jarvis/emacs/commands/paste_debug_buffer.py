if 'arg' in globals():
    from Pymacs import lisp
    import jarvis

    debug_file = jarvis.get_filename(jarvis.DEBUG_FILE)

    # Sample code : break on whitespace
    lisp.insert(open(debug_file).read())
