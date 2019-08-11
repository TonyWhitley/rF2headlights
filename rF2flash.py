"""
Flash the headlights in rFactor 2 when a button is pressed.
Read the shared memory to find whether the lights are on or off prior to
flashing them.  As the headlight control is a toggle read it again to check
they are in the same state afterwards in case a command was missed.
"""
# pylint: disable=invalid-name

import msvcrt as ms
import sys
from threading import Timer

from directInputKeySend import DirectInputKeyCodeTable, PressReleaseKey
import sharedMemoryAPI

BUILD_REVISION = 10 # The git branch commit count
versionStr = 'rF2flash V0.0.%d' % BUILD_REVISION
versionDate = '2019-08-11'

program_credits = "Reads the headlight state from rF2 using a Python\n" \
 "mapping of The Iron Wolf's rF2 Shared Memory Tools.\n" \
 "https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin\n" \
 "Original Python mapping implented by\n" \
 "https://forum.studio-397.com/index.php?members/k3nny.35143/\n\n" \
 "Icon made by https://www.flaticon.com/authors/those-icons"


flashButton = '#'
headlightToggle = 'DIK_H'

#################################################################################
def SetTimer(mS, callback, _args=None) -> Timer:
    """ docstring """
    if mS > 0:
        timer = Timer(mS / 1000, callback, args=_args)
        timer.start()
    else:
        pass # TBD delete timer?
    return timer

def StopTimer(timer) -> None:
    """ docstring """
    timer.cancel()

def msgBox(string: str) -> None:
    """ docstring """
    print(string)

#################################################################################
def quit_program(errorCode: int) -> None:
    """ User presses a key before exiting program """
    print('\n\nPress Enter to exit')
    input()
    sys.exit(errorCode)
#################################################################################

def main() -> None:
    """ docstring """
    if headlightToggle in DirectInputKeyCodeTable: # (it must be)
        __headlightToggleKeycode = headlightToggle[4:]
    else:
        print('\nheadlight toggle button "%s" not recognised.\nIt must be one of:' %
              headlightToggle)
        for _keyCode in DirectInputKeyCodeTable:
            print(_keyCode, end=', ')
        quit_program(99)

    headlightFlash_o = HeadlightFlash()

    #testing:
    if 1:   # pylint: disable=using-constant-test
        for x in range(1, 50):
            SetTimer(5_000 * x, headlightFlash_o.pit_limiter_flashes)
    if 0:   # pylint: disable=using-constant-test
        for x in range(1, 50):
            SetTimer(5_000 * x, headlightFlash_o.pit_lane_flashes)
    if 0:   # pylint: disable=using-constant-test
        for x in range(1, 10):
            SetTimer(5_000 * x, headlightFlash_o.four_flashes)

    # kbhit only works when this program has focus,
    # not when rF is running
    while True:
        if ms.kbhit():
            _key = ms.getch()
            if _key == b'#':
                headlightFlash_o.four_flashes()

class HeadlightFlash:
    """
    Flash the headlights on and off by sending the key
    that toggles the headlights.
    """
    headlightState = None
    _flashing = False
    _count = 0
    _info = sharedMemoryAPI.SimInfoAPI()
    print(_info.versionCheckMsg)

    def __init__(self) -> None:
        """ docstring """
        # pylint: disable=unnecessary-pass
        pass

    def count_down(self) -> bool:
        """
        Stopping callback function
        Returns True is count as expired.
        """
        self._count -= 1
        return self._count <= 0
    def four_flashes(self) -> None:
        """ Flash four times (e.g. for overtaking) """
        self._count = 8 # 4 flashes
        self.start_flashing(self.count_down)

    def pit_limiter_flashes(self) -> None:
        """ Flash while the pit limiter is on """
        self.start_flashing(self.__pit_limiter_is_off)

    def pit_lane_flashes(self) -> None:
        """ Flash while in the pit lane """
        self.start_flashing(self.__not_in_pit_lane)

    def toggle(self) -> None:
        """
        Now this program is controlling the headlights a replacement
        for the headlight control is needed.
        We could have separate on and off controls too, just call
        are_headlights_on() to decide if they need to be toggled.
        """
        PressReleaseKey(headlightToggle)


    def start_flashing(self, stopping_callback) -> None:
        """ Start flashing (if not already) """
        if not self._flashing:
            self.headlightState = self.are_headlights_on()
            self.__toggle(stopping_callback)

    def __toggle(self, stopping_callback) -> None:
        """ Toggle the headlights unless it's time to stop """
        if self._info.isRF2running():
            if self._info.isTrackLoaded():
                if self._info.isOnTrack():
                    if self.__ignition_is_on():
                        if not stopping_callback():
                            self._flashing = True
                            PressReleaseKey(headlightToggle)
                            __flashTimer = SetTimer(20,
                                                    self.__toggle,
                                                    _args=[stopping_callback])
                            # type: ignore
                            return
                else:
                    print('Not on track')
            else:
                print('Track not loaded')
        else:
            print('rFactor 2 not running')
        self.stop_flashing()

    def stop_flashing(self):
        """ docstring """
        # Check that headlights in same start as originally
        if self.headlightState != self.are_headlights_on():
            # toggle the headlights again
            PressReleaseKey(headlightToggle)
        self._flashing = False

    def are_headlights_on(self) -> bool:
        """ Are they on? """
        return self._info.playersVehicleTelemetry().mHeadlights
    def __not_in_pit_lane(self) -> bool:
        """ Used to stop when not in the pit lane """
        return not self._info.playersVehicleScoring().mInPits
    def __pit_limiter_is_off(self) -> bool:
        """ Used to stop when the pit limiter is off """
        return not self._info.playersVehicleTelemetry().mSpeedLimiter
    def __ignition_is_on(self) -> bool:
        """ Is it pn? """
        return self._info.playersVehicleTelemetry().mIgnitionStarter
    def flashing(self) -> bool:
        """ Are the headlights being flashed? """
        return self._flashing

if __name__ == "__main__":
    main()
