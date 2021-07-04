"""
注意：
1.加固的apk在没有脱壳的情况下，更换别的签名会崩溃，所以加固的apk必须使用原apk包里的签名
"""
import os
import shutil
import stat
import threading

import threadpool

import Constants
import ConfigExcelHandler
import DateUtils
import LogUtils
import RebuildApk

import SignApk

TAG = "main"


def check_permission():
    msg = r' 没有权限，将尝试获取读写执行权限'
    for item in [Constants.PATH_KEYSTORE,
                 Constants.PATH_TEMP,
                 Constants.PATH_MATERIAL,
                 Constants.PATH_OUTPUT,
                 Constants.PATH_APKSIGNER,
                 Constants.PATH_APKTOOL_JAR]:
        if not os.access(item, os.R_OK | os.W_OK | os.X_OK):
            LogUtils.w(TAG, item + msg)
            os.chmod(item, stat.S_IRWXU)


def check_and_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def clear_temp():
    if os.path.exists(Constants.PATH_TEMP):
        print('清空临时文件')
        shutil.rmtree(Constants.PATH_TEMP)


def clear_material():
    if os.path.exists(Constants.PATH_MATERIAL):
        print('清空素材文件')
        shutil.rmtree(Constants.PATH_MATERIAL)


def clear_output():
    if os.path.exists(Constants.PATH_OUTPUT):
        print('清空输出文件')
        shutil.rmtree(Constants.PATH_OUTPUT)


def packing(pack_apk, apk_config):
    pack_apk.packing(apk_config)


