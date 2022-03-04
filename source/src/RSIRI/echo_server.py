from lxml import etree
from RSIRI.network import Network
from RSIRI.tools import \
    rsi_config_to_xml_string, \
    get_ipoc, \
    xml_string_to_dict, \
    merge_dict_with_xml_string, \
    extract_config_from_rsi_config
from time import sleep


# Logging setup
import logging
# Define the log format
log_format = '[%(asctime)s] %(levelname)-8s %(name)-12s %(funcName)20s() %(lineno)s %(message)s'
# Define basic configuration
logging.basicConfig(level=logging.DEBUG, format=log_format, handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


class RSIEchoServer:
    def __init__(self, config_file):
        # Network connection Object
        # TODO Get port from config
        self.network = Network("127.0.0.1", extract_config_from_rsi_config(config_file)[1])
        # RSI Variables
        self.send_values_xml = rsi_config_to_xml_string(config_file, "send")
        self.send_values = xml_string_to_dict(self.send_values_xml)
        self.receive_values_xml = rsi_config_to_xml_string(config_file, "receive")
        self.receive_values = xml_string_to_dict(self.receive_values_xml)
        self.state = False
        self.ipoc = 0

    def run(self):
        logger.debug("Echo server running")
        while self.state is True:
            logger.debug(self.send_values)
            self.send_message()
            sleep(0.03)
            try:
                self.get_response()
                logger.debug(self.receive_values)
                self.process_data()
            except(TimeoutError, ConnectionResetError):
                pass

    def send_message(self):
        """ Send RSI Message.

        Updates IPOC of message and sends the RSIValues Object .xml values
        """
        logger.debug("Send Reply")
        self.send_values_xml = merge_dict_with_xml_string(self.send_values, self.send_values_xml)
        self.update_ipoc()
        self.network.send(self.send_values_xml)

    def update_ipoc(self):
        """ Updates IPOC of send message. """
        xml_val = etree.fromstring(self.send_values_xml)
        xml_val[len(xml_val) - 1].text = str(int(self.ipoc) + 4)
        self.send_values_xml = etree.tostring(xml_val, encoding="unicode")

    def get_response(self):
        """ Get RSI data from robot and process.

        Polls network socket and then updates RSIValues.values
        Gets IPOC from message and updates self.ipoc
        """
        logger.debug("Get Robot Data")
        # Polls network, returns a string of XML
        self.receive_values_xml = self.network.receive()
        # Get IPOC
        self.ipoc = get_ipoc(self.receive_values_xml)
        # Convert XML string into Dict
        self.receive_values.update(xml_string_to_dict(self.receive_values_xml))

    def process_data(self):
        rec = self.receive_values["RKorr"]
        sen = self.send_values["RIst"]

        for key in rec:
            sen[key] = str(float(sen[key]) + float(rec[key]))

        self.send_values["RIst"] = sen


if __name__ == '__main__':
    pass
