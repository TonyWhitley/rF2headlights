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
from gui import run, gui_main, status_poker_fn, KEYBOARD, TIMER_EVENT

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
    def pit_limiter():
        return config_o.get('miscellaneous', 'pit_limiter') == '1'
    def pit_lane():
        return config_o.get('miscellaneous', 'pit_lane') == '1'
    def flash_duration():
        return int(config_o.get('miscellaneous', 'flash_duration'))
    def pit_flash_duration():
        return int(config_o.get('miscellaneous', 'pit_flash_duration'))
    def default_to_on():
        return config_o.get('miscellaneous', 'default_to_on') == '1'
    def on_automatically():
        return int(config_o.get('miscellaneous', 'on_automatically'))

    _root, tabConfigureFlash = gui_main()
    _player_is_driving = False
    _o_run = run(_root, tabConfigureFlash)
    _o_run.controller_o.start_pit_check_timer() # Start the 1 second timer
    while True:
        _cmd = _o_run.running()
        if headlightFlash_o.player_is_driving():
            if not _player_is_driving:
                # First time player takes control
                _player_is_driving = True
                if default_to_on():
                    status_poker_fn('default_to_on')
                    headlightFlash_o.on()

            if _cmd == 'Headlights off':
                headlightFlash_o.on()
            if _cmd == 'Headlights on':
                headlightFlash_o.off()
            if _cmd == 'Flash headlights':
                headlightFlash_o.four_flashes(flash_duration())
            if _cmd == 'Toggle headlights':
                headlightFlash_o.toggle()
            if _cmd == TIMER_EVENT:
                if pit_limiter():
                    headlightFlash_o.check_pit_limiter(pit_flash_duration())
                if pit_lane():
                    headlightFlash_o.check_pit_lane(pit_flash_duration())
                headlightFlash_o.automatic_headlights(on_automatically())
        else:
            _player_is_driving = False
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
    if _info.isRF2running():
        print('rFactor2 is running')
        print(_info.versionCheckMsg)
    else:
        print('\nrFactor2 is not running\n')

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
            status_poker_fn('\nHeadlight toggle control must be a key.\n')
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
        status_poker_fn('Overtaking flash')
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
                status_poker_fn('Entered pit lane')
                self.pit_lane_flashes(pit_flash_duration)

    def on(self) -> None:
        """ Turn them on regardless """
        status_poker_fn('Headlights on')
        if not self.are_headlights_on():
            self.toggle()

    def off(self) -> None:
        """ Turn them off regardless """
        status_poker_fn('Headlights off')
        if self.are_headlights_on():
            self.toggle()

    def automatic_headlights(self, on_automatically) -> None:
        """
        # Headlights on when:
                    # 0     Driver turns them on
                    # 1     At least one other driver has them on
                    # 2     More than one other driver has them on
                    # 3     At least half of the other drivers have them on
                    # 4     All the other drivers have them on
        """
        _on = False
        if self._flashing:
            return  # Don't turn headlights on when flashing

        if on_automatically and not self.are_headlights_on():
            _num_drivers = self._info.Rf2Scor.mScoringInfo.mNumVehicles
            _num_drivers_with_lights = 0
            for _driver in range(_num_drivers):
                if self._info.Rf2Tele.mVehicles[_driver].mHeadlights:
                    _num_drivers_with_lights += 1
            # Total includes the player so
            _num_drivers -= 1

            if on_automatically == 1 and _num_drivers_with_lights:
                _on = True
                status_poker_fn('At least one other driver has headlights on')
            if on_automatically == 2 and _num_drivers_with_lights > 1:
                _on = True
                status_poker_fn('More than one other driver has headlights on')
            if on_automatically == 3 and \
                _num_drivers_with_lights >= (_num_drivers/2):
                _on = True
                status_poker_fn('At least half of the other drivers have headlights on')
            if on_automatically == 4 and \
                _num_drivers_with_lights >= _num_drivers:
                _on = True
                status_poker_fn('All the other drivers have headlights on')
            if _on:
                self.on()

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
        if self._info.isSharedMemoryAvailable():
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
                    status_poker_fn('Not on track')
            else:
                status_poker_fn('Track not loaded')
        else:
            status_poker_fn('rFactor 2 not running')
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

    def player_is_driving(self) -> bool:
        """ If not there's no point trying to control the headlights """
        return self._info.isRF2running() and \
            self._info.versionCheckMsg != '' and \
            self._info.isTrackLoaded() and \
            self._info.isOnTrack()


if __name__ == "__main__":
    main()
