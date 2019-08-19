"""
Flash the headlights in rFactor 2 when a button is pressed.
Read the shared memory to find whether the lights are on or off prior to
flashing them.  As the headlight control is a toggle read it again to check
they are in the same state afterwards in case a command was missed.
"""
# pylint: disable=invalid-name

import sys
from threading import Timer

from configIni import Config
from pyDirectInputKeySend.directInputKeySend import DirectInputKeyCodeTable, PressReleaseKey
import pyRfactor2SharedMemory.sharedMemoryAPI as sharedMemoryAPI
from gui import run, KEYBOARD, TIMER_EVENT

BUILD_REVISION = 25  # The git branch commit count
versionStr = 'rF2headlights V0.3.%d' % BUILD_REVISION
versionDate = '2019-08-19'

program_credits = "Reads the headlight state from rF2 using a Python\n" \
    "mapping of The Iron Wolf's rF2 Shared Memory Tools.\n" \
    "https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin\n" \
    "Original Python mapping implented by\n" \
    "https://forum.studio-397.com/index.php?members/k3nny.35143/\n\n" \
    "Icon made by https://www.flaticon.com/authors/freepik"


#################################################################################
def SetTimer(mS, callback, _args=None) -> Timer:
    """ docstring """
    if mS > 0:
        timer = Timer(mS / 1000, callback, args=_args)
        timer.start()
    else:
        pass  # TBD delete timer?
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


def main():
    """ docstring """
    headlightFlash_o = HeadlightControl()
    config_o = Config()
    # pylint: disable=C0326
    pit_limiter =           config_o.get('miscellaneous', 'pit_limiter') == '1'
    pit_lane =              config_o.get('miscellaneous', 'pit_lane') == '1'
    flash_duration =    int(config_o.get('miscellaneous', 'flash_duration'))
    pit_flash_duration =int(config_o.get('miscellaneous', 'pit_flash_duration'))
    # pylint: enable=C0326

    _o_run = run()
    _o_run.controller_o.start_timer() # Start the 1 second timer
    while True:
        _cmd = _o_run.running()
        #print(_cmd)
        if _cmd == 'Headlights off':
            headlightFlash_o.on()
        if _cmd == 'Headlights on':
            headlightFlash_o.off()
        if _cmd == 'Flash headlights':
            headlightFlash_o.four_flashes(flash_duration)
        if _cmd == 'Toggle headlights':
            headlightFlash_o.toggle()
        if _cmd == TIMER_EVENT:
            if pit_limiter:
                headlightFlash_o.check_pit_limiter(pit_flash_duration)
            if pit_lane:
                headlightFlash_o.check_pit_lane(pit_flash_duration)
        if _cmd == 'QUIT':
            break


class HeadlightControl:
    """
    Flash the headlights on and off by sending the key
    that toggles the headlights.
    """
    headlightState = None
    headlightToggleDIK = None
    _flashing = False
    _count = 0
    timer = None
    _info = sharedMemoryAPI.SimInfoAPI()
    print(_info.versionCheckMsg)

    def __init__(self) -> None:
        """ docstring """
        config_o = Config()
        if config_o.get('rFactor Toggle', 'controller') == KEYBOARD:
            self.headlightToggleDIK = config_o.get('rFactor Toggle', 'control')
            # (it must be)
            if self.headlightToggleDIK not in DirectInputKeyCodeTable:
                print('\nheadlight toggle button "%s" not recognised.\n'
                      'It must be one of:' %
                      self.headlightToggleDIK)
                for _keyCode in DirectInputKeyCodeTable:
                    print(_keyCode, end=', ')
                quit_program(99)
        else:
            print('\nHeadlight toggle control must be a key.\n')
            quit_program(99)

    def count_down(self) -> bool:
        """
        Stopping callback function
        Returns True is count as expired.
        """
        self._count -= 1
        return self._count <= 0

    def four_flashes(self, flash_duration) -> None:
        """ Flash four times (e.g. for overtaking) """
        self._count = 8  # 4 flashes
        self.timer = flash_duration
        self.start_flashing(self.count_down)

    def pit_limiter_flashes(self, pit_flash_duration) -> None:
        """ Flash while the pit limiter is on """
        self.timer = pit_flash_duration
        self.start_flashing(self.__pit_limiter_is_off)

    def check_pit_limiter(self, pit_flash_duration) -> None:
        """ Is the pit limiter on? """
        if self._info.isOnTrack():
            if not self.__pit_limiter_is_off():
                self.pit_limiter_flashes(pit_flash_duration)

    def pit_lane_flashes(self, pit_flash_duration) -> None:
        """ Flash while in the pit lane """
        self.timer = pit_flash_duration
        self.start_flashing(self.__not_in_pit_lane)

    def check_pit_lane(self, pit_flash_duration) -> None:
        """ Has the car entered the pit lane? """
        if self._info.isOnTrack():
            if not self.__not_in_pit_lane():
                self.pit_lane_flashes(pit_flash_duration)

    def on(self) -> None:
        """ Turn them on regardless """
        if not self.are_headlights_on():
            self.toggle()

    def off(self) -> None:
        """ Turn them off regardless """
        if self.are_headlights_on():
            self.toggle()

    def toggle(self) -> None:
        """
        Now this program is controlling the headlights a replacement
        for the headlight control is needed.
        """
        PressReleaseKey(self.headlightToggleDIK)

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
                            self.toggle()
                            __flashTimer = SetTimer(self.timer,
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
            self.toggle()
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
        """ Is it on? """
        return self._info.playersVehicleTelemetry().mIgnitionStarter

    def flashing(self) -> bool:
        """ Are the headlights being flashed? """
        return self._flashing


if __name__ == "__main__":
    main()
