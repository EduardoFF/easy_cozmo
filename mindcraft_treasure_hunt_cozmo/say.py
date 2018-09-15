def _say_error(errormsg, *args):
    """**Say "ERROR" followed by a message**

    Cozmo will indicate using its voice that an error occurred.  It
    also prints a message in the console indicating the error
    message.

    :return: True (suceeded) or False (failed)
    """
    from .mindcraft import _mycozmo
    
    #errormsg = "ERROR, "+errormsg
    errormsg = errormsg + ' '.join(map(str, args))
    print("ERROR ",errormsg)
#    _mycozmo.say_text(errormsg).wait_for_completed()
    
def say_error(errormsg):
    """**Say "ERROR" followed by a message**

    Cozmo will indicate using its voice that an error occurred.  It
    also prints a message in the console indicating the error
    message.

    :return: True (suceeded) or False (failed)
    """
    from .mindcraft import _mycozmo
    
    errormsg = "ERROR, "+errormsg
    print(errormsg)
    _mycozmo.say_text(errormsg).wait_for_completed()

def say(txtmsg, *args):
    """**Say a simple message**

    Cozmo will read a message and display the message in the
    console.

    ..  note::

            This function receives a variable number or arguments. All arguments will be concatenated and delimited by a space, in order to compose the message. This is useful to compose sentences.

    :return: True (suceeded) or False (failed)
    """

    from .mindcraft import _mycozmo

    txtmsg = txtmsg + ' '.join(map(str, args))
    print("SAY: "+txtmsg)
    _mycozmo.say_text(txtmsg).wait_for_completed()

def _say(txtmsg, *args):
    """**Print  a simple message **

    Cozmo will read a message and display the message in the
    console.

    ..  note::

            This function receives a variable number or arguments. All arguments will be concatenated and delimited by a space, in order to compose the message. This is useful to compose sentences.

    :return: True (suceeded) or False (failed)
    """

    from .mindcraft import _mycozmo

    txtmsg = txtmsg + ' '.join(map(str, args))
    print("SAY: "+txtmsg)
