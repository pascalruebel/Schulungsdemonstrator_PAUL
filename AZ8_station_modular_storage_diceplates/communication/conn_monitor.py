import threading
import time

class ConnMonitor(threading.Thread):
    """ Ethernet connection monitor ."""

    def __init__(self, name, logger, conn_alive_cb, conn_broken_cb):
        threading.Thread.__init__(self, name=name, daemon=True)
        self._must_stop = False
        self._conn_alive_cb = conn_alive_cb
        self._conn_broken_cb = conn_broken_cb
        self._logger = logger

    def stop(self):
        self._must_stop = True
        self._logger.info("Ethernet connection monitor has been stopped.")

    def run(self):
        is_triggered = False
        self._logger.info("Ethernet connection monitor has been started.")
        self._conn_alive_cb()

        while not self._must_stop:

            with open('/sys/class/net/eth0/operstate') as f:
                read_data = f.read()
            if (read_data.strip().lower() == 'down') and not is_triggered:
                is_triggered = True
                self._logger.info("Ethernet connection was brocken.")
                self._conn_broken_cb()
            elif (read_data.strip().lower() == 'up') and is_triggered:
                is_triggered = False
                self._logger.info("Ethernet connection was renewed.")
                self._conn_alive_cb()

            f.close()

            time.sleep(1)