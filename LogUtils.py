import DateUtils


def i(tag, msg):
    print(DateUtils.date_time_full() + " Info/" + str(tag) + ": " + str(msg))


def w(tag, msg):
    print(DateUtils.date_time_full() + " Warn/" + str(tag) + ": " + str(msg))


def e(tag, msg):
    print(DateUtils.date_time_full() + " Error/" + str(tag) + ": " + str(msg))
