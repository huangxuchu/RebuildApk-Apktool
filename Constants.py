import os

# 线程数量（Mac-i5电脑，测试50个包，4条线程耗时400秒，8条线程耗时380秒）
THREAD_COUNT = 4

# excel表格的key
KEY_INFO_LIST = 'info_list'
KEY_INFO_APP_NAME = 'app_name'
KEY_INFO_APP_ICON_URL = 'app_icon_url'
KEY_INFO_CHANNEL = 'channel'
KEY_INFO_CHANNEL_PREFIXES = 'channel_prefixes'
KEY_PARAMS = 'params'
KEY_PARAMS_KEYSTORE = 'keystore'
KEY_PARAMS_OUTPUT = 'output'

# apktool工具存放地址
PATH_APKTOOL_JAR = os.path.join(os.getcwd(), 'apktool', 'apktool.jar')
# apksigner工具地址
PATH_APKSIGNER = os.path.join(os.getcwd(), 'build-tools', '30.0.3', 'apksigner')

# 文件夹路径
PATH_MATERIAL = os.path.join(os.getcwd(), 'material')
PATH_MATERIAL_ICON = os.path.join(PATH_MATERIAL, 'icon')
PATH_OUTPUT = os.path.join(os.getcwd(), 'output')
PATH_TEMP = os.path.join(os.getcwd(), 'temp')
PATH_KEYSTORE = os.path.join(os.getcwd(), 'keystore')
