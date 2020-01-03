from configIni import Config
import unittest
from unittest import mock

import tkinter as tk

import rF2headlights
from gui import rFactorHeadlightControlFrame


def mock_status_poker_fn(_str):
    print(_str)

#pylint: disable=protected-access

class Test_test_headlights(unittest.TestCase):
    @mock.patch('gui.status_poker_fn', side_effect=mock_status_poker_fn)
    @mock.patch('pyDirectInputKeySend.directInputKeySend.PressReleaseKey')
    def setUp(self, mock_status_poker_fn, PressReleaseKey):  # pylint: disable=arguments-differ,unused-argument
        self.headlightFlash_o = rF2headlights.HeadlightControl()
        for i, ch in enumerate('3.6.0.0'):
            self.headlightFlash_o._info.Rf2Ext.mVersion[i] = ord(ch)
        self.headlightFlash_o._info.Rf2Ext.is64bit = 1
        self.headlightFlash_o._info.Rf2Ext.mSessionStarted = 1
        self.headlightFlash_o._info.Rf2Ext.mInRealtimeFC = 1
        self.headlightFlash_o._info.playersVehicleTelemetry().mIgnitionStarter = 1
        self.headlightFlash_o.escape_pressed = False
        self.headlightFlash_o.headlightToggleDIK = 'DIK_H'
        rF2headlights.bypass_timer = True

    def test_null(self):
        """ test SetUp """
        assert self.headlightFlash_o

    def test_versionCheck(self):
        """ test Version poking """
        msg = self.headlightFlash_o._info.versionCheck()
        assert self.headlightFlash_o._info.sharedMemoryVerified, msg

    def test_pit_limiter_flashes(self):
        """
        self.headlightFlash_o._info.playersVehicleTelemetry().mSpeedLimiter = 1
        #rF2headlights.SetTimer(4000, self.SpeedLimiterOff)
        pit_flash_duration = (100,20)
        self.headlightFlash_o.pit_limiter_flashes(pit_flash_duration)
        """

    def SpeedLimiterOff(self):
        """ Timer callback """
        self.headlightFlash_o._info.playersVehicleTelemetry().mSpeedLimiter = 0


class Test_test_config(unittest.TestCase):
    def test_pit_flash_duration(self):
        config_o = Config()
        on_time, off_time = \
            (int(config_o.get('miscellaneous', 'pit_flash_on_time')),
             int(config_o.get('miscellaneous', 'pit_flash_off_time')))

        print(on_time, off_time)


class Test_test_gui(unittest.TestCase):
    def test_1(self):
        root = tk.Tk()
        frame = rFactorHeadlightControlFrame(root)
        frame.get_headlight_control('nosuchfile')
        root.destroy()
        pass


if __name__ == '__main__':
    unittest.main()
