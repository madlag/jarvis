Jarvis emacs bindings
==================================

.. _Pymacs: http://pymacs.progiciels-bpi.ca/index.html

.. _jarvis.el: https://github.com/madlag/jarvis/blob/master/jarvis/emacs/jarvis.el 

.. _jinja2: http://jinja.pocoo.org/

Those bindings are available through Pymacs_. You will have to install it if you want to use the jarvis commands in emacs.
You will have to install jinja2_ too.

Once Pymacs is installed, you will have to copy or require jarvis.el_ file in your own ~/.emacs init file. The typical content of this file is :

.. code-block:: none

  ;; Initialize Jarvis
  (pymacs-load "jarvis.emacs" "j-")
  (global-set-key (kbd "C-x g") 'j-goto-error)
  (global-set-key (kbd "C-x i") 'j-inspect-vars)

The first line tell pymacs to load jarvis.emacs and then to prefix the jarvis command with "j-" . You can change that, but I will assume that you are using this prefix below.

So, all the commands below will appear prefixed by j- , you will be able to see them using by typing "M-x j- TAB" in emacs once everything is installed correctly.


Basic functions
---------------

**launch:**
  Launch jarvis. It will start with the last known entry point.

**test_this**
  Tell Jarvis to load the current file, and then to run the *main* function.

**test_filename_function_set**
  The argument to this function should looks like `file:function` .
  Tell Jarvis to load the file, and then to run the function in this file.

Code interaction
----------------

**inspect_vars**
  Request local variables in the current file at the current line. They will be displayed in a `*jarvis_inspect*` buffer .

**goto_error**
  Go to the last error that was displayed in the error panel.

**paste_debug_buffer**
  Paste the content of the debug panel at the current cursor position.

Creating new commands
---------------------

The commands or snippets created by the following two functions will be created in your ~/.jarvis.d directory. They will appear as new j- prefixed commands. You can modify those commands and test them inside emacs without restarting jarvis, they are completely dynamic.

**new_command**
  Create a new command. Will ask for a command name, and will write a file with a typical command code, with the right filename.

**new_snippet**
  Create a new command. Will ask for a command name, and will write a file with a typical command code, with the right filename.

Misc
----------------
**test_create**
  This will create a test file, given the current python file. It will look for a *tests* directory somewhere, or will ask for one if not found.

**google**
  Ask for a query then open a browser with google search.
