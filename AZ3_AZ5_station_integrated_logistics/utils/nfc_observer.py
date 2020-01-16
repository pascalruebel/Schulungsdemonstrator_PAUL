
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.util import toHexString
from smartcard import Exceptions
from utils import error_codes
from communication import events

class PosReaderObserver(ReaderObserver):
    """ NFC-reader observer that is notified
        when readers are added/removed from the system
    """
    def __init__(self, station_app):
        self._station_app = station_app
        self.addedreaders = list()
        self.removedreaders = list()
        self.activereaders = list()

    def update(self, observable, actions):
        (self.addedreaders, self.removedreaders) = actions

        for reader in self.addedreaders:
            connection = reader.createConnection()
            reader_name = connection.getReader()
            reader_number = int(reader_name.split(" ")[4])
            self.activereaders.append(reader_number)
            self._station_app.logger.info("The reader is connected to the position  %s ", reader_number)

            if reader_number == 0:
                self._station_app.nfc_pos1_ok()
            elif reader_number == 1:
                self._station_app.nfc_pos2_ok()
            elif reader_number == 2:
                self._station_app.nfc_pos3_ok()

        for reader in self.removedreaders:
            connection = reader.createConnection()
            reader_name = connection.getReader()
            reader_number = int(reader_name.split(" ")[4])
            self._station_app.logger.info("The reader at the position %s was disconnected", reader_number)
            self.activereaders.remove(reader_number)

            if reader_number == 0:
                self._station_app.nfc_pos1_nok()
            elif reader_number == 1:
                self._station_app.nfc_pos2_nok()
            elif reader_number == 2:
                self._station_app.nfc_pos3_nok()

        self._station_app.logger.info("List of the actve rfid readers: %s", self.activereaders)

    def check_reader(self, reader_number, cb_true, cb_false):

        self._station_app.logger.info("List of the actve rfid readers: %s", self.activereaders)

        if (reader_number - 1) in self.activereaders:
            cb_true()
        else:
            cb_false()

        # reader_numbers = list()
        # print("Check reader, added readers:", self.addedreaders)
        # if self.addedreaders:
        #     for reader in self.addedreaders:
        #         connection = reader.createConnection()
        #         reader_name = connection.getReader()
        #         reader_number = int(reader_name.split(" ")[4])
        #         reader_numbers.append(reader_number)
        #     print("Readers numbers list:,", reader_numbers)
        #     if (reader_number - 1) in reader_numbers:
        #         cb_true()
        #     else:
        #         cb_false()
        # else:
        #     cb_false()


class PosObserver(CardObserver):
    """ NFC-card observer that is notified
        when readers are added/removed from the system
    """
    def __init__(self, station_app):
        self._station_app = station_app
        self.addedcards = None
        self.removedcards = None

    def update(self, observable, actions):
        (self.addedcards, self.removedcards) = actions
        for card in self.addedcards:
            connection = card.createConnection()
            reader_name = connection.getReader()
            reader_number = int(reader_name.split(" ")[4])
            self._station_app.logger.info("RFID chip is detected at position %s ", reader_number)

            if reader_number == 0:
                self._station_app.nfc_pos1_posedge()
            elif reader_number == 1:
                self._station_app.nfc_pos2_posedge()
            elif reader_number == 2:
                self._station_app.nfc_pos3_posedge()

        for card in self.removedcards:
            connection = card.createConnection()
            reader_name = connection.getReader()
            reader_number = int(reader_name.split(" ")[4])
            self._station_app.logger.info("RFID chip was removed from position %s ", reader_number)

            if reader_number == 0:
                self._station_app.nfc_pos1_negedge()
            elif reader_number == 1:
                self._station_app.nfc_pos2_negedge()
            elif reader_number == 2:
                self._station_app.nfc_pos3_negedge()

    def check_pos(self, pos_number, cb_true, cb_false):
        reader_numbers = list()
        if self.addedcards:
            for card in self.addedcards:
                connection = card.createConnection()
                reader_name = connection.getReader()
                reader_number = int(reader_name.split(" ")[4])
                reader_numbers.append(reader_number)

            if (pos_number-1) in reader_numbers:
                cb_true()
            else:
                cb_false()
        else:
            cb_false()


