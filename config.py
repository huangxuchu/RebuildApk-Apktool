import Constants

HOST = '192.168.31.34'
PORT = 8883
DEBUG = False


# 配置对象，里面定义需要给 APP 添加的一系列配置
class FlaskConfig:
    DEBUG = DEBUG
    SERVER_NAME = f'{HOST}:{PORT}'
    UPLOAD_FOLDER = Constants.PATH_MATERIAL
