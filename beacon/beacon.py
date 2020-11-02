"""
This is a monitoring agent publishing a system information packet to a file configured server
"""
from typing import Dict, Tuple
import os
import sys
import socket
import platform
import time
import pickle
import json

import psutil
import GPUtil
import daemon


class ConfigFileInvalidError(Exception):
    pass


class SystemInformation:
    """
    Represents a collection of system information items that can be updated and serialized
    """
    def __init__(self):
        self._sys_info: Dict[str, str] = {}
        self._load_static_info()

    def update_and_serialize(self) -> bytes:
        """
        Load updated system information and return it in serialized form
        :return:
        """
        self._update()
        return self._serialize()

    def _load_static_info(self):
        """
        Loads the static components of system info, doesn't need to be queried every time
        """
        self._sys_info['platform'] = platform.platform()
        self._sys_info['system'] = platform.system()
        self._sys_info['cpu'] = platform.processor()
        self._sys_info['hostname'] = socket.gethostname()

    def _update(self):
        """
        Loads the dynamic components oof system info, has to be called before requesting updated information
        """
        self._sys_info['cpu_usage'] = psutil.cpu_percent(0.2)
        self._sys_info['mem_usage'] = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
        self._sys_info['gpu'] = self._get_gpu_utilization_if_exists()

    def _serialize(self) -> bytes:
        """
        Returns a bytes representation of the system information
        :return:
        """
        return pickle.dumps(self._sys_info)

    @staticmethod
    def _get_gpu_utilization_if_exists(self) -> str:
        load = "Unknown"
        try:
            first_gpu = GPUtil.getFirstAvailable()
            if first_gpu:
                load = str(first_gpu.load)
        except Exception:
            pass
        return load


class Beacon:
    """
    Cyclically sends updated system information over the given socket
    """
    def __init__(self, ip_port: Tuple[str, int], interval: float):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip_port = ip_port
        self.interval = interval
        self.sys_info = SystemInformation()

    def start(self):
        while True:
            payload = self.sys_info.update_and_serialize()
            self._send_sys_info(payload)
            time.sleep(self.interval)

    def _send_sys_info(self, payload: bytes):
        sent_bytes = 0

        # not all bytes might get sent after first call
        while sent_bytes < len(payload):
            sent_bytes += self.sock.sendto(payload, self.ip_port)


class BeaconFactory:
    """
    Creates a beacon object from a config file
    """
    def from_config_file(self, filepath: str) -> Beacon:
        with open(filepath, 'r') as f:
            config = json.load(f)
            self._validate_config_file(config)
            ip = config['server_ip']
            port = config['server_port']
            interval = config['interval']

            return Beacon(ip_port=(ip, port), interval=interval)

    @staticmethod
    def _validate_config_file(config: Dict):
        """
        check that config file contains all mandatory fields and raise a ConfigFileInvalidError if not
        :param config:
        :return:
        """
        if not isinstance(config, dict):
            raise ConfigFileInvalidError("Config file is not a vaild dictionary")
        if "server_ip" not in config.keys():
            raise ConfigFileInvalidError("server_ip missing in config file")
        if "server_port" not in config.keys():
            raise ConfigFileInvalidError("server_port missing in config file")
        if "interval" not in config.keys():
            raise ConfigFileInvalidError("interval missing in config file")


def main():
    factory = BeaconFactory()
    beacon = factory.from_config_file("config.json")
    beacon.start()


if __name__ == '__main__':
    # start beacon as daemon
    # TODO: optionally get config file path from stdin
    config_file = open("config.json", 'r')
    with daemon.DaemonContext(
            files_preserve=[config_file],
            chroot_directory=None,
            stderr=sys.stderr,  # if any, errors shall be printed to stderr
            working_directory=os.getcwd()
    ):
        main()
