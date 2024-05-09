from __future__ import annotations
import ctypes
import subprocess
import sys

class Named:
    @staticmethod
    def new(value) -> Named:
        return Named(value)

    def __init__(self, value) -> None:
        self.value = value
    
    def __eq__(self, other: Named) -> bool:
        return self.value == other.value
    
    def __ne__(self, other: Named) -> bool:
        return not self == other
    
def getOS():
    if PLATFORM.startswith('linux'): return 'Linux'
    elif PLATFORM.startswith('darwin'): return 'OSX'
    elif PLATFORM.startswith('win'): return 'Windows'
    return 'Unknown'

def getResolution():
    system = getOS()
    if (system == "Windows"):
        return [USER.GetSystemMetrics(0), USER.GetSystemMetrics(1)]
    elif (system in ["Linux", "OSX"]):
        try:
            output = subprocess.check_output(["xrander"]).decode("utf-8")
            for line in output.split("\n"):
                if ('connected' in line):
                    width, height = line.split()[2].split('x')
                    return [int(width), int(height)]

        except subprocess.CalledProcessError as err:
            return ERROR
    else:
        return ERROR

PLATFORM = sys.platform
if (getOS() == "Windows"):
    USER = ctypes.windll.user32

ERROR = 0

#Testing
if __name__ == "__main__":
    print(getResolution())