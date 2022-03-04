from time import sleep
from RSIRI.server import RSIServer
from RSIRI.tools import \
    rsi_config_to_dict, \
    extract_config_from_rsi_config
from multiprocessing import Process, Manager

# Log file location
import logging
# Define the log format
log_format = '[%(asctime)s] %(levelname)-8s %(name)-12s %(funcName)20s() %(lineno)s %(message)s'
# Define basic configuration
logging.basicConfig(level=logging.DEBUG, format=log_format, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def rsi_process(file, send, receive, status):
    """Process containing the RSI networking functions

    This process operates the networking side of the RSI RI Functions.
    :param file: RSI config file
    :param ip: IP of local system
    :param port: Port used in RSI config file.
    :param send: Variable containing Manager.Dict variable with RSI values
    :param receive: Variable containing Manager.Dict variable with RSI values
    :param status: Variable containing Manager.Dict variable with RSI status values
    :return:
    """
    rsi_server = RSIServer(file, receive, send, status)
    rsi_server.state = True
    rsi_server.run()


def check_position_values(values, send_values, rec_values, rate):
    """Checks

    :param values:
    :param send_values:
    :param rec_values:
    :param rate:
    :return:
    """
    for key, val in values.items():
        if float(rec_values[key]) > val:
            send_values[key] = str(rate)
        if float(rec_values[key]) < val:
            send_values[key] = str(rate * -1)
        if float(rec_values[key]) == val:
            send_values[key] = 0
    return send_values


class RSIClient:
    """ RSI Client Object """
    def __init__(self, file):
        """RSI Client Object

        Object used to provide interface to RSI Variables.
        :param file: RSI Config File
        :param ip: Local IP address
        :param port: Port used in RSI Config file
        """
        self.file = file
        self.ip, self.port, self.sen_type, self.only_send = extract_config_from_rsi_config(file)
        self.state = False
        self.manager = Manager()
        self.send = self.manager.dict(rsi_config_to_dict(file, "receive"))
        self.receive = self.manager.dict(rsi_config_to_dict(file, "send"))
        self.status = self.manager.dict({"State": False})
        self.movement_type = None
        self.rsi = Process(target=rsi_process, args=(self.file,
                                                     self.receive,
                                                     self.send,
                                                     self.status))

    def print_send_receive_variables(self):
        """

        :return:
        """
        print("Values Received")
        for key, value in self.receive.items():
            print(key, ' : ', value)

        print("Values Sent")
        for key, value in self.send.items():
            print(key, ' : ', value)

    def start(self):
        """Start RSI Network process

        :return:
        """
        self.rsi.start()
        self.status["State"] = True
        # self.rsi.join()

    def stop(self):
        """

        :return:
        """
        self.status["State"] = False
        sleep(1)
        self.rsi.terminate()
        sleep(1)
        self.rsi.kill()
        sleep(1)
        self.rsi = Process(target=rsi_process, args=(self.file,
                                                     self.ip,
                                                     self.port,
                                                     self.receive,
                                                     self.send,
                                                     self.status))

    def set_attribute(self, key, axis, value):
        """Sets the value of a multi value variable.

        :param key:
        :param axis:
        :param value:
        :return:
        """
        try:
            send_value = self.send
            values = send_value[key]
            values[axis] = str(value)
            send_value[key] = values
            self.send = send_value
            return "OK"
        except ValueError:
            return "{} not present in config file".format(key)

    def set_rkorr(self, axis, value):
        """

        :param axis:
        :param value:
        :return:
        """
        self.set_attribute("RKorr", axis, value)

    def set_akorr(self, joint, value):
        """

        :param joint:
        :param value:
        :return:
        """
        self.set_attribute("AKorr", joint, value)

    def set_string(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        try:
            self.send[key] = value
        except ValueError:
            return "{} not present in config file".format(key)

    def load_send_values(self, key):
        """

        :param key:
        :return:
        """
        return self.send[key]

    def load_receive_values(self, key):
        """

        :param key:
        :return:
        """
        return self.receive[key]

    def move_basic_ptp(self, coord, rate):
        """

        :param coord:
        :param rate:
        :return:
        """
        values = {"X": coord[0], "Y": coord[1], "Z": coord[2], "A": coord[3], "B": coord[4], "C": coord[5]}
        send_values = self.load_send_values("RKorr")
        rec_values = self.load_receive_values("RIst")

        self.send["RKorr"] = check_position_values(values, send_values, rec_values, rate)

    def move_joints(self, a1, a2, a3, a4, a5, a6, rate):
        """

        :param a1:
        :param a2:
        :param a3:
        :param a4:
        :param a5:
        :param a6:
        :param rate:
        :return:
        """
        values = {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5, "A6": a6}
        send_values = self.load_send_values("RKorr")
        rec_values = self.load_receive_values("RIst")

        self.send["AKorr"] = check_position_values(values, send_values, rec_values, rate)


if __name__ == '__main__':
    pass
