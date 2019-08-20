===========
easy_cozmo
===========

easy_cozmo provides a bunch of python wrappers for Anki Cozmo's SDK. You might
find it most useful for educational tasks involving students with little CS
background. This library was created for a series of workshops for high shool
students in Qatar. The code has been used by over 1,000 students over one year.
Typical usage often looks like this::

    """
    Makes cozmo saying "hello world"
    """

    from easy_cozmo import *

    def cozmo_program():
    	say("Hello world")

    run_program_with_viewer(cozmo_program)


Documentation
===============


`Take a look at the documentation <http://www.example.com/foo/bar>`_.
