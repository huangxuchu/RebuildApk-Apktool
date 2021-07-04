import datetime
import time


def date_time():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def date_time_full():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def current_time_millis():
    return int(time.time() * 1000)


if __name__ == '__main__':
    print(current_time_millis())
