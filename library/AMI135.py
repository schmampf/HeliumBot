from pyvisa import ResourceManager
import numpy as np
from logging import getLogger
from datetime import datetime

logger = getLogger("HeliumBot")


class AMI135:
    """
    Helium Level Meter Scheer 2
    """

    def __init__(self, address=1, name="AMI135"):
        rm = ResourceManager()
        self.inst = rm.open_resource(f"ASRL{address}::INSTR")
        self.inst.read_termination = "\r\n"
        self.inst.timeout = 10000
        self.with_IVC = True
        self.name = name

        self.config = {"0": (12, 12.5), "66": (37.5, 45.5), "119": (78, 97), "122.3": (79, 99)}
        logger.info(f"({self.name}) ... initialized!")

    def exit(self):
        self.inst.close()
        logger.info(f"({self.name}) ... closed!")

    @property
    def keys(self):
        keys = []
        for key in self.config.keys():
            keys.append(key)
        return keys

    @property
    def get_fill_height(self):
        fill_height = float(self.inst.query("LEVEL"))
        return fill_height

    def fill_height_to_volume(self, fill_height):
        keys = self.keys

        index = 1 - int(self.with_IVC)

        check = False
        if np.shape(fill_height) == ():
            fill_height = np.array([fill_height], dtype="float64")
            check = True
        else:
            fill_height = np.array(fill_height, dtype="float64")

        volume = []
        for cm in fill_height:
            try:
                for i, key in enumerate(keys):
                    if float(key) <= cm < float(keys[i + 1]):
                        volume.append(
                            self.config[key][index]
                            + (cm - float(key))
                            * (self.config[keys[i + 1]][index] - self.config[key][index])
                            / (float(keys[i + 1]) - float(key))
                        )
            except:
                if cm == float(key):
                    volume.append(self.config[key][index])
                else:
                    volume.append(999.9)

        if check:
            volume = volume[0]
        else:
            volume = np.array(volume)
        return volume

    def volume_to_ratio(self, volume):
        index = 1 - int(self.with_IVC)
        if volume <= self.config[self.keys[0]][index]:
            ratio = np.nan
        else:
            ratio = volume / self.config[self.keys[-1]][index] * 100
        return ratio

    @property
    def status(self):
        utc_timer = datetime.utcnow()
        fill_height = self.get_fill_height
        volume = self.fill_height_to_volume(fill_height)
        ratio = self.volume_to_ratio(volume)
        file_string = f"{utc_timer.strftime('%Y-%m-%d %H:%M:%S')}, {fill_height}, {volume}, {ratio}"
        printer = f"{utc_timer.strftime('%Y-%m-%d %H:%M:%S')}, {fill_height} cm, {volume:3.2f} L, {ratio:3.2f} %"
        status = {"file_string": file_string, "printer": printer, "volume": volume}
        logger.debug(f"({self.name}) {status['printer']}")
        return status
