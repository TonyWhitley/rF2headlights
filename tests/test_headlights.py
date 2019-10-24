import unittest

import rF2headlights

class Test_test_headlights(unittest.TestCase):
    def setUp(self):
        self.headlightFlash_o = rF2headlights.HeadlightControl()
        for i, ch in enumerate('3.6.0.0'):
            self.headlightFlash_o._info.Rf2Ext.mVersion[i] = ord(ch)
        self.headlightFlash_o._info.Rf2Ext.is64bit = 1
        self.headlightFlash_o._info.Rf2Ext.mSessionStarted = 1
        self.headlightFlash_o._info.Rf2Ext.mInRealtimeFC = 1
        self.headlightFlash_o._info.playersVehicleTelemetry().mIgnitionStarter = 1
        self.headlightFlash_o.escape_pressed = False
        self.headlightFlash_o.headlightToggleDIK = 'DIK_H'
    def test_null(self):
        """ test SetUp """
        assert self.headlightFlash_o
    def test_versionCheck(self):
        """ test Version poking """
        msg = self.headlightFlash_o._info.versionCheck()
        assert self.headlightFlash_o._info.sharedMemoryVerified, msg
    def test_pit_limiter_flashes(self):
        rF2headlights.SetTimer(4000, self.SpeedLimiterOff)
        self.headlightFlash_o._info.playersVehicleTelemetry().mSpeedLimiter = 1
        pit_flash_duration = (20,20)
        self.headlightFlash_o.pit_limiter_flashes(pit_flash_duration)
        pass
    def SpeedLimiterOff(self):
        """ Timer callback """
        self.headlightFlash_o._info.playersVehicleTelemetry().mSpeedLimiter = 0


if __name__ == '__main__':
    unittest.main()
