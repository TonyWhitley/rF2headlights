# https://discourse.panda3d.org/t/game-controllers-on-windows-without-pygame/14129
# Original release by rdb under the Unlicense (unlicense.org)
# Modified by wezu and then by tjw
from __future__ import print_function
from math import floor, ceil
import time
import ctypes
from ctypes.wintypes import WORD, UINT, DWORD
from ctypes.wintypes import WCHAR as TCHAR
from direct.showbase.DirectObject import DirectObject
import winreg

# Fetch function pointers
joyGetNumDevs = ctypes.windll.winmm.joyGetNumDevs
joyGetPos = ctypes.windll.winmm.joyGetPos
joyGetPosEx = ctypes.windll.winmm.joyGetPosEx
joyGetDevCaps = ctypes.windll.winmm.joyGetDevCapsW

# Define constants
MAXPNAMELEN = 32
MAX_JOYSTICKOEMVXDNAME = 260

JOY_RETURNX = 0x1
JOY_RETURNY = 0x2
JOY_RETURNZ = 0x4
JOY_RETURNR = 0x8
JOY_RETURNU = 0x10
JOY_RETURNV = 0x20
JOY_RETURNPOV = 0x40
JOY_RETURNBUTTONS = 0x80
JOY_RETURNRAWDATA = 0x100
JOY_RETURNPOVCTS = 0x200
JOY_RETURNCENTERED = 0x400
JOY_USEDEADZONE = 0x800
JOY_RETURNALL = JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ | JOY_RETURNR | JOY_RETURNU | JOY_RETURNV | JOY_RETURNPOV | JOY_RETURNBUTTONS

# Define some structures from WinMM that we will use in function calls.
class JOYCAPS(ctypes.Structure):
    _fields_ = [
        ('wMid', WORD),
        ('wPid', WORD),
        ('szPname', TCHAR * MAXPNAMELEN),
        ('wXmin', UINT),
        ('wXmax', UINT),
        ('wYmin', UINT),
        ('wYmax', UINT),
        ('wZmin', UINT),
        ('wZmax', UINT),
        ('wNumButtons', UINT),
        ('wPeriodMin', UINT),
        ('wPeriodMax', UINT),
        ('wRmin', UINT),
        ('wRmax', UINT),
        ('wUmin', UINT),
        ('wUmax', UINT),
        ('wVmin', UINT),
        ('wVmax', UINT),
        ('wCaps', UINT),
        ('wMaxAxes', UINT),
        ('wNumAxes', UINT),
        ('wMaxButtons', UINT),
        ('szRegKey', TCHAR * MAXPNAMELEN),
        ('szOEMVxD', TCHAR * MAX_JOYSTICKOEMVXDNAME),
    ]

class JOYINFO(ctypes.Structure):
    _fields_ = [
        ('wXpos', UINT),
        ('wYpos', UINT),
        ('wZpos', UINT),
        ('wButtons', UINT),
    ]

class JOYINFOEX(ctypes.Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('dwFlags', DWORD),
        ('dwXpos', DWORD),
        ('dwYpos', DWORD),
        ('dwZpos', DWORD),
        ('dwRpos', DWORD),
        ('dwUpos', DWORD),
        ('dwVpos', DWORD),
        ('dwButtons', DWORD),
        ('dwButtonNumber', DWORD),
        ('dwPOV', DWORD),
        ('dwReserved1', DWORD),
        ('dwReserved2', DWORD),
    ]

povbtn_names = ['pad_up', 'pad_right', 'pad_down', 'pad_left']

