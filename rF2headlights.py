"""
Flash the headlights in rFactor 2 when a button is pressed.
Read the shared memory to find whether the lights are on or off prior to
flashing them.  As the headlight control is a toggle read it again to check
they are in the same state afterwards in case a command was missed.
"""
# pylint: disable=invalid-name

import os
import sys
from threading import Timer
import time

from configIni import Config
from pyDirectInputKeySend.directInputKeySend import DirectInputKeyCodeTable, \
    PressReleaseKey
import pyRfactor2SharedMemory.sharedMemoryAPI as sharedMemoryAPI
from gui import run, gui_main, status_poker_fn, KEYBOARD, TIMER_EVENT

##############################################################################
from StateMachine import State
from StateMachine import StateMachine

class HeadlightsAction:
    def __init__(self, action):
        self.action = action
    def __str__(self): return self.action
    def __cmp__(self, other):
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)

# Static fields; an enumeration of events:
HeadlightsAction.rfactor_running = HeadlightsAction("rfactor_running")
HeadlightsAction.rfactor_stopped = HeadlightsAction("rfactor_stopped")
HeadlightsAction.shared_memory_ok = HeadlightsAction("shared_memory_ok")
HeadlightsAction.track_loaded = HeadlightsAction("track_loaded")
HeadlightsAction.track_exited = HeadlightsAction("track_exited")
HeadlightsAction.car_has_headlights = HeadlightsAction("car_has_headlights")
HeadlightsAction.car_has_no_headlights = HeadlightsAction("car_has_no_headlights")
HeadlightsAction.on_track = HeadlightsAction("on_track")
HeadlightsAction.escape_pressed = HeadlightsAction("escape_pressed")
HeadlightsAction.ai_driving = HeadlightsAction("ai_driving")
HeadlightsAction.player_driving = HeadlightsAction("player_driving")
HeadlightsAction.player_driving_stationary = HeadlightsAction("player_driving_stationary")
HeadlightsAction.in_pits_car_moving = HeadlightsAction("in_pits_car_moving")
HeadlightsAction.in_pits_stationary = HeadlightsAction("in_pits_stationary")
HeadlightsAction.pit_limiter_on_car_moving = HeadlightsAction("pit_limiter_on_car_moving")
HeadlightsAction.pit_limiter_on_stationary = HeadlightsAction("pit_limiter_on_stationary")
HeadlightsAction.overtaking_flash = HeadlightsAction("overtaking_flash")
HeadlightsAction.other_cars_have_headlights_on = HeadlightsAction("other_cars_have_headlights_on")
HeadlightsAction.headlights_on = HeadlightsAction("headlights_on")
HeadlightsAction.headlights_off = HeadlightsAction("headlights_off")
HeadlightsAction.headlights_toggle = HeadlightsAction("headlights_toggle")
HeadlightsAction.E = HeadlightsAction("E")

# A different subclass for each state:

class HeadlightsState(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, HeadlightsState.no_rfactor)

