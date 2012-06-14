import jarvis

def main():
    test_filename_function = arg[0]
    test_filename_function_path = jarvis.get_filename(jarvis.TEST_FILENAME_FUNCTION)

    f = open(test_filename_function_path, "w")
    f.write(test_filename_function)
    f.close()

if "arg" in globals():
    main()