class Controller(DirectObject):
    def __init__(self, controller_name='joystick'):
        self.controller_name=controller_name
        self.has_devices=False

        # Get the number of supported devices (usually 16).
        num_devs = joyGetNumDevs()
        if num_devs == 0:
            print("Joystick driver not loaded.")
            return

        # Number of the joystick to open.
        for joy_id in range(num_devs):

            # Check if the joystick is plugged in.
            joyinfo = JOYINFO()
            p_info = ctypes.pointer(joyinfo)
            if joyGetPos(0, p_info) != 0:
                print("Joystick %d not plugged in." % (joy_id + 1))
                next

            # Get device capabilities.
            self.caps = JOYCAPS()
            x = joyGetDevCaps(joy_id, ctypes.pointer(self.caps), ctypes.sizeof(JOYCAPS))
            if x != 0:
                #print("Failed to get device capabilities.")
                next
            # "Microsoft PC-joystick driver" print(self.caps.szPname)

            # Fetch the name from registry.
            key = None
            if len(self.caps.szRegKey) > 0:
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "System\\CurrentControlSet\\Control\\MediaResources\\Joystick\\%s\\CurrentJoystickSettings" % (self.caps.szRegKey))
                except WindowsError:
                    key = None

            if key:
                # Computer\HKEY_LOCAL_MACHINE\SYSTEM\Setup\Upgrade\PnP\CurrentControlSet\Control\DeviceMigration\Devices\USB\VID_0810&PID_E501\7&c7a4f36&0&1
                oem_name = winreg.QueryValueEx(key, "Joystick%dOEMName" % (joy_id + 1))
                if oem_name:
                    #key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "System\\CurrentControlSet\\Control\\MediaProperties\\PrivateProperties\\Joystick\\OEM\\%s" % (oem_name[0]))
                    keybit = r"System\Setup\Upgrade\PnP\CurrentControlSet\Control\DeviceMigration\Devices\USB\%s" % (oem_name[0])
                    key2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keybit)
                    if key2:
                        #try:
                        for k in winreg.QueryInfoKey(key2):
                            subkey = None
                            try:
                                subkey = winreg.EnumKey(key2,k)
                            except: next
                            if subkey:
                                key3 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, keybit+ '\\' + subkey)
                                #winreg.EnumValue(key3,0)
                                BusDeviceDesc = winreg.QueryValueEx(key3, "BusDeviceDesc")
                                print("BusDeviceDesc: ", BusDeviceDesc[0])
                        #except: pass
                    key2.Close()

        self.has_devices=True

        # Button states
        self.last_button_states={'pad_up':False, 'pad_right':False, 'pad_down':False, 'pad_left':False}
        for b in range(self.caps.wNumButtons):
            name = 'button_'+str(b)
            if (1 << b) & joyinfo.wButtons:
                self.last_button_states[name] = True
            else:
                self.last_button_states[name] = False
        self.last_analog={'x':0,'y':0,'rx':0,'ry':0,'lt':0, 'rt':0}

        # Initialise the JOYINFOEX structure.
        self.joyinfoex = JOYINFOEX()
        self.joyinfoex.dwSize = ctypes.sizeof(JOYINFOEX)
        self.joyinfoex.dwFlags = JOY_RETURNBUTTONS | JOY_RETURNCENTERED | JOY_RETURNPOV | JOY_RETURNU | JOY_RETURNV | JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ
        self.joyinfoex_pointer = ctypes.pointer(self.joyinfoex)

        #task
        taskMgr.add(self._update, 'controller._update')

    def _update(self, task):
        # Fetch new joystick data until it returns non-0 (that is, it has been unplugged)
        if joyGetPosEx(0, self.joyinfoex_pointer) == 0:
            # Analog stick/trigger
            analog={}
            # Remap the values to float
            analog['x'] = (self.joyinfoex.dwXpos - 32767) / 32768.0
            analog['y'] = (self.joyinfoex.dwYpos - 32767) / 32768.0
            analog['rx'] = (self.joyinfoex.dwRpos - 32767) / 32768.0
            analog['ry'] = (self.joyinfoex.dwUpos - 32767) / 32768.0
            # NB.  Windows drivers give one axis for the trigger, but I want to have
            # two for compatibility with platforms that do support them as separate axes.
            # This means it'll behave strangely when both triggers are pressed, though.
            trig = (self.joyinfoex.dwZpos - 32767) / 32768.0
            analog['lt'] = max(-1.0,  trig * 2 - 1.0)
            analog['rt'] = max(-1.0, -trig * 2 - 1.0)

            # Figure out which buttons are pressed.
            button_states={}
            for b in range(self.caps.wNumButtons):
                pressed = (0 != (1 << b) &  self.joyinfoex.dwButtons)
                name = 'button_'+str(b)
                button_states[name] = pressed

            # Determine the state of the POV buttons using the provided POV angle.
            if  self.joyinfoex.dwPOV == 65535:
                povangle1 = None
                povangle2 = None
            else:
                angle = self.joyinfoex.dwPOV / 9000.0
                povangle1 = int(floor(angle)) % 4
                povangle2 = int(ceil(angle)) % 4

            for i, btn in enumerate(povbtn_names):
                if i == povangle1 or i == povangle2:
                    button_states[btn] = True
                else:
                    button_states[btn] = False

            # Send events
            for button, state in button_states.items():
                if self.last_button_states[button] != state:
                    if state is False:
                        messenger.send(button+'-up')
                    else:
                        messenger.send(button)
                        messenger.send(self.controller_name, [button])

            for axis, state in analog.items():
                if self.last_analog[axis] != state:
                    messenger.send(self.controller_name+'-analog', [axis, state])

            # Remember the state for next time
            self.last_button_states=button_states
            self.last_analog=analog

            return task.cont
        else:
            self.has_devices=False
            return task.done


from panda3d.core import *
from direct.showbase import ShowBase
from direct.showbase.DirectObject import DirectObject

class Demo(DirectObject):
    def __init__(self):
        base = ShowBase.ShowBase()

        self.joy_pad=Controller('joystick')
        #get all buttons
        self.accept('joystick', self.print_key)
        #get all axis
        self.accept('joystick-analog', self.print_axis)
        #get just one specific
        self.accept('button_0', self.jump)
        #good-ol'-keymap

        #key mapping
        self.keyMap = {'key_up': False,
                       'key_down': False,
                       'key_left': False,
                       'key_right': False}
        self.accept('pad_up', self.keyMap.__setitem__, ["key_up", True])
        self.accept('pad_up-up', self.keyMap.__setitem__, ["key_up", False])
        self.accept('pad_down', self.keyMap.__setitem__, ["key_down", True])
        self.accept('pad_down-up', self.keyMap.__setitem__, ["key_down", False])
        self.accept('pad_left', self.keyMap.__setitem__, ["key_left", True])
        self.accept('pad_left-up', self.keyMap.__setitem__, ["key_left", False])
        self.accept('pad_right', self.keyMap.__setitem__, ["key_right", True])
        self.accept('pad_right-up', self.keyMap.__setitem__, ["key_right", False])

    def jump(self):
        print('jump!')

    def print_axis(self, axis, pos):
        print(axis, pos)

    def print_key(self, key):
        print(key)

d=Demo()
base.run()