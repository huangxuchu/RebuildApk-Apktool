#!/usr/bin/python3
# 文件工具类工具类
import os
import re
import shutil


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def copy(from_path, to_path):
    return shutil.copy(from_path, to_path)


def rename(old_path, new_path):
    os.rename(old_path, new_path)


# 读取文件并替换复合规则的内容
def replace_content(file_path, regex, replace):
    file_data = ""
    with open(file_path, 'r') as f:
        for line in f:
            file_data += re.sub(regex, replace, line)
    with open(file_path, "w") as f:
        f.write(file_data)
    return file_data


def listdir(path):
    return os.listdir(path)


def exists(path):
    return os.path.exists(path)


def rmdir(path):
    try:
        os.rmdir(path)
    except BaseException:
        print(BaseException)


def remove(path):
    try:
        os.remove(path)
    except BaseException:
        print(BaseException)
