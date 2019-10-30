"""
Flash the headlights in rFactor 2 when a button is pressed.
Read the shared memory to find whether the lights are on or off prior to
flashing them.  As the headlight control is a toggle read it again to check
they are in the same state afterwards in case a command was missed.
"""
# pylint: disable=invalid-name

import sys
from threading import Timer
import time

from configIni import Config
from pyDirectInputKeySend.directInputKeySend import DirectInputKeyCodeTable, \
    PressReleaseKey
import pyRfactor2SharedMemory.sharedMemoryAPI as sharedMemoryAPI
from gui import run, gui_main, status_poker_fn, KEYBOARD, TIMER_EVENT

global bypass_timer
bypass_timer = False     # Set for testing, timer calls callback immediately

#################################################################################
def SetTimer(mS, callback, _args=None) -> Timer:
    """ docstring """
    global bypass_timer

    if mS > 0:
        if bypass_timer:
            print(mS)
            time.sleep(mS/1000)
            callback(_args[0])
        else:
            status_poker_fn(str(mS))
            timer = Timer(mS / 1000, callback, args=_args)
            timer.start()
    else:
        pass  # TBD delete timer?
    return timer
#################################################################################
def quit_program(errorCode: int) -> None:
    """ User presses a key before exiting program """
    print('\n\nPress Enter to exit')
    input()
    sys.exit(errorCode)
#################################################################################hhhhh


