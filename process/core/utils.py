from constant import CONST

def openStorageCSVFile(file_path):
    """
    CSV 파일을 여는 함수

    Parameters:
    file_path (list): 다수의 파일 위치 리스트

    Returns:
    DataFrame list : pandas.core.frame.DataFrame의 리스트
    """
    pass

def addFeature(all_data):
    for data in all_data:
        data['x+y+z'] = data[CONST.ACCX] + data[CONST.ACCY] + data[CONST.ACCZ]
        data['x+y'] = data[CONST.ACCX] + data[CONST.ACCY]
        data['y+z'] = data[CONST.ACCY] + data[CONST.ACCZ]
        data['x+z'] = data[CONST.ACCX] + data[CONST.ACCZ]

        data['x*y*z'] = data[CONST.ACCX] * data[CONST.ACCY] * data[CONST.ACCZ]
        data['x*y'] = data[CONST.ACCX] * data[CONST.ACCY]
        data['y*z'] = data[CONST.ACCY] * data[CONST.ACCZ]
        data['x*z'] = data[CONST.ACCX] * data[CONST.ACCZ]

        data['p+r+w'] = data[CONST.RVP] + data[CONST.RVR] + data[CONST.RVY]
        data['p+r'] = data[CONST.RVP] + data[CONST.RVR]
        data['r+w'] = data[CONST.RVR] + data[CONST.RVY]
        data['p+w'] = data[CONST.RVP] + data[CONST.RVY]

        data['p*r*w'] = data[CONST.RVP] * data[CONST.RVR] * data[CONST.RVY]
        data['p*r'] = data[CONST.RVP] * data[CONST.RVR]
        data['r*w'] = data[CONST.RVR] * data[CONST.RVY]
        data['p*w'] = data[CONST.RVP] * data[CONST.RVY]
        
        del data[CONST.PITCH]
        del data[CONST.ROLL]
        del data[CONST.YAW]

    return all_data