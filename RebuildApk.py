#!/usr/bin/python3
# 重新打包apk工具。
# 将apk反编译，然后替换对应的资源文件及文案。并重新打包未签名的apk
# 1、替换图片
# 2、修改xml的内容
import os
import sys
from multiprocessing import Process

import ConfigExcelHandler
import Constants
import FileUtils
# apktool程序执行命令
import LogUtils

TAG = "RebuildApk"
MSG = """RebuildApk工具
\t-b\t可用于反编译apk包
\t-c\t替换反编译后的apk内容
\t-p\t把反编译文件重新打包成apk
"""

# 反编译工具命令
APKTOOL_JAR = "java -jar " + Constants.PATH_APKTOOL_JAR
# 反编译命令 参数：1=apk文件路径，2=反编译文件输出路径
APKTOOL_ORDER_D = " d -s %s -o %s"
# 打包命令 参数：1=反编译文件输出路径，2=新apk文件路径
APKTOOL_ORDER_B = " b %s -o %s"

# apk的string.xml路径
APK_PATH_VALUES = os.path.join("res", "values")
# 字符串资源文件
APK_PATH_VALUES_STRINGS_XML = os.path.join(APK_PATH_VALUES, "strings.xml")
# apk的drawable-xxhdpi路径
APK_PATH_DRAWABLE_XXHDPI = os.path.join("res", "drawable-xxhdpi")
# apk的mipmap-xxhdpi路径
APK_PATH_MIPMAP_XXHDPI = os.path.join("res", "mipmap-xxhdpi")
# AndroidManifest.xml文件名
ANDROID_MANIFEST_XML = "AndroidManifest.xml"
# 图标名称 后缀可能是.png/.jpg
IC_LAUNCHER = "ic_launcher"

# apk的名称匹配正则表达式
PATTERN_STRING_APP_NAME = """<string name="app_name">.*</string>"""
# app的渠道名称
PATTERN_MANIFEST_CHANNEL = """<meta-data android:name="DC_CHANNEL" android:value=".*"/>"""


# 解密apk文件 -d
def decode_apk(apk_path, out_path):
    print("解压 apk=" + apk_path + " out_path=" + out_path)
    apktool_decode = APKTOOL_JAR + APKTOOL_ORDER_D % (apk_path, out_path)
    os.system(apktool_decode)


# 重新打包 -p
def repack_apk(apk_folder_path, out_path):
    print("打包 apk_folder_path=" + apk_folder_path + " out_path=" + out_path)
    apktool_rebuild = APKTOOL_JAR + APKTOOL_ORDER_B % (apk_folder_path, out_path)
    os.system(apktool_rebuild)


# 替换素材 -c
def change_material(apk_config_item, apk_decode_path):
    print("替换apk内容: " + str(apk_config_item) + " path=" + apk_decode_path)
    # 替换app名称
    new_app_name = apk_config_item[Constants.KEY_INFO_APP_NAME].strip()
    if new_app_name is None or len(new_app_name) == 0:
        LogUtils.e(TAG, "没有设置app的名称")
        return False
    FileUtils.replace_content(os.path.join(apk_decode_path, APK_PATH_VALUES_STRINGS_XML),
                              PATTERN_STRING_APP_NAME,
                              PATTERN_STRING_APP_NAME.replace(r".*", new_app_name))
    # 替换channel
    new_channel = apk_config_item[Constants.KEY_INFO_CHANNEL]
    if new_channel is not None and len(new_channel) > 0:
        FileUtils.replace_content(os.path.join(apk_decode_path, ANDROID_MANIFEST_XML),
                                  PATTERN_MANIFEST_CHANNEL,
                                  PATTERN_MANIFEST_CHANNEL.replace(r".*", new_channel))
    # 替换app图标
    new_app_icon_path = os.path.join(Constants.PATH_MATERIAL_ICON,
                                     ConfigExcelHandler.parse_image_name(
                                         apk_config_item[Constants.KEY_INFO_APP_ICON_URL]))
    if new_app_icon_path is not None and os.path.isfile(new_app_icon_path):
        local_app_icon_path = ''
        local_image_folder = os.path.join(apk_decode_path, APK_PATH_MIPMAP_XXHDPI)
        local_app_icon_name = _find_ic_launcher(local_image_folder)
        if local_app_icon_name != '':
            local_app_icon_path = os.path.join(local_image_folder, local_app_icon_name)
        else:
            local_image_folder = os.path.join(apk_decode_path, APK_PATH_DRAWABLE_XXHDPI)
            local_app_icon_name = _find_ic_launcher(local_image_folder)
            if local_app_icon_name != '':
                local_app_icon_path = os.path.join(local_image_folder, local_app_icon_name)
        if local_app_icon_path == '':
            LogUtils.e(TAG, "没有找到替换的图标名称，请联系攻城狮大哥")
        else:
            # 修改原来的图标做备份，以防替换失败
            temp_path = os.path.join(local_app_icon_path + '.temp')
            FileUtils.rename(local_app_icon_path, temp_path)
            try:
                new_ic_launcher = os.path.join(local_image_folder,
                                               IC_LAUNCHER + '.' + str.rpartition(new_app_icon_path, '.')[2])
                FileUtils.copy(new_app_icon_path, new_ic_launcher)
                FileUtils.remove(temp_path)
            except BaseException:
                LogUtils.e(TAG, "替换图标异常")
                FileUtils.rename(temp_path, local_app_icon_path)
    return True


# 替换素材并重新打包
def change_and_pack_apk(task_id, apk_config_item, apk_decode_path, output_path):
    # 替换app内容
    if not change_material(apk_config_item, apk_decode_path):
        LogUtils.e(TAG, "替换马甲包素材失败")
        return
    # 重新打包apk包
    new_app_name = apk_config_item[Constants.KEY_INFO_APP_NAME].strip()
    new_channel = apk_config_item[Constants.KEY_INFO_CHANNEL]
    output_name = new_app_name + '.apk'
    if new_channel is not None and len(new_channel) > 0:
        output_name = str(new_channel) + '_' + output_name
    multiple_repack_apk(apk_decode_path, os.path.join(output_path, task_id, output_name))


# 多进程打包apk
def multiple_repack_apk(apk_folder_path, out_path):
    p = Process(target=repack_apk, args=(apk_folder_path, out_path))
    p.start()
    p.join()


def _find_ic_launcher(path):
    for item in os.listdir(path):
        if item.split('.')[0] == IC_LAUNCHER:
            return item
    return ''


def order_decode_apk():
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]
    if os.path.isfile(arg2) and len(arg3) > 0:
        decode_apk(arg2, arg3)
    else:
        print("参数错误")


def order_repack_apk():
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]
    if os.path.isdir(arg2) and len(arg3) > 0:
        repack_apk(arg2, arg3)
    else:
        print("参数错误")


if __name__ == "__main__":
    print('执行RebuildApk:' + str(sys.argv))
    if len(sys.argv) <= 1:
        print(MSG)
        exit()
    order = sys.argv[1]
    if order == '-p':
        order_repack_apk()
    elif order == '-b':
        order_decode_apk()
    else:
        print(MSG)
        exit()
