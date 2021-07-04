"""
为apk包签名。
需求：
1、批量签名apk
2、多个签名文件可选
逻辑：
1、网页上传apk文件到本地的temp文件夹下，并生成时间戳的文件夹。没有temp文件夹时需要自动生成。
2、签名程序获取本地temp目录下的时间错文件夹的目录下的所有apk
"""
import json
import os

import CmdUtils
import Constants
import DateUtils
import FileUtils
import LogUtils
import main

TAG = 'SignApk'

# 签名命令 参数：1=签名.jks或.keystore文件路径, 2=签名文件密码, 3=别名, 4=别名密码, 5=apk文件路径
APKSIGNER_ORDER_SIGN = """ sign --ks %s --ks-pass pass:%s --ks-key-alias %s --key-pass pass:%s %s"""
# 获取apk包签名md5 参数：1=apk文件路径
KEYTOOL_ORDER_APK_SIGN_INFO = """keytool -printcert -jarfile %s"""
# 获取keystore的md5 参数：1=keystore文件路径, 2=keystore的密码
KEYTOOL_ORDER_KEYSTORE_INFO = """keytool -list -v -keystore %s -storepass %s"""

# 签名信息
_keystore_json = {}
#
_keystore_keys = {}
# 正在执行的任务
signing_task = []


# selected_keystore: apk的签名文件
# task_id: 任务id
# input_path: 批量签名存放任务的目录
# output: 签名后的输出目录
def sign_batch(selected_keystore, task_id, input_path, output_path):
    if task_id is None or len(task_id) == 0:
        task_id = DateUtils.date_time()
    print('签名 task=' + task_id)
    print('Using Apksigner ' + (CmdUtils.popen(Constants.PATH_APKSIGNER + ' --version')[0]).strip())
    if task_id in signing_task:
        return
    signing_task.append(task_id)
    taskPath = os.path.join(input_path)
    apkList = os.listdir(taskPath)
    apkList.sort()
    for apk in apkList:
        if not apk.endswith(".apk"):
            continue
        apkPath = os.path.join(taskPath, apk)
        code = _sign(selected_keystore, apkPath)
        if code == 0:
            apk_sign = apk.replace(".apk", "_sign.apk")
            os.renames(apkPath, os.path.join(output_path, task_id, apk_sign))
            os.remove(apkPath + r'.idsig')
    signing_task.remove(task_id)
    baseName = os.path.basename(input_path)
    if baseName != 'output' and input_path != output_path:
        FileUtils.rmdir(input_path)


def sign(selected_keystore, task_id, apk_path, output_path):
    """
    签名方法，签名后apk名称变为 xxx.apk->xxx_sign.apk
    :param selected_keystore: apk的签名文件
    :param task_id: 任务id
    :param apk_path: apk的目录
    :param output_path: 签名后的输出目录
    :return:
    """
    if task_id is None or len(task_id) == 0:
        task_id = DateUtils.date_time()
    print('开始签名 task=' + task_id)
    print('Using Apksigner ' + (CmdUtils.popen(Constants.PATH_APKSIGNER + ' --version')[0]).strip())
    if not apk_path.endswith(".apk"):
        return
    code = _sign(selected_keystore, apk_path)
    if code == 0:
        apk_sign = os.path.basename(apk_path).replace(".apk", "_sign.apk")
        os.renames(apk_path, os.path.join(output_path, task_id, apk_sign))
        os.remove(apk_path + r'.idsig')
    else:
        LogUtils.e(TAG, f'签名失败 code={code}')


def select_keystore(apk):
    dc = get_apk_signed_dc(apk)
    return _get_keystore_json_key(dc)


def get_apk_signed_dc(apk):
    command = KEYTOOL_ORDER_APK_SIGN_INFO % apk
    info = CmdUtils.popen(command)
    return _parse_dc(info)


def get_keystore_dc(keystore, password):
    command = KEYTOOL_ORDER_KEYSTORE_INFO % (keystore, password)
    info = CmdUtils.popen(command)
    return _parse_dc(info)


def _sign(key, apk_path):
    _init_keystore()
    if key not in _keystore_json:
        LogUtils.e(TAG, '未获取到签名数据，请检查"keystore"文件夹下相应的签名文件是否存在，以及确认签名配置"keystore.json"是否正确')
        return -1
    keystore_info = _keystore_json[key]
    print("签名数据: " + keystore_info['name'] + " Apk路径: " + apk_path)
    task = Constants.PATH_APKSIGNER + APKSIGNER_ORDER_SIGN % (
        os.path.join(Constants.PATH_KEYSTORE, keystore_info['name']),
        keystore_info['password'],
        keystore_info['alias'],
        keystore_info['alias_password'],
        apk_path)
    code = os.system(task)
    return code


def _init_keystore():
    global _keystore_json
    if len(_keystore_json) == 0:
        _keystore_json = json.loads(FileUtils.read_file('keystore/keystore.json'))


def _parse_dc(info):
    key = "证书指纹:"
    start = False
    DC = []
    for line in info:
        line = line.strip()
        if start:
            if line.startswith("MD5:"):
                DC.append(line)
            elif line.startswith("SHA1:"):
                DC.append(line)
            elif line.startswith("SHA256:"):
                DC.append(line)
                break
        if not start:
            start = line.startswith(key)
    return DC


def _get_keystore_json_key(DC):
    query = str(DC)
    if len(query) == 0:
        return ''
    if len(_keystore_keys) == 0:
        _init_keystore()
        for key, values in dict.items(_keystore_json):
            d = get_keystore_dc(os.path.join(Constants.PATH_KEYSTORE, values['name']), values['password'])
            k = str(d)
            v = key
            _keystore_keys[k] = v
    if query in _keystore_keys:
        return _keystore_keys[query]
    else:
        return ''


if __name__ == "__main__":
    print("启动SignApk")
    main.check_permission()