def main():
    """ docstring """
    global bypass_timer

    headlightFlash_o = HeadlightControl()
    #headlightFlash_o._fake_status()
    #bypass_timer = True
    config_o = Config()
    def pit_limiter():
        return config_o.get('miscellaneous', 'pit_limiter') == '1'
    def pit_lane():
        return config_o.get('miscellaneous', 'pit_lane') == '1'
    def flash_duration():
        return (int(config_o.get('miscellaneous', 'flash_on_time')),
                int(config_o.get('miscellaneous', 'flash_off_time')))
    def pit_flash_duration():
        return (int(config_o.get('miscellaneous', 'pit_flash_on_time')),
                int(config_o.get('miscellaneous', 'pit_flash_off_time')))
    def default_to_on():
        return config_o.get('miscellaneous', 'default_to_on') == '1'
    def on_automatically():
        return int(config_o.get('miscellaneous', 'on_automatically'))

    _root, tabConfigureFlash = gui_main()
    _player_is_driving = False
    _o_run = run(_root, tabConfigureFlash)
    # Start the 1 second timer
    _o_run.controller_o.start_pit_check_timer()
    # side effect is it generates an event which makes running() return
    while True:
        _cmd = _o_run.running()
        if headlightFlash_o.player_is_driving():
            if headlightFlash_o.esc_check():
                continue

            if not _player_is_driving:
                # First time player takes control
                _player_is_driving = True
                if default_to_on():
                    status_poker_fn('default_to_on')
                    headlightFlash_o.on()

            if _cmd == 'Headlights on':
                headlightFlash_o.on()
                status_poker_fn('Headlights on')
            if _cmd == 'Headlights off':
                headlightFlash_o.off()
                status_poker_fn('Headlights off')
            if _cmd == 'Flash headlights':
                headlightFlash_o.four_flashes(flash_duration())
                status_poker_fn('Overtaking flash')
            if _cmd == 'Toggle headlights':
                headlightFlash_o.toggle()
                status_poker_fn('Headlights toggle')
            if _cmd == TIMER_EVENT:
                if pit_limiter():
                    headlightFlash_o.check_pit_limiter(pit_flash_duration())
                if pit_lane():
                    headlightFlash_o.check_pit_lane(pit_flash_duration())
                headlightFlash_o.automatic_headlights(on_automatically())
        else:
            _player_is_driving = False
            headlightFlash_o.stop_flashing()
            #_o_run.controller_o.stop_pit_check_timer()
            # It then needs restarting, which is tricky
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
    timer = (None,None) # On time, off time
    _timestamp = 0
    _in_pit_lane = False
    _info = sharedMemoryAPI.SimInfoAPI()
    escape_pressed = False
    _fake_escape_pressed = False

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
        self._count = 8  # 4 flashes
        self.start_flashing(self.count_down, flash_duration)

    def pit_limiter_flashes(self, pit_flash_duration) -> None:
        """ Flash while the pit limiter is on """
        self.start_flashing(self.__pit_limiter_is_off, pit_flash_duration)

    def check_pit_limiter(self, pit_flash_duration) -> None:
        """ Is the pit limiter on? """
        if self._info.isOnTrack():
            if not self.__pit_limiter_is_off():
                self.pit_limiter_flashes(pit_flash_duration)

    def pit_lane_flashes(self, pit_flash_duration) -> None:
        """ Flash while in the pit lane """
        self.start_flashing(self.__not_in_pit_lane, pit_flash_duration)

    def check_pit_lane(self, pit_flash_duration) -> None:
        """ Has the car entered the pit lane? """
        if self._info.isOnTrack():
            if not self.__not_in_pit_lane():
                if not self._in_pit_lane:
                    status_poker_fn('Entered pit lane')
                    self.pit_lane_flashes(pit_flash_duration)
                    self._in_pit_lane = True
            else:
                if self._in_pit_lane:
                    status_poker_fn('Left pit lane')
                    self._in_pit_lane = False
        else:
            self._in_pit_lane = False

    def on(self) -> None:
        """ Turn them on regardless """
        #status_poker_fn('on')
        if not self.are_headlights_on():
            self.toggle()

    def off(self) -> None:
        """ Turn them off regardless """
        #status_poker_fn('off')
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

    def esc_check(self) -> bool:
        """
        If mElapsedTime is not changing then player has pressed Esc
        or rFactor does not have focus
        """
        if self._fake_escape_pressed:
            return False
        if not self._info.isOnTrack() or \
            self._timestamp < self._info.playersVehicleTelemetry().mElapsedTime:
            self.escape_pressed = False
        else:
            self.escape_pressed = True
        self._timestamp = self._info.playersVehicleTelemetry().mElapsedTime
        return self.escape_pressed

    def toggle(self) -> None:
        """
        Now this program is controlling the headlights a replacement
        for the headlight control is needed.
        """
        #status_poker_fn('H')
        #self._info.playersVehicleTelemetry().mHeadlights = not \
        #    self._info.playersVehicleTelemetry().mHeadlights
        PressReleaseKey(self.headlightToggleDIK)

    def start_flashing(self, stopping_callback, flash_timer) -> None:
        """ Start flashing (if not already) """
        if not self._flashing:
            self.timer = flash_timer
            self.headlightState = self.are_headlights_on()
            if self.headlightState:
                self.__toggle_off(stopping_callback)
            else:
                self.__toggle_on(stopping_callback)

    def headlight_control_is_live(self) -> bool:
        """ Player is driving the car, headlight control is active """
        if self._info.isSharedMemoryAvailable():
            if self._info.isTrackLoaded():
                if self._info.isOnTrack():
                    if not self.escape_pressed:
                        return True
                    else:
                        status_poker_fn('Esc pressed')
                else:
                    status_poker_fn('Not on track')
            else:
                status_poker_fn('Track not loaded')
        else:
            status_poker_fn('rFactor 2 not running')
        return False

    def __toggle_on(self, stopping_callback) -> None:
        """ Toggle the headlights on unless it's time to stop """
        if self.__ignition_is_on():
            self.on()
            if not stopping_callback():
                self._flashing = True
                __flashTimer = SetTimer(self.timer[0],
                                        self.__toggle_off,
                                        _args=[stopping_callback])
                # type: ignore
                return
        else:
            status_poker_fn('Engine not running')
        self.stop_flashing()

    def __toggle_off(self, stopping_callback) -> None:
        """ Toggle the headlights of unless it's time to stop """
        if self.__ignition_is_on():
            self.off()
            if not stopping_callback():
                self._flashing = True
                __flashTimer = SetTimer(self.timer[1],
                                        self.__toggle_on,
                                        _args=[stopping_callback])
                # type: ignore
                return
        else:
            status_poker_fn('Engine not running')
        self.stop_flashing()

    def stop_flashing(self):
        """ docstring """
        if self._flashing:
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
        res = not self._info.playersVehicleScoring().mInPits
        return res

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
        return self._info.versionCheckMsg != '' and \
            self._info.isTrackLoaded() and \
            self._info.isOnTrack()

    def _fake_status(self) -> None:
        for i, ch in enumerate('3.6.0.0'):
            self._info.Rf2Ext.mVersion[i] = ord(ch)
        self._info.Rf2Ext.is64bit = 1
        self._info.Rf2Ext.mSessionStarted = 1
        self._info.Rf2Ext.mInRealtimeFC = 1
        self._info.playersVehicleTelemetry().mIgnitionStarter = 1
        self._fake_escape_pressed = True
        self.headlightToggleDIK = 'DIK_H'
        self._info.playersVehicleTelemetry().mSpeedLimiter = 1

if __name__ == "__main__":
    main()
