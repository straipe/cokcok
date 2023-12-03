# from django.templatetags.static import static
import os


def constant(func):
    def func_set(self, value):
        raise TypeError
    
    def func_get(self):
        return func()
    return property(func_get, func_set)

class _Const(object):
    # @constant
    # def CURRENT_PATH():
    #     return static('core/')

    @constant
    def CURRENT_PATH():
        return os.path.dirname(os.path.abspath(__file__)) + '/data'
    
    @constant
    def ACCX():
        return 'AccelerationX'
    
    @constant
    def ACCY():
        return 'AccelerationY'
    
    @constant
    def ACCZ():
        return 'AccelerationZ'
    
    @constant
    def RVP():
        return 'RRX'
    
    @constant
    def RVR():
        return 'RRY'
    
    @constant
    def RVY():
        return 'RRZ'
    
    @constant
    def PITCH():
        return 'Pitch'
    
    @constant
    def ROLL():
        return 'Roll'
    
    @constant
    def YAW():
        return 'Yaw'
    
    @constant
    def TIMESTAMP():
        return 'Timestamp'
    
    @constant
    def FEATURE():
        return 'Feature'
    
    @constant
    def VALUE():
        return 'Value'
    
    # for Analysis
    @constant
    def SWING_WINDOW_SIZE():
        return 8
    
    @constant
    def SWING_BEFORE_IMPACT():
        return 15
    
    @constant
    def SWING_AFTER_IMPACT():
        return 15
    

    # for Classification
    @constant
    def CLASS_STROKE():
        return ['bd', 'bn', 'bh', 'bu', 'fd', 'fp', 'fn', 'fh', 'fs', 'fu', 'ls', 'ss']
    
    @constant
    def CLASS_START():
        return 'StartFrame'
    
    @constant
    def CLASS_END():
        return 'EndFrame'
    
    @constant
    def CLASS_WINDOW_SIZE():
        return 30
    
    @constant
    def CLASS_ACC_THR():
        return 2
    
    @constant
    def CLASS_RR_THR():
        return 200
    
    @constant
    def CLASS_FEAT_THR():
        return 1
    
    @constant
    def CLASS_PEAK_THR():
        return 3
    
    @constant
    def CLASS_COLS():
        return [CONST.ACCX, CONST.ACCY, CONST.ACCZ, CONST.RVP, CONST.RVR, CONST.RVY]
    
CONST = _Const() if not hasattr(_Const, '_instance') else _Const._instance