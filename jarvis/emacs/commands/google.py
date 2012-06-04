from Pymacs import lisp
import urllib

def main():
    query = urllib.urlencode({"q":arg[0]})
    lisp.browse_url("https://www.google.com/search?hl=en&%s" % query)

if "arg"  in globals():
    main()


    
