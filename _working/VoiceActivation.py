from RSI-RI import RSIClient

if __name__ == '__main__':

    config_file = "../../../resources/Example Files/ConfigFiles/rsi examples/RSI_EthernetConfig.xml"
    # Create RSI Client
    client = RSIClient(config_file)

    # Start Server
    client.start()

    while True:
        file1 = open("MyFile.txt", "r")

        file1.close()