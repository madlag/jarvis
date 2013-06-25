import jarvis
import jarvis.client as client

def main():
    test_filename_function = arg[0]
    test_filename_function_path = jarvis.get_filename(jarvis.TEST_FILENAME_FUNCTION)

    f = open(test_filename_function_path, "w")
    f.write(test_filename_function)
    f.close()

    print test_filename_function
    client.Client().update("test_filename_function", "set", test_filename_function)

    

if "arg" in globals():
    main()
