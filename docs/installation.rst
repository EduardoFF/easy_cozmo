.. _installation:

Installation
============

Python Version
--------------

We recommend using the latest version of Python 3::

  pip install easy_cozmo

Dependencies
------------

These distributions will be installed automatically when installing the library.


Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

These distributions will not be installed automatically. This library will
detect and use them only if you install them.

* `reindent`_ provides automatic reindentation.

.. _reindent: https://pypi.org/project/Reindent/

Configuring Sublime 3 to run programs with the pycozmo tool
-------------------------------------------------------------

Windows
~~~~~~~~~

1. Add the bin folder to the PATH variable

2. Copy the file :file:`pycozmo.sublime-build` into the :file:`AppData\\Roaming\\Sublime Text 3\\Packages\\User` folder

3. Open Sublime 3

4. Set build system to pycozmo
