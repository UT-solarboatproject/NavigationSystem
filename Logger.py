import csv
from datetime import datetime


class Logger:
    present = datetime.now()
    now = present.strftime("%Y-%m-%d-%H-%M-%S")
    filename = now + "_gpslog.csv"

    def open(self):

        self.f = open(Logger.filename, "a")
        self.writer = csv.writer(self.f, lineterminator="\n")
        log_list = [
            "TIME_STAMP",
            "MODE",
            "LATITUDE",
            "LONGITUDE",
            "HEADING",
            "SPEED",
            "T_INDEX",
            "T_LATITUDE",
            "T_LONGITUDE",
            "T_BEARING",
            "T_DISTANCE",
            "SERVO_PW",
            "THR_PW",
            "ERR_BACK",
            "CURRENT",
            "VOLTAGE",
            "POWER",
        ]
        self.writer.writerow(log_list)

    def write(self, log_list):
        self.writer.writerow(log_list)

    def close(self):
        self.f.write("END\n")
        self.f.close()


# test code
if __name__ == "__main__":
    logger = Logger()
    logger.open()
    logger.write([1, 1, 1])
    logger.close()
