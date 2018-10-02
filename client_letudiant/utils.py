import datetime


def time_stamp():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%dT%H-%M-%S')
