BUFFER_NAME = "*jarvis_inspect*"

if 'arg' in globals():
    from Pymacs import lisp
    import jarvis.emacs.utils as utils
    import jarvis.commands

    # Retrieve current buffer file name
    filename = lisp.buffer_file_name()

    # Sample code : break on whitespace
    line = utils.cursor_line_number()

    # The +1 is because we prefer to have the result of an assignation when the cursor is on it, not one line later.
    var_info = jarvis.commands.external_inspect_vars(filename, line + 1)

    new_var_info = ""
    infos = eval(var_info.split("\n")[1])
    for time, info in infos:
        new_var_info  += "Executed at %ss\n" % time

        context = []
        for k,v in info.iteritems():
            context += [(k,v)]
            
        context.sort(key = lambda x : - x[1][0])

        for k, info in context:
            new_var_info += "  %s => %s\n" % (k, info[1])
            
    var_info = new_var_info
    
    found = False
    for window in lisp.window_list():
        buffer = lisp.window_buffer(window)
        if lisp.buffer_name(buffer) == BUFFER_NAME:
            found = True
        

    buffer = lisp.get_buffer_create(BUFFER_NAME)
    lisp.set_buffer(buffer)
    lisp.erase_buffer()
    lisp.insert(str(var_info))

    if not found:
        lisp.split_window_vertically(-10)
        lisp.other_window(1)
        lisp.switch_to_buffer(buffer)
        lisp.goto_line(1)
        lisp.other_window(1)
    
