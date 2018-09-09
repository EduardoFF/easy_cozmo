from .mindcraft_defaults import _df_volume

def initialize_robot(robot):
    robot.enable_all_reaction_triggers(False)
    # todo: disable it by default
#    robot.enable_facial_expression_estimation(False)
    robot.set_robot_volume(_df_volume)
    robot.set_lift_height(0).wait_for_completed()
    robot.world.disconnect_from_cubes()