class no_rfactor(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.rfactor_running:
            return HeadlightsState.rfactor_running
        return HeadlightsState.no_rfactor

class rfactor_running(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.shared_memory_ok:
            return HeadlightsState.shared_memory
        return HeadlightsState.rfactor_running

class shared_memory(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.shared_memory

class track_loaded(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.track_loaded

class car_has_headlights(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.car_has_headlights

class on_track(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.on_track

class escape_pressed(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.escape_pressed

class ai_driving(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.ai_driving

class player_driving_headlights_off(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.player_driving_headlights_off

class player_driving_headlights_on(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.player_driving_headlights_on

class player_driving_stationary(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.player_driving_stationary

class in_pits_car_moving(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.in_pits_car_moving

class in_pits_stationary(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.in_pits_stationary

class pit_limiter_on_car_moving(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.pit_limiter_on_car_moving

class pit_limiter_on_stationary(State):
    def run(self):
        pass

    def next(self, input):
        if input == HeadlightsAction.E:
            return HeadlightsState.X
        return HeadlightsState.pit_limiter_on_stationary

# State variable initialization:
HeadlightsState.no_rfactor = no_rfactor()
HeadlightsState.rfactor_running = rfactor_running()
HeadlightsState.shared_memory = shared_memory()
HeadlightsState.track_loaded = track_loaded()
HeadlightsState.car_has_headlights = car_has_headlights()
HeadlightsState.on_track = on_track()
HeadlightsState.escape_pressed = escape_pressed()
HeadlightsState.ai_driving = ai_driving()
HeadlightsState.player_driving_headlights_off = player_driving_headlights_off()
HeadlightsState.player_driving_headlights_on = player_driving_headlights_on()
HeadlightsState.player_driving_stationary = player_driving_stationary()
HeadlightsState.in_pits_car_moving = in_pits_car_moving()
HeadlightsState.in_pits_stationary = in_pits_stationary()
HeadlightsState.pit_limiter_on_car_moving = pit_limiter_on_car_moving()
HeadlightsState.pit_limiter_on_stationary = pit_limiter_on_stationary()
HeadlightsState.X = pit_limiter_on_stationary()

##############################################################################

global bypass_timer
bypass_timer = False     # Set for testing, timer calls callback immediately

##########################################################################


def SetTimer(mS, callback, _args=None) -> Timer:
    """ docstring """
    global bypass_timer

    if mS > 0:
        if bypass_timer:
            print(mS)
            time.sleep(mS / 1000)
            callback(_args[0])
            timer = None
        else:
            # NO!!! Causes a LONG delay status_poker_fn(str(mS))
            timer = Timer(mS / 1000, callback, args=_args)
            timer.start()
    else:
        pass  # TBD delete timer?
    return timer
##########################################################################


def quit_program(errorCode: int) -> None:
    """ User presses a key before exiting program """
    print('\n\nPress Enter to exit')
    input()
    sys.exit(errorCode)
# hhhhh


def main():
    """ docstring """
    global bypass_timer

    headlightFlash_o = HeadlightControl()
    # headlightFlash_o._fake_status()
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

    # States
    """
    NO_RFACTOR
    RFACTOR_RUNNING
    SHARED_MEMORY
    TRACK_LOADED
    CAR_HAS_HEADLIGHTS
    ON_TRACK
    ESCAPE_PRESSED
    AI_DRIVING
    PLAYER_DRIVING_HEADLIGHTS_OFF
    PLAYER_DRIVING_HEADLIGHTS_ON
    PLAYER_DRIVING_STATIONARY
    IN_PITS_CAR_MOVING
    IN_PITS_STATIONARY
    PIT_LIMITER_ON_CAR_MOVING
    PIT_LIMITER_ON_STATIONARY
    """

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
            # _o_run.controller_o.stop_pit_check_timer()
            # It then needs restarting, which is tricky
        if _cmd == 'QUIT':
            break
    if 'DEBUG' in sys.executable:  # rF2headlightsDEBUG.exe
        print('Controllers')
        print(_o_run.controller_o.controller_names)

class HeadlightControl:
    """
    Flash the headlights on and off by sending the key
    that toggles the headlights.
    """
    headlightState = None
    headlightToggleDIK = None
    _flashing = False
    _count = 0
    timer = (None, None)  # On time, off time
    _timestamp = 0
    _in_pit_lane = False
    _info = sharedMemoryAPI.SimInfoAPI()
    escape_pressed = False
    _fake_escape_pressed = False
    _car_has_headlights = True # Until we find otherwise
    tested_car_has_headlights = False
    car_is_moving = False # Initially
    _headlights_state_on_pit_entry = False # Initially

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
                    self._headlights_state_on_pit_entry = self.are_headlights_on()
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
        # status_poker_fn('on')
        if not self.are_headlights_on():
            self.toggle()

    def off(self) -> None:
        """ Turn them off regardless """
        # status_poker_fn('off')
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
                    _num_drivers_with_lights >= (_num_drivers / 2):
                _on = True
                status_poker_fn(
                    'At least half of the other drivers have headlights on')
            if on_automatically == 4 and \
                    _num_drivers_with_lights >= _num_drivers:
                _on = True
                status_poker_fn('All the other drivers have headlights on')
            if _on:
                self.on()

    def car_has_headlights(self) -> bool:
        # Need to retest every time the track is loaded
        if not self.tested_car_has_headlights:
            _save = self.are_headlights_on()
            self.toggle(testing_car_has_headlights=True)
            if sharedMemoryAPI.Cbytestring2Python(self._info.Rf2Ext.mLastHistoryMessage) == \
                'Headlights: N/A':
                self._car_has_headlights = False
            _car = self._info.vehicleName()
            if self._car_has_headlights:
                status_poker_fn(_car + " has headlights")
            else:
                status_poker_fn(_car + " has no headlights")
            self.tested_car_has_headlights = True
        return self._car_has_headlights

    def car_is_moving(self) -> bool:
        #return self._info.playersVehicleTelemetry().mLocalVel.x > 1
        return self._info.playersVehicleTelemetry().mClutchRPM > 10

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

    def toggle(self, testing_car_has_headlights=False) -> None:
        """
        Now this program is controlling the headlights a replacement
        for the headlight control is needed.
        """
        # status_poker_fn('H')
        # self._info.playersVehicleTelemetry().mHeadlights = not \
        #    self._info.playersVehicleTelemetry().mHeadlights
        if testing_car_has_headlights or self.car_has_headlights():
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
        self._in_pit_lane = False
        return False

    def __toggle_on(self, stopping_callback) -> None:
        """ Toggle the headlights on unless it's time to stop """
        if self.headlight_control_is_live() and not stopping_callback():
            self._flashing = True
            if self.__ignition_is_on():
                if self.car_is_moving(): # Only flash if the car is moving
                    self.on()
            else:
                status_poker_fn('Engine not running')
            __flashTimer = SetTimer(self.timer[0],
                                    self.__toggle_off,
                                    _args=[stopping_callback])
            # type: ignore
            return
        self.stop_flashing()

    def __toggle_off(self, stopping_callback) -> None:
        """ Toggle the headlights off unless it's time to stop """
        if self.headlight_control_is_live() and not stopping_callback():
            self._flashing = True
            self.off()
            __flashTimer = SetTimer(self.timer[1],
                                    self.__toggle_on,
                                    _args=[stopping_callback])
            # type: ignore
            return
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
        return self._info.playersVehicleTelemetry().mHeadlights != 0

    def __not_in_pit_lane(self) -> bool:
        """ Used to stop when not in the pit lane """
        res = not self._info.playersVehicleScoring().mInPits
        return res

    def __pit_limiter_is_off(self) -> bool:
        """ Used to stop when the pit limiter is off """
        return not self._info.playersVehicleTelemetry().mSpeedLimiter

    def __ignition_is_on(self) -> bool:
        """ Is it on? """
        return self._info.playersVehicleTelemetry().mIgnitionStarter != 0

    def flashing(self) -> bool:
        """ Are the headlights being flashed? """
        return self._flashing

    def player_is_driving(self) -> bool:
        """ If not there's no point trying to control the headlights """
        if self._info.versionCheckMsg != '' and self._info.isTrackLoaded():
            if self._info.isOnTrack():
                return True
        else:
            self.tested_car_has_headlights = False
        return False

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


def debug() -> None:
    """
    Print out start up debug information if this is a debug .exe
    """
    if 'DEBUG' in sys.executable:  # rF2headlightsDEBUG.exe
        from configIni import CONFIG_FILE_NAME
        from readJSONfile import read_file
        conf_file = os.path.abspath(CONFIG_FILE_NAME)
        try:
            conf = read_file(conf_file)
        except BaseException:
            print(F'Could not read "{conf_file}" "{CONFIG_FILE_NAME}"')
            return
        print(F'\n"{conf_file}" contents:\n')
        print(conf)
        print(F'\n"{conf_file}" contents end\n')


if __name__ == "__main__":
    debug()
    main()
