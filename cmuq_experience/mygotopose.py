from cozmo import action
import cozmoclad.clad.types.pathMotionProfile as pmp
from cozmo._clad import _clad_to_engine_iface
class MyGoToPose(action.Action):
    '''Represents the go to pose action in progress.
    Returned by :meth:`~cozmo.robot.Robot.go_to_pose`
    '''
    def __init__(self, pose, **kw):
        super().__init__(**kw)
        self.pose = pose

    def _repr_values(self):
        return "pose=%s" % (self.pose)

    def _encode(self):
        motionprof = pmp.Anki.Cozmo.PathMotionProfile(speed_mmps=80.0,
                                       accel_mmps2=400.0,
                                       decel_mmps2=500.0,
                                       pointTurnSpeed_rad_per_sec=0.7,
                                       pointTurnAccel_rad_per_sec2=0.7,
                                       pointTurnDecel_rad_per_sec2=0.7,
                                       dockSpeed_mmps=60.0,
                                       dockAccel_mmps2=200.0,
                                       dockDecel_mmps2=500.0,
                                       reverseSpeed_mmps=80.0,
                                                      isCustom=True)
       # motionprof = pmp.Anki.Cozmo.PathMotionProfile()
        gtp= _clad_to_engine_iface.GotoPose(x_mm=self.pose.position.x,
                                              y_mm=self.pose.position.y,
                                              rad=self.pose.rotation.angle_z.radians)
        #print(gtp, type(gtp))
       # print(gtp.motionProf, type(gtp.motionProf))
        gtp._motionProf = motionprof
        #gtp.motionProf=motionprof
        return gtp


