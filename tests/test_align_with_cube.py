from easy_cozmo import *

def cozmo_program():
    set_volume_low()
    if align_with_nearest_cube():
        say_text("Aligned success")
    else:
        say_text("Aligned failed")

run_program_with_viewer(cozmo_program)
