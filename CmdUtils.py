import os


# 执行控制台命令，并返回日志（注意：日志过多的问题）
def popen(command):
    r = os.popen(command)  # 执行该命令
    info = r.readlines()  # 读取命令行的输出到一个list
    r.close()
    return info
