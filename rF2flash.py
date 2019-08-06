"""
Flash the headlights in rFactor 2 when a button is pressed.
Read the shared memory to find whether the lights are on or off prior to 
flashing them.  As the headlight control is a toggle read it again to check
they are in the same state afterwards in case a command was missed.
"""

import msvcrt as ms
import sys
from threading import Timer

from directInputKeySend import DirectInputKeyCodeTable, PressReleaseKey
import sharedMemoryAPI

BUILD_REVISION = 1 # The git branch commit count
versionStr = 'rF2flash V0.0.%d' % BUILD_REVISION
versionDate = '2019-08-06'

credits = "Reads the headlight state from rF2 using a Python\n" \
 "mapping of The Iron Wolf's rF2 Shared Memory Tools.\n" \
 "https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin\n" \
 "Original Python mapping implented by\n" \
 "https://forum.studio-397.com/index.php?members/k3nny.35143/\n\n" \
 "Icon made by https://www.flaticon.com/authors/those-icons"


flashButton = '#'
headlightToggle = 'DIK_H'

#################################################################################
def SetTimer(callback, mS: int) -> Timer:
  if mS > 0:
    timer = Timer(mS / 1000, callback)
    timer.start()
  else: 
    pass # TBD delete timer?
  return timer

def StopTimer(timer) -> None:
  timer.cancel()

def msgBox(str: str) -> None:
  print(str)

#################################################################################
def quit(errorCode: int) -> None:
  # User presses a key before exiting program
  print('\n\nPress Enter to exit')
  input()
  sys.exit(errorCode)
#################################################################################

def main() -> None:
    if headlightToggle in DirectInputKeyCodeTable: # (it must be)
        headlightToggleKeycode = headlightToggle[4:]
    else:
        print('\nheadlight toggle button "%s" not recognised.\nIt must be one of:' % headlightToggle)
        for _keyCode in DirectInputKeyCodeTable:
            print(_keyCode, end=', ')
        quit(99)

    headlightFlash_o = HeadlightFlash()

    SetTimer(headlightFlash_o.flash, 5_000)

    while True:
        if ms.kbhit():
            _key = ms.getch()
            if _key == b'#':
                headlightFlash_o.flash()

class HeadlightFlash:
    _info = sharedMemoryAPI.SimInfoAPI()
    print(_info.versionCheckMsg)

    def __init__(self) -> None:
        pass
    def flash(self) -> None:
        if self._info.isRF2running():
            if self._info.isTrackLoaded():
                if self._info.isOnTrack():
                    self.headlightState = self.__headlights()
                    self._count = 20
                    self._toggle()
                else:
                    print('Not on track')
            else:
                print('Track not loaded')
        else:
            print('rFactor 2 not running')
                    
    def _toggle(self) -> None:
        PressReleaseKey(headlightToggle)
        flashTimer = SetTimer(self.__flashTimeout, 20) # type: ignore

    def __flashTimeout(self) -> None:
        self._count -= 1
        if self._count:
            self._toggle()
        else:
            # Check that headlights in same start as originally
            if self.headlightState != self.__headlights():
                    # toggle the headlights again
                    PressReleaseKey(headlightToggle)
    def __headlights(self):
        return self._info.playersVehicleTelemetry().mHeadlights
if __name__ == "__main__":
    main()
