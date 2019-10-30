import unittest
from unittest import mock

import rF2headlights
from pyDirectInputKeySend.directInputKeySend import PressReleaseKey
from gui import status_poker_fn

def mock_status_poker_fn(str):
    print(str)

class Test_test_headlights(unittest.TestCase):
    @mock.patch('gui.status_poker_fn', side_effect=mock_status_poker_fn)
    @mock.patch('pyDirectInputKeySend.directInputKeySend.PressReleaseKey')
    def setUp(self, mock_status_poker_fn, PressReleaseKey):
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
        self.headlightFlash_o._info.playersVehicleTelemetry().mSpeedLimiter = 1
        #rF2headlights.SetTimer(4000, self.SpeedLimiterOff)
        pit_flash_duration = (100,20)
        self.headlightFlash_o.pit_limiter_flashes(pit_flash_duration)
    def SpeedLimiterOff(self):
        """ Timer callback """
        self.headlightFlash_o._info.playersVehicleTelemetry().mSpeedLimiter = 0

from configIni import Config

class Test_test_config(unittest.TestCase):
    def test_pit_flash_duration(self):
        config_o = Config()
        on_time, off_time = \
            (int(config_o.get('miscellaneous', 'pit_flash_on_time')),
            int(config_o.get('miscellaneous', 'pit_flash_off_time')))

        print(on_time, off_time)
if __name__ == '__main__':
    unittest.main()
