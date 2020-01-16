import subprocess
import time


class ShellCommand:
    """ ShellCommand executes terminal command via subprocess interface """

    @staticmethod
    def run(cmd):
        """ Run the command sent via `cmd` string """
        return subprocess.check_output(cmd, shell=True).decode('utf-8')


class NetworkUtil:
    """ NetworkUtil includes util methods to interact with the OS Network """

    @staticmethod
    def get_ipv4():
        """ Return the IPv4 from the Network configuration via the `hostname -I` command """
        GET_IPV4_CMD = 'hostname -I'

        retry_limit = 60
        ips_list = []
        while not ips_list and retry_limit > 0:

            output = ShellCommand.run(GET_IPV4_CMD)
            ips_list = output.split()

            time.sleep(1)
            retry_limit -= 1

        if retry_limit == 0:
            raise ValueError("Number of retries exceeded, check the device's network configuration")

        return ips_list[0]


##############################
#                            #
#      Example of usage      #
#                            #
##############################

# In order to get the connected IPv4
try:
    ipv4 = NetworkUtil.get_ipv4()
except ValueError as e:
    # In case the method is not able to recognize the IPv4, or the device is not connected to any
    # network it is possible to make a fallback solution or reboot the device
    print(e)
    ipv4 = 'error'

print(ipv4)
