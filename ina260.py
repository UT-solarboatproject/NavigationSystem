# -*- coding: utf-8 -*-
import csv
from datetime import datetime
import signal
import time
import board
import adafruit_ina260

REC_START_HOUR = 8
REC_END_HOUR = 18


def task(arg1, arg2):

    # 電流・電圧・電力の取得
    cur = ina260.current
    vol = ina260.voltage
    po  = ina260.power
    
    # 日時の取得
    _now = datetime.now()
    today = _now.strftime("%Y-%m-%d")
    nowtime = _now.strftime("%H:%M:%S")
    file_end = _now.strftime("%Y%m%d")
    
    print ('日付 %s 時刻 %s 電流 %.2f mA 電圧 %.2f V 電力 %.2f mW' % (today,nowtime,cur,vol,po))
    with open("ina260_log_1.csv", "a") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([today,nowtime,cur,vol,po])

i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c,0x40)

signal.signal(signal.SIGALRM, task)
signal.setitimer(signal.ITIMER_REAL, 0.1, 0.1) # コマンドラインでCtrl+Cで止められるように

while True:
    time.sleep(1)