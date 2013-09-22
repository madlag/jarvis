import jarvis
import jarvis.client as client

def main():
    test_filename_function = arg[0]    
    client.Client().update("test_filename_function", "set", test_filename_function)

    

if "arg" in globals():
    main()
