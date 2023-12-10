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
        return 10
    
    @constant
    def SWING_AFTER_IMPACT():
        return 5
        
    @constant
    def SWING_PREPARE_END():
        return 6
    
    @constant
    def SWING_IMPACT_END():
        return 11
    
    @constant
    def SWING_INTERPRET_RES():
        return {'000': '백스윙 속도가 부족합니다.',
                '001': '백스윙 속도가 매우 부족합니다.',
                '010': '백스윙 궤적이 이상합니다.',
                '020': '백스윙 손목 방향이 잘못되었습니다.',
                '021': '백스윙 손목 방향이 매우 잘못되었습니다.',
                '030': '백스윙 깊이가 부족합니다.',
                '031': '백스윙 깊이가 매우 부족합니다.',
                '100': '임팩트 스윙 속도가 부족합니다.',
                '101': '임팩트 스윙 속도가 매우 부족합니다.',
                '110': '임팩트 스윙 손목 방향이 잘못되었습니다.',
                '120': '임팩트 스윙 손목 회전을 활용하지 않았습니다.',
                '130': '임팩트 스윙 손목 회전이 부자연스럽습니다.',
                '131': '임팩트 스윙 손목 회전이 매우 부자연스럽습니다.',
                '200': '임팩트 이후 자세가 부자연스럽습니다.',
                '201': '임팩트 이후 자세가 매우 부자연스럽습니다.',
                '210': '손목회전의 속도가 부족합니다.',
                '211': '손목회전의 속도가 매우 부족합니다.',
                '220': '팔로우 스윙 과정에서 손목이 꺾였습니다.',
                '221': '팔로우 스윙 과정에서 손목이 매우 꺾였습니다.',
                '500': '백스윙 속도가 적절합니다.',
                '510': '백스윙 궤적이 적절합니다.',
                '600': '임팩트 스윙 속도가 적절합니다.',
                '610': '임팩트 스윙 시 손목을 올바르게 회전하였습니다.',
                '700': '임팩트 이후 자세가 안정적입니다.',
                '710': '임팩트 이후 손목회전이 자연스럽습니다.',
                '720': '임팩트 이후 손목이 꺾이지 않았습니다.',
                }
    

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