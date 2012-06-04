if 'arg' in globals():
    from Pymacs import lisp
    import jarvis.emacs.utils as utils

    # Sample code : break on whitespace
    start, end = lisp.point(), lisp.mark(True)
    text = lisp.buffer_substring(start, end)

    rewriteRules = {';':'', '::':'.', '( ': '(', ' )':')', '->':'.', 'new ':'', '//':'#'}
    for k,v in rewriteRules.iteritems():    
        text = text.replace(k,v)
    
    lisp.delete_region(start, end)
    lisp.insert(text)
