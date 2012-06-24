BUFFER_NAME = "*jarvis_inspect*"

VAR_KEY = "inspect_vars_timer_installed"

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

    var_info = utils.inspect_format(var_info)

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

#    if not timer_installed:

    timer_installed = utils.get_command_global_var(VAR_KEY, False)
    if not timer_installed:
        utils.set_command_global_var(VAR_KEY, True)
        # This is a bit unstable right now, it trigger refresh of the window when needed ...
        #lisp.run_at_time(True, 1.0, lisp.j_inspect_vars_refresh)
