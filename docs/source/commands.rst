Commands
==================================
Jarvis commands are available through the ``jarvis.commands`` module.


.. code-block:: python

  from jarvis.commands import debug, debug_xml

  def main():
     a = "Hello World !"
     debug(a)

Displaying data
---------------

These functions are use to display data in the Jarvis panels.
All displayed strings are prefixed with a timestamp.

.. py:function:: debug(\*args):

   Display args separated by a blank space
 
.. py:function:: debug_dir(object, filt):

   Display keys in dir(object) that contains the string "filt", or all if filt is None

.. py:function:: debug_xml(args):

   Display the n first  arguments like debug would do, and the last one as an xml object

.. py:function:: debug_osg(osgdata):

   Display the osg tree "osgdata" in the osg panell

.. py:function:: debug_osg_set_loop_time(loop_time):

   Set the looping time for the osg view

.. py:function:: error(\*args):

   Display an error in the error panel.
   (If an exception is raised in your code, it will be displayed in any case)

.. py:function:: testunit_result(result):

   print an error in the error panel if any of the unittest result has an error or a failure

Here is a typical use of this function, given a unittest class called TestMyModule:

.. code-block:: python

   import unittest

   class TestMyModule(unittest.TestCase):
   ...
   def main():
    filt = "test_"
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMyModule)
    suite = filter(lambda x : str(x).startswith(filt), suite)
    suite = unittest.TestLoader().suiteClass(suite)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    # Show the test_unit in jarvis
    testunit_result(result)


.. py:function:: reset_start_time():

    Used to reset the timer used to time debug displays
    
Using the osg viewer in an external app
---------------------------------------
.. py:function:: get_osg_viewer():

   Return the osg viewer that is displayed in the osg panel

Adding files to monitor for change
----------------------------------
.. py:function:: add_watch_file

    Add a file to be watched by Jarvis. As soon as the file changes, the full code is reexecuted.

# Misc
replace_this