# 打包马甲apk
def packing_apk(task_id, selected_keystore, info_list, apk_decode_path, output_path):
    all_config_item = []
    for item in info_list:
        channel_prefixes = item[Constants.KEY_INFO_CHANNEL_PREFIXES]
        channels = item[Constants.KEY_INFO_CHANNEL]
        app_name = item[Constants.KEY_INFO_APP_NAME]
        app_icon_url = item[Constants.KEY_INFO_APP_ICON_URL]
        for channel in channels:
            all_config_item.append({Constants.KEY_INFO_APP_NAME: app_name,
                                    Constants.KEY_INFO_APP_ICON_URL: app_icon_url,
                                    Constants.KEY_INFO_CHANNEL_PREFIXES: channel_prefixes,
                                    Constants.KEY_INFO_CHANNEL: channel})
    # 根据线程或打包的数量创建打包任务和复制被打包的文件夹
    count = Constants.THREAD_COUNT
    if len(all_config_item) < Constants.THREAD_COUNT:
        count = len(all_config_item)
    pack_job_list = []
    for num in range(0, count):
        # 复制文件夹
        shutil.copytree(apk_decode_path, apk_decode_path + str(num))
        # 创建打包任务
        pack_job_list.append(PackJob(task_id,
                                     selected_keystore,
                                     apk_decode_path + str(num % count),
                                     output_path))
    params_list = []
    for i in range(0, len(all_config_item)):
        ptl = pack_job_list[(i % count)]
        params_list.append((None, {'pack_apk': ptl, 'apk_config': all_config_item[i]}))
    pool = threadpool.ThreadPool(count)
    requests = threadpool.makeRequests(packing, params_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    # 删除临时文件
    for i in range(0, count):
        shutil.rmtree(apk_decode_path + str(i))


# 为apk签名
def signing_apk_batch(task_id, input_path, output_path, selected_keystore):
    if selected_keystore is not None and len(selected_keystore) > 0:
        SignApk.sign_batch(selected_keystore,
                           task_id,
                           input_path,
                           output_path)
    else:
        LogUtils.e(TAG, '未配置Apk对应的签名，或Apk未签名')


class Main:
    def start(self, date_time):
        """
        线程执行Main.start_task
        :param date_time: 开始时间
        """
        check_permission()
        t = threading.Thread(target=Main().starting_task, args=(date_time,))
        t.start()

    def starting_task(self, task_id):
        if task_id is None or len(task_id) == 0:
            task_id = DateUtils.date_time()
        start_time = DateUtils.current_time_millis()
        print('开始任务 task=' + task_id + ' start_time=' + str(start_time))
        material_path = os.path.join(Constants.PATH_MATERIAL, task_id)
        apk_name = None
        apk_decode_path = None
        selected_keystore = None
        output_path = None
        info_list = []
        # 解析配置excel文件和反编译apk
        for file_name in os.listdir(material_path):
            if ('.xlsx' in file_name or '.xls' in file_name) and 'config' in file_name:
                config_dict = ConfigExcelHandler.parse(os.path.join(material_path, file_name))
                for k, v in config_dict.items():
                    if k == Constants.KEY_INFO_LIST:
                        info_list = v
                        ConfigExcelHandler.init_apk_json(info_list)
                    if k == Constants.KEY_PARAMS:
                        if Constants.KEY_PARAMS_KEYSTORE in v:
                            selected_keystore = v[Constants.KEY_PARAMS_KEYSTORE]
                        if Constants.KEY_PARAMS_OUTPUT in v:
                            output_path = v[Constants.KEY_PARAMS_OUTPUT]
            if '.apk' in file_name:
                apk_name = file_name
                apk_decode_path = os.path.join(Constants.PATH_TEMP, task_id, file_name.replace('.', ''))
                RebuildApk.decode_apk(os.path.join(material_path, file_name), apk_decode_path)
        # 检查输出路径是否有效
        if output_path is None or len(output_path) == 0 or not os.path.isdir(output_path):
            LogUtils.w(TAG, '没有配置输出路径，或者输出路径错误。将使用默认的输出路径：' + Constants.PATH_OUTPUT)
            output_path = Constants.PATH_OUTPUT
        # 检查是否有可用的签名
        if selected_keystore is None or len(selected_keystore) == 0:
            selected_keystore = SignApk.select_keystore(os.path.join(material_path, apk_name))
        # 打包马甲apk
        packing_apk(task_id, selected_keystore, info_list, apk_decode_path, output_path)
        print('结束任务 task=' + task_id + ' elapsed_time=' + str(DateUtils.current_time_millis() - start_time))


class PackJob:
    def __init__(self, task_id, selected_keystore, apk_decode_path, output_path):
        self.task_id = task_id
        self.selected_keystore = selected_keystore
        self.apk_decode_path = apk_decode_path
        self.output_path = output_path
        self.lock = threading.RLock()

    def packing(self, apk_config_item):
        # 加锁
        self.lock.acquire()
        try:
            # 开始打包
            LogUtils.i(TAG,
                       threading.current_thread().name + " 开始打包:" + str(
                           apk_config_item) + " " + self.apk_decode_path)
            # 打包apk
            RebuildApk.change_and_pack_apk(self.task_id,
                                           apk_config_item,
                                           self.apk_decode_path,
                                           self.output_path)
            new_app_name = apk_config_item[Constants.KEY_INFO_APP_NAME].strip()
            new_channel = apk_config_item[Constants.KEY_INFO_CHANNEL]
            output_name = new_app_name + '.apk'
            if new_channel is not None and len(new_channel) > 0:
                output_name = str(new_channel) + '_' + output_name
            # 为apk签名
            SignApk.sign(self.selected_keystore,
                         self.task_id,
                         os.path.join(self.output_path, self.task_id, output_name),
                         self.output_path)
            # 结束打包
            LogUtils.i(TAG,
                       threading.current_thread().name + " 结束打包: " + str(
                           apk_config_item) + " " + self.apk_decode_path)

        finally:
            # 修改完成，释放锁
            self.lock.release()


if __name__ == "__main__":
    check_and_mkdir(Constants.PATH_MATERIAL)
    check_and_mkdir(Constants.PATH_TEMP)
    check_and_mkdir(Constants.PATH_OUTPUT)
    # 测试样例
    Main().starting_task("123456")
    print('测试样例：./material/123456/')
