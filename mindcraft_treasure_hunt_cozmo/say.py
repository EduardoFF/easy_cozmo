def _say_error(errormsg, *args):
    """**Say "ERROR" followed by a message**

    Cozmo will indicate using its voice that an error occurred.  It
    also prints a message in the console indicating the error
    message.

    :return: True (suceeded) or False (failed)
    """
    from .easy_cozmo import _robot

    #errormsg = "ERROR, "+errormsg
    errormsg = errormsg + ' '.join(map(str, args))
    print("ERROR ",errormsg)
#    _robot.say_text(errormsg).wait_for_completed()

def say_error(errormsg):
    """**Say "ERROR" followed by a message**

    Cozmo will indicate using its voice that an error occurred.  It
    also prints a message in the console indicating the error
    message.

    :return: True (suceeded) or False (failed)
    """
    from .easy_cozmo import _robot

    errormsg = "ERROR, "+errormsg
    print(errormsg)
    _robot.say_text(errormsg).wait_for_completed()

def say(txtmsg, *args):
    """**Say a simple message**

    Cozmo will read a message and display the message in the
    console.

    ..  note::

            This function receives a variable number or arguments. All arguments will be concatenated and delimited by a space, in order to compose the message. This is useful to compose sentences.

    :return: True (suceeded) or False (failed)
    """

    from .easy_cozmo import _robot

    txtmsg = txtmsg + ' '.join(map(str, args))
    print("SAY: "+txtmsg)
    _robot.say_text(txtmsg).wait_for_completed()

def _say(txtmsg, *args):
    """**Print  a simple message **

    Cozmo will read a message and display the message in the
    console.

    ..  note::

            This function receives a variable number or arguments. All arguments will be concatenated and delimited by a space, in order to compose the message. This is useful to compose sentences.

    :return: True (suceeded) or False (failed)
    """

    from .easy_cozmo import _robot

    txtmsg = txtmsg + ' '.join(map(str, args))
    print("SAY: "+txtmsg)
