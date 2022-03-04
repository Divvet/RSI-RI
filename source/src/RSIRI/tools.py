from lxml import etree


def rsi_config_to_dict(rsi_file, direction):
    return xml_string_to_dict(rsi_config_to_xml_string(rsi_file, direction))


def xml_string_to_dict(xml):
    """ Convert RSI XML string to dict variables.

    Converts an RSI XML string to RSIValue Object values.
    Either takes an XML String or reads from Object.xml value

    Keyword arguments:
        xml - RSI XML String (default None)
    """
    # Convert string to XML object
    xml_string = etree.fromstring(xml)
    new_values = {}
    # Cycle through XML object converting each attribute/value
    # to dict and storing in the shared value variable
    for xml_row in xml_string:
        if xml_row.text is None:
            new_values[xml_row.tag] = {}
            for a, v in xml_row.items():
                # new_values[xml_row.tag].insert(a, str(v))
                new_values[xml_row.tag][a] = str(v)
        else:
            new_values[xml_row.tag] = xml_row.text
    # logging.debug(new_values)
    return new_values


def get_ipoc(message):
    x = etree.fromstring(message)
    ipoc = x[len(x) - 1].text
    return ipoc


def update_ipoc(xml_string, ipoc):
    """ Updates IPOC of send message. """
    xml_val = etree.fromstring(xml_string)
    xml_val[len(xml_val) - 1].text = str(ipoc)
    send_string = etree.tostring(xml_val, encoding="unicode")
    return send_string


def merge_dict_with_xml_string(dict_value, xml_string):
    """ Convert to Object variables to RSI XML string. """
    xml = etree.fromstring(xml_string)
    for xml_row in xml:
        if xml_row.text is None:
            for a, v in xml_row.items():
                xml.find(xml_row.tag).attrib[a] = dict_value[xml_row.tag][a]
        else:
            xml_row.text = dict_value[xml_row.tag]

    xml_string = etree.tostring(xml).decode()
    return xml_string


def load_xml(file):
    """ Load Send XML template and returns XML root to object """
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(file, parser=parser)
    return tree.getroot()


def rsi_config_to_xml_string(file, direction):
    """Opens the KUKA RobotSensorInterface XML config file and creates the XML template
    for sending and receiving messages"""

    xml_root = load_xml(file)
    root_name = None
    rsi_type = None
    index = None

    # Set XML structure based off being a send or receive value
    for i, c in enumerate(xml_root):
        if c.tag == "SEND" and direction == "send":
            index = i
            rsi_type = "KUKA"
            root_name = "Rob"
        if c.tag == "RECEIVE" and direction == "receive":
            index = i
            for item in xml_root[0]:
                if item.tag == "SENTYPE":
                    rsi_type = item.text
            root_name = "Sen"

    send_root = etree.Element(root_name, Type=rsi_type)

    # Add Elements
    # TODO Flesh out internal and non internal variables
    internal = {"ComStatus": "String",
                "RIst": ["X", "Y", "Z", "A", "B", "C"],
                "RSol": ["X", "Y", "Z", "A", "B", "C"],
                "AIPos": ["A1", "A2", "A3", "A4", "A5", "A6"],
                "ASPos": ["A1", "A2", "A3", "A4", "A5", "A6"],
                "ELPos": ["X", "Y", "Z", "A", "B", "C"],
                "ESPos": ["X", "Y", "Z", "A", "B", "C"],
                "MaCur": ["X", "Y", "Z", "A", "B", "C"],
                "MECur": ["X", "Y", "Z", "A", "B", "C"],
                "IPOC": 000000,
                "BMode": "Status",
                "IPOSTAT": "",
                "Delay": ["D"],
                "EStr": "EStr Test",
                "Tech.C1": ["C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C110"],
                "Tech.T2": ["T21", "T22", "T23", "T24", "T25", "T26", "T27", "T28", "T29", "T210"],
                }
    kuka_variables = {"DiL": "0",
                      "Source1": "Empty test value",
                      "DiO": "125",
                      }
    custom = {}
    count = 0
    # For each item in xml_root
    for i, item in enumerate(xml_root[index][0]):
        tag = item.values()[0]
        indx = item.values()[2]
        if indx == "INTERNAL":
            # logger.debug("Tag: {}".format(tag))
            if tag.startswith("DEF_"):
                tag = tag[4:]

                # logger.debug("Tag: {}".format(tag))
                values = internal[tag]
                if tag.__contains__("."):
                    # print(tag)
                    # tag = tag[:tag.find(".")]
                    pass
                send_root.append(etree.Element(str(tag)))
                if isinstance(values, list):
                    for a in values:
                        send_root[i].set(a, "0")
                else:
                    send_root[i].text = values
        elif tag.__contains__("."):
            value = tag[tag.find(".") + 1:]
            tag = tag[:tag.find(".")]
            if custom.__contains__(tag):
                values = custom[tag]
                values.append(value)
                custom[tag] = values
                send_root[count].set(value, "0")
            else:
                custom[tag] = [value]
                send_root.append(etree.Element(str(tag)))
                send_root[i].set(value, "0")
                count = i
        else:
            if tag.startswith("FREE"):
                pass
            else:
                if kuka_variables.__contains__(tag):
                    values = kuka_variables[tag]
                    send_root.append(etree.Element(str(tag)))
                    count = len(send_root)
                    if isinstance(values, list):
                        for a in values:
                            send_root[count - 1].set(a, "0")
                    else:
                        send_root[count - 1].text = values
                        count = i
    send_root.append(etree.Element("IPOC"))
    send_root[len(send_root) - 1].text = str("0")

    # logger.debug(etree.tostring(send_root, pretty_print=True, encoding='unicode'))
    return etree.tostring(send_root, pretty_print=True, encoding='unicode')


def extract_config_from_rsi_config(file):
    xml_root = load_xml(file)
    ip, port, sen_type, only_send = None, None, None, None

    for item in xml_root[0]:
        if item.tag == "IP_NUMBER":
            ip = item.text
        if item.tag == "PORT":
            port = item.text
        if item.tag == "SENTYPE":
            sen_type = item.text
        if item.tag == "ONLYSEND":
            if item.text == "FALSE":
                only_send = False
            else:
                only_send = True

    return str(ip), int(port), str(sen_type), only_send


def extract_hold_values_from_config(file):
    xml_root = load_xml(file)
    hold = {}
    send_index = 0

    for index, value in enumerate(xml_root):
        if value.tag == "RECEIVE":
            send_index = index

    for index, item in enumerate(xml_root[send_index][0]):
        try:
            hold[item.values()[0]] = bool(int(item.values()[3]))
        except IndexError:
            pass
    return hold


if __name__ == '__main__':
    pass
