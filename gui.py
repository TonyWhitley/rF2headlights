"""
Set values in headlightControls.ini to configure headlight controls
"""
# pylint: disable=invalid-name

# Python 3
from lib.tkToolTip import Tooltip as Tooltip
from readJSONfile import Json
import pyRfactor2SharedMemory.sharedMemoryAPI as sharedMemoryAPI
from pyDirectInputKeySend.directInputKeySend import KeycodeToDIK, rfKeycodeToDIK
from wheel import Controller
from configIni import Config, CONFIG_FILE_NAME
from os import path
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as font
import sys
import pygame

sys.path.append('rF2headlights')

# pylint: disable=global-statement
# pylint: disable=global-at-module-level
# pylint: disable=global-variable-undefined
global status_poker  # Function pointer to poke text into status window
global status_poker_scroll


def status_poker_fn(string) -> None:
    """
    Jesus! Hack alert!
    Poke text into rFactorStatusFrame class's text widget
    """
    try:
        status_poker(tk.END, string + '\n')
        status_poker_scroll(tk.END)
    except RuntimeError:
        # "main thread is not in main loop" whatever that means
        print(string)
        pass
    except BaseException:  # pylint: disable=bare-except
        pass


BUILD_REVISION = 79  # The git commit count
versionStr = 'rFactor 2 Headlight Controls V1.9.%d' % BUILD_REVISION
versionDate = '2021-06-05'

program_credits = "Reads the headlight state from rF2 using a Python\n" \
    "mapping of The Iron Wolf's rF2 Shared Memory Tools.\n" \
    "https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin\n" \
    "Original Python mapping implemented by\n" \
    "https://forum.studio-397.com/index.php?members/k3nny.35143/\n\n" \
    "Icon made by https://www.flaticon.com/authors/freepik"

KEYBOARD = 'keyboard'

headlight_controls = {
    'Toggle headlights': {
        'tkButton': None,
        'tkLabel': None,
        'ControllerName': None,
        'svControllerName': None,
        'svControl': None,
    },
    'Flash headlights': {
        'tkButton': None,
        'tkLabel': None,
        'ControllerName': None,
        'svControllerName': None,
        'svControl': None,
    },
    'Headlights on': {
        'tkButton': None,
        'tkLabel': None,
        'ControllerName': None,
        'svControllerName': None,
        'svControl': None,
    },
    'Headlights off': {
        'tkButton': None,
        'tkLabel': None,
        'ControllerName': None,
        'svControllerName': None,
        'svControl': None,
    }
}

rfactor_headlight_control = {
    'rFactor Toggle': {
        'tkButton': None,
        'tkLabel': None,
        'ControllerName': None,
        'svControllerName': None,
        'svControl': None,
    }
}

TIMER_EVENT = 'TIMER_EVENT'

tk_event = None


def icon(_root):
    """ Use our icon """
    if getattr(sys, 'frozen', False):
        # running in a PyInstaller bundle (exe)
        _p = path.join(sys._MEIPASS, 'headlight.ico')  #pylint: disable=protected-access
        _root.iconbitmap(_p)
    else:
        # running live
        _root.iconbitmap('resources/headlight.ico')

#########################
# The tab's public class:
#########################


class Tab:
    """ Configure the headlight control app """
    parentFrame = None
    controller_o = Controller()
    config_o = Config()
    xyPadding = 10

    def __tk_event_callback(self, _event):    # pylint: disable=no-self-use
        """ docstring """
        global tk_event  # pylint: disable=global-statement
        tk_event = _event
        if tk_event == 'QUIT':
            sys.exit(0)

    def __init__(self, parentFrame):
        """ Put this into the parent frame """
        self.root = parentFrame.master
        self.parentFrame = parentFrame
        # icon(self.root)

        self.root.bind('<KeyPress>', self.controller_o.tk_event_callback)

        #############################
        # Three sub-frames

        self.headlight_controls_frame_o = headlightControlsFrame(
            self.parentFrame)
        self.headlight_controls_frame_o.tkFrame_headlight_control.grid(
            column=0, row=0, sticky='new', padx=self.xyPadding, rowspan=1)

        self.headlightOptionsFrame_o = headlightOptionsFrame(
            self.parentFrame)
        self.headlightOptionsFrame_o.tkFrame_headlight_control.grid(
            column=1, row=0, sticky='new', padx=self.xyPadding, rowspan=2)

        self.rFactorStatusFrame_o = rFactorStatusFrame(
            self.parentFrame)
        self.rFactorStatusFrame_o.tkFrame_headlight_control.grid(
            column=2, row=0, sticky='new', padx=self.xyPadding, rowspan=3)

        self.rf_headlight_control_frame_o = rFactorHeadlightControlFrame(
            self.parentFrame)
        self.rf_headlight_control_frame_o.tkFrame_headlight_control.grid(
            column=0, row=1, sticky='nsew', padx=self.xyPadding, rowspan=1)

        #############################
        # And a "Save configuration" button
        buttonFont = font.Font(weight='bold', size=10)

        self.tkButtonSave = tk.Button(
            parentFrame,
            text="Save configuration",
            width=20,
            height=2,
            background='green',
            font=buttonFont,
            command=self.save)
        self.tkButtonSave.grid(column=0,
                               row=2,
                               columnspan=2,
                               pady=25,
                               sticky='s')
        #############################

    def save(self):
        """ Save all the settings written to the config data struct """
        self.headlight_controls_frame_o.save()
        self.rf_headlight_control_frame_o.save()
        self.headlightOptionsFrame_o.save()
        self.config_o.write()

    def getSettings(self):  # pylint: disable=no-self-use
        """ Return the settings for this tab """
        return ['Options']

    def setSettings(self, settings):
        """ Set the settings for this tab """
        pass    # pylint: disable=unnecessary-pass


class ControlFrame(Tab):
    """ Generic frame with a list of controls """
    tkFrame_headlight_control = None
    pygame_event = None

    def __init__(self,   # pylint: disable=super-init-not-called
                 parentFrame,
                 frame_name,
                 _headlight_controls):

        self.parentFrame = parentFrame
        self.headlight_controls = _headlight_controls
        self.config_o = super().config_o
        self.tkFrame_headlight_control = tk.LabelFrame(parentFrame,
                                                       text=frame_name,
                                                       padx=self.xyPadding,
                                                       pady=self.xyPadding)

        if self.headlight_controls:
            tk.Label(self.tkFrame_headlight_control,
                     text="Controller").grid(row=0, column=1)
            tk.Label(self.tkFrame_headlight_control,
                     text="Control").grid(row=0, column=2)

        ##########################################################
        for _control_num, (name, control) in enumerate(
                self.headlight_controls.items()):
            # (temp var to simplify and shorten the following lines)
            _control_line = self.headlight_controls[name]
            ##########################################################
            _control_line['tkButton'] = tk.Button(
                self.tkFrame_headlight_control,
                text='Select ' + name,
                width=20,
                command=lambda n=name,
                w=super().controller_o: self.set_control(
                    n,
                    w))
            _control_line['tkButton'].grid(row=_control_num + 2,
                                           sticky='w',
                                           pady=3)
            ##########################################################
            _control_line['svControllerName'] = tk.StringVar()
            _control_line['svControllerName'].set(
                super().config_o.get(name, 'Controller'))
            _control_line['ControllerName'] = \
                tk.Label(self.tkFrame_headlight_control,
                         textvariable=control['svControllerName'],
                         fg='SystemInactiveCaptionText',
                         relief=tk.GROOVE,
                         borderwidth=4,
                         anchor='e',
                         padx=4)
            _control_line['ControllerName'].grid(row=_control_num + 2,
                                                 column=1,
                                                 sticky='e')
            ##########################################################
            _control_line['svControl'] = tk.StringVar()
            __control = super().config_o.get(name, 'Control')
            # if __control.startswith('DIK_'):
            #    __control = __control[len('DIK_'):]
            _control_line['svControl'].set(
                __control)
            _control_line['tkLabel'] = tk.Label(
                self.tkFrame_headlight_control,
                textvariable=control['svControl'],
                fg='SystemInactiveCaptionText',
                relief=tk.GROOVE,
                borderwidth=4,
                anchor='e',
                padx=4)
            _control_line['tkLabel'].grid(row=_control_num + 2,
                                          column=2,
                                          sticky='w')

    def pygame_callback(self, event):
        """ docstring """
        self.pygame_event = event
        print(event) # Seems it's not called

    def set_control(self, name, controller_o):
        """ Wait for user to press a control """
        global tk_event  # pylint: disable=global-statement
        tk_event = None
        self.pygame_event = None
        while True:
            # Run pygame and tk to get latest input
            controller_o.pygame_tk_check(
                self.pygame_callback, self.parentFrame)
            if self.pygame_event:
                if isinstance(self.pygame_event, str):
                    if self.pygame_event == 'TIMER_EVENT':
                        continue
                    else:   # 'QUIT'
                        break
                if self.pygame_event.type == pygame.KEYDOWN:
                    if name == 'rFactor Toggle':
                        # This program's controls must not be a key
                        dik = KeycodeToDIK(self.pygame_event.keycode)
                        self.headlight_controls[name]['svControl'].set(dik)
                        # if dik.startswith('DIK_'):
                        #    dik = dik[len('DIK_'):]
                        self.headlight_controls[name]['tkLabel'].configure(
                            text=dik)
                        self.headlight_controls[name]['ControllerName'].configure(
                            text=KEYBOARD)
                        self.headlight_controls[name]['svControllerName'].set(
                            KEYBOARD)
                        return self.pygame_event.char
                else:
                    if name != 'rFactor Toggle':
                        # The control sent to rFactor must be a key
                        _button = self.pygame_event.button
                        _joy = controller_o.controller_names[self.pygame_event.joy]
                        self.headlight_controls[name]['svControl'].set(_button)
                        self.headlight_controls[name]['tkLabel'].configure(
                            text=str(_button))
                        self.headlight_controls[name]['ControllerName'].configure(
                            text=_joy)
                        self.headlight_controls[name]['svControllerName'].set(
                            _joy)
                        return _button

    def save(self):
        """ Save the Controller/Control pairs to the .ini file """
        for name, control in self.headlight_controls.items():
            self.config_o.set(name, 'Controller',
                              control['svControllerName'].get())
            self.config_o.set(name, 'Control', control['svControl'].get())
        # super().save()  # Parent class handles writing the struct to disc


class headlightControlsFrame(ControlFrame):
    """
    Frame for specifying the controls used by this program to select
    flashing the headlights etc.
    """

    def __init__(self, parentFrame):
        super().__init__(parentFrame,
                         'Player Headlight Controls',
                         headlight_controls)


class rFactorHeadlightControlFrame(ControlFrame):
    """
    Frame for selecting the control that operates the headlight toggle
    Must be a keyboard key
    """

    def __init__(self, parentFrame):
        super().__init__(parentFrame,
                         'rFactor Headlight Control',
                         rfactor_headlight_control)
        ##########################################################
        _match_label = ttk.Label(
            self.tkFrame_headlight_control,
            text='Controller.json keycode must match, it is:')
        _match_label.grid(row=3, columnspan=2, sticky='e')
        Tooltip(_match_label, text='Note: only written when rFactor exits')

        _key_label = tk.Label(self.tkFrame_headlight_control,
                              text=self.get_headlight_control(),
                              fg='SystemInactiveCaptionText',
                              relief=tk.GROOVE,
                              borderwidth=4,
                              anchor='e',
                              padx=4)
        _key_label.grid(row=3, column=2)
        Tooltip(_key_label, text='Note: only written when rFactor exits')

        Tooltip(rfactor_headlight_control['rFactor Toggle']['ControllerName'],
                text='Must be a keyboard key')
        Tooltip(rfactor_headlight_control['rFactor Toggle']['tkButton'],
                text='Must be a keyboard key')

    def get_headlight_control(self, _controller_file_test=None):
        """
        Get the keycode specified in controller.json
        """
        if _controller_file_test:
            _controller_file = _controller_file_test
        else:
            _controller_file = super().config_o.get_controller_file()
        _JSON_O = Json(_controller_file)
        headlight_control = _JSON_O.get_item("Control - Headlights")
        if headlight_control:
            keycode = rfKeycodeToDIK(headlight_control[1])
            return keycode
        err = F'"Control - Headlights" not in {_controller_file}\n'\
            F'See {CONFIG_FILE_NAME} "controller_file" entry'.format()
        messagebox.showinfo('Config error', err)
        return ''


class headlightOptionsFrame(ControlFrame):
    """
    Frame for selecting the pit limiter / pit lane flash options
    and the automatic turning on of the headlights
    """

    def __init__(self, parentFrame):
        super().__init__(parentFrame,
                         'Headlight Options',
                         _headlight_controls={})

        self.pit_limiter = tk.IntVar()
        tkCheckbutton_pitLimiter = tk.Checkbutton(
            self.tkFrame_headlight_control,
            var=self.pit_limiter,
            text='Flash when pit limiter on')

        tkCheckbutton_pitLimiter.grid(sticky='w',
                                      columnspan=2)
        x = self.config_o.get('miscellaneous', 'pit_limiter')
        if not x:
            x = 0
        self.pit_limiter.set(x)

        ##########################################################
        self.pit_lane = tk.IntVar()
        tkCheckbutton_pitLane = tk.Checkbutton(self.tkFrame_headlight_control,
                                               var=self.pit_lane,
                                               text='Flash when in pit lane')

        tkCheckbutton_pitLane.grid(sticky='w',
                                   columnspan=2)
        x = self.config_o.get('miscellaneous', 'pit_lane')
        if not x:
            x = 0
        self.pit_lane.set(x)

        ##########################################################
        self.default_to_on = tk.IntVar()
        tkCheckbutton_pitLane = tk.Checkbutton(self.tkFrame_headlight_control,
                                               var=self.default_to_on,
                                               text='Headlights on at start')

        tkCheckbutton_pitLane.grid(sticky='w',
                                   columnspan=2)
        x = self.config_o.get('miscellaneous', 'default_to_on')
        if not x:
            x = 0
        self.default_to_on.set(x)

        ##########################################################
        _row = 9
        tkLabel_flash_count = tk.Label(self.tkFrame_headlight_control,
                                         text='Overtake flash count')
        tkLabel_flash_count.grid(sticky='se',
                                   column=0,
                                   row=_row)
        self.tkSlider_flash_count = tk.Scale(self.tkFrame_headlight_control,
                                               from_=2,
                                               to=10,
                                               resolution=1,
                                               orient=tk.HORIZONTAL)

        self.tkSlider_flash_count.grid(sticky='w',
                                         column=1,
                                         row=_row)
        x = self.config_o.get('miscellaneous', 'flash_count')
        if not x:
            x = 4
        self.tkSlider_flash_count.set(x)

        ##########################################################
        _row +=1
        tkLabel_flash_on_time = tk.Label(self.tkFrame_headlight_control,
                                         text='Overtake flash ON time')
        tkLabel_flash_on_time.grid(sticky='se',
                                   column=0,
                                   row=_row)
        self.tkSlider_flash_on_time = tk.Scale(self.tkFrame_headlight_control,
                                               from_=10,
                                               to=500,
                                               resolution=10,
                                               orient=tk.HORIZONTAL)

        self.tkSlider_flash_on_time.grid(sticky='w',
                                         column=1,
                                         row=_row)
        x = self.config_o.get('miscellaneous', 'flash_on_time')
        if not x:
            x = 10
        self.tkSlider_flash_on_time.set(x)

        ##########################################################
        _row += 1
        tkLabel_flash_off_time = tk.Label(self.tkFrame_headlight_control,
                                          text='Overtake flash OFF time')
        tkLabel_flash_off_time.grid(sticky='se',
                                    column=0,
                                    row=_row)
        self.tkSlider_flash_off_time = tk.Scale(self.tkFrame_headlight_control,
                                                from_=10,
                                                to=500,
                                                resolution=10,
                                                orient=tk.HORIZONTAL)

        self.tkSlider_flash_off_time.grid(sticky='w',
                                          column=1,
                                          row=_row)
        x = self.config_o.get('miscellaneous', 'flash_off_time')
        if not x:
            x = 10
        self.tkSlider_flash_off_time.set(x)

        ##########################################################
        _row += 1
        tkLabel_pit_flash_on_time = tk.Label(self.tkFrame_headlight_control,
                                             text='Pit flash ON time')
        tkLabel_pit_flash_on_time.grid(sticky='se',
                                       column=0,
                                       row=_row)
        self.tkSlider_pit_flash_on_time = tk.Scale(
            self.tkFrame_headlight_control,
            from_=10,
            to=500,
            resolution=10,
            orient=tk.HORIZONTAL)

        self.tkSlider_pit_flash_on_time.grid(sticky='w',
                                             column=1,
                                             row=_row)
        x = self.config_o.get('miscellaneous', 'pit_flash_on_time')
        if not x:
            x = 10
        self.tkSlider_pit_flash_on_time.set(x)

        ##########################################################
        _row += 1
        tkLabel_pit_flash_off_time = tk.Label(self.tkFrame_headlight_control,
                                              text='Pit flash OFF time')
        tkLabel_pit_flash_off_time.grid(sticky='se',
                                        column=0,
                                        row=_row)
        self.tkSlider_pit_flash_off_time = tk.Scale(
            self.tkFrame_headlight_control,
            from_=10,
            to=500,
            resolution=10,
            orient=tk.HORIZONTAL)

        self.tkSlider_pit_flash_off_time.grid(sticky='w',
                                              column=1,
                                              row=_row)
        x = self.config_o.get('miscellaneous', 'pit_flash_off_time')
        if not x:
            x = 10
        self.tkSlider_pit_flash_off_time.set(x)

        ##########################################################
        _separator = ttk.Separator(self.tkFrame_headlight_control,
                                   orient="horizontal")
        _separator.grid(column=0,
                        sticky="we",
                        columnspan=3)
        ##########################################################
        _row += 2
        self.vars = {}
        _name = 'Automatic headlights'
        self.vars[_name] = tk.StringVar(name=_name)
        # self.vars[_name].set('Fred')

        tkLabel_on_automatically = tk.Label(self.tkFrame_headlight_control,
                                            text='Automatic headlights')
        tkLabel_on_automatically.grid(sticky='se',
                                      column=0,
                                      row=_row)
        self.tkSlider_on_automatically = tk.Scale(
            self.tkFrame_headlight_control,
            command=self.__on_automatically_val,
            showvalue=0,
            from_=0,
            to=4,
            resolution=1,
            orient=tk.HORIZONTAL)

        self.tkSlider_on_automatically.grid(sticky='w',
                                            column=1,
                                            row=_row)
        x = self.config_o.get('miscellaneous', 'on_automatically')
        if not x:
            x = 10
        self.tkSlider_on_automatically.set(x)
        self.__on_automatically_val(x)

        tkLabel_on_automatically_val = tk.Label(
            self.tkFrame_headlight_control,
            textvariable=self.vars['Automatic headlights'])
        _row += 1
        tkLabel_on_automatically_val.grid(sticky='se',
                                          column=0,
                                          columnspan=2,
                                          row=_row)

    def __on_automatically_val(self, event):
        """ Callback when Automatic headlight slider changes """
        _strings = [
            'Driver turns them on',
            'At least one other driver has them on',
            'More than one other driver has them on',
            'At least half of the other drivers have them on',
            'All the other drivers have them on'
        ]
        self.vars['Automatic headlights'].set(_strings[int(event)])

    def save(self):
        """ Save the settings in this frame to the config data struct """
        self.config_o.set('miscellaneous', 'pit_limiter',
                          str(self.pit_limiter.get()))
        self.config_o.set('miscellaneous', 'pit_lane',
                          str(self.pit_lane.get()))
        self.config_o.set('miscellaneous', 'default_to_on',
                          str(self.default_to_on.get()))
        self.config_o.set('miscellaneous', 'flash_count',
                          str(self.tkSlider_flash_count.get()))
        self.config_o.set('miscellaneous', 'flash_on_time',
                          str(self.tkSlider_flash_on_time.get()))
        self.config_o.set('miscellaneous', 'flash_off_time',
                          str(self.tkSlider_flash_off_time.get()))
        self.config_o.set('miscellaneous', 'pit_flash_on_time',
                          str(self.tkSlider_pit_flash_on_time.get()))
        self.config_o.set('miscellaneous', 'pit_flash_off_time',
                          str(self.tkSlider_pit_flash_off_time.get()))
        self.config_o.set('miscellaneous', 'on_automatically',
                          str(self.tkSlider_on_automatically.get()))
        # super().save()  # Parent class handles writing the struct to disc


class rFactorStatusFrame(ControlFrame):
    """
    Frame to show rFactor status
    rF2 running
    Shared memory working
    Track loaded
    On track
    Escape pressed
    AI driving
    Player name
    """

    def __init__(self, parentFrame):
        ####################################################
        # Status frame
        global status_poker
        global status_poker_scroll
        super().__init__(parentFrame,
                         'rFactor Status',
                         {})
        self.parentFrame = parentFrame
        self.vars = dict()
        self._tkCheckbuttons = dict()
        self._leds = dict()
        self._timestamp = 0
        self.xPadding = 10
        self.rFactor_running = False
        tkFrame_Status = tk.LabelFrame(parentFrame, text='rFactor 2 status')
        tkFrame_Status.grid(column=2,
                            row=0,
                            rowspan=3,
                            sticky='nsew',
                            padx=self.xPadding)

        self.__createBoolVar('rF2 running', False)
        self._tkCheckbuttons['rF2 running'] = tk.Checkbutton(
            tkFrame_Status,
            text='rF2 running',
            justify='l',
            state=tk.DISABLED,
            disabledforeground='black',
            selectcolor='white',
            variable=self.vars['rF2 running'])
        self._tkCheckbuttons['rF2 running'].grid(row=0, column=0, sticky='w')

        self._leds['rF2 running'] = self.Led(tkFrame_Status)
        self._leds['rF2 running'].grid(row=0, column=1, sticky='ns')
        self._leds['rF2 running'].set_colour('red')

        self.__createBoolVar('Shared memory working', False)
        self._tkCheckbuttons['Shared memory working'] = \
            tk.Checkbutton(tkFrame_Status,
                           text='Shared memory\nworking',
                           justify='l',
                           state=tk.DISABLED,
                           disabledforeground='black',
                           variable=self.vars['Shared memory working'])
        self._tkCheckbuttons['Shared memory working'].grid(sticky='w')

        self.__createBoolVar('Track loaded', False)
        self._tkCheckbuttons['Track loaded'] = tk.Checkbutton(
            tkFrame_Status,
            text='Track loaded',
            state=tk.DISABLED,
            disabledforeground='black',
            variable=self.vars['Track loaded'])
        self._tkCheckbuttons['Track loaded'].grid(sticky='w')

        self.__createBoolVar('On track', False)
        self._tkCheckbuttons['On track'] = tk.Checkbutton(
            tkFrame_Status,
            text='On track',
            state=tk.DISABLED,
            disabledforeground='black',
            variable=self.vars['On track'])
        self._tkCheckbuttons['On track'].grid(sticky='w')

        self.__createBoolVar('Escape pressed', False)
        self._tkCheckbuttons['Escape pressed'] = tk.Checkbutton(
            tkFrame_Status,
            text='Escape pressed',
            state=tk.DISABLED,
            disabledforeground='black',
            variable=self.vars['Escape pressed'])
        self._tkCheckbuttons['Escape pressed'].grid(sticky='w')

        self.__createBoolVar('AI driving', False)
        self._tkCheckbuttons['AI driving'] = tk.Checkbutton(
            tkFrame_Status,
            text='AI driving',
            state=tk.DISABLED,
            disabledforeground='black',
            variable=self.vars['AI driving'])
        self._tkCheckbuttons['AI driving'].grid(sticky='w')

        _row = 5
        self.__createVar('Player', False)
        _driverLabel = tk.Label(tkFrame_Status,
                                text='Driver')
        _driverLabel.grid(column=1,
                          row=_row,
                          sticky='e'
                          )
        self.driverLabel = tk.Entry(tkFrame_Status,
                                    state=tk.DISABLED,
                                    disabledforeground='black',
                                    textvariable=self.vars['Player'])
        self.driverLabel.grid(column=2,
                              row=_row,
                              sticky='w')

        self.__createVar('Status message', 'Status\nstat2\nstat3')
        self.statusText = tk.Text(tkFrame_Status,
                                  height=14,
                                  width=20,
                                  wrap=tk.WORD
                                  )
        self.statusText.grid(column=0,
                             columnspan=3,
                             sticky='nswe')
        status_poker = self.statusText.insert
        status_poker_scroll = self.statusText.see

        ####################################################
        # Kick off the tick
        self.info = sharedMemoryAPI.SimInfoAPI()
        if not self.info.isRF2running():
            self.statusText.insert(tk.END, 'rFactor 2 not running\n')
        self.__tick()

        ####################################################

    def __tick(self):
        """ Timed callback to update live status """
        if self.info.isRF2running():
            callback_time = 200
            self.vars['rF2 running'].set(True)
            self._leds['rF2 running'].set_colour('green')
            if not self.rFactor_running:
                if self.info.isSharedMemoryAvailable():
                    self.statusText.insert(tk.END, 'rFactor 2 running\n')
                    self.statusText.insert(
                        tk.END, self.info.versionCheck() + '\n')
                    self.rFactor_running = True
        else:
                    # Checking whether rFactor has started running is
                    # slow so don't check so frequently.
            callback_time = 2000
            self._leds['rF2 running'].set_colour('')
            if self.rFactor_running:
                self.statusText.insert(tk.END, 'rFactor 2 exited\n')
                self.rFactor_running = False
            self.vars['rF2 running'].set(False)
        self.vars['Shared memory working'].set(
            self.info.isSharedMemoryAvailable())
        self.vars['Track loaded'].set(self.info.isTrackLoaded())
        self.vars['On track'].set(self.info.isOnTrack())
        self.vars['Player'].set(self.info.driverName())
        # This duplicates the test HeadlightControl.esc_check()
        if not self.info.isOnTrack() or \
                self._timestamp < self.info.playersVehicleTelemetry().mElapsedTime:
            self.vars['Escape pressed'].set(False)
        else:
            self.vars['Escape pressed'].set(True)
        self._timestamp = self.info.playersVehicleTelemetry().mElapsedTime

        self.vars['AI driving'].set(self.info.isOnTrack() and
                                    self.info.isAiDriving())
        # self.parentFrame.update()
        self.parentFrame.after(callback_time, self.__tick)

    def __createVar(self, name, value):
        self.vars[name] = tk.StringVar(name=name)
        self.vars[name].set(value)

    def __createBoolVar(self, name, value):
        self.vars[name] = tk.BooleanVar(name=name)
        self.vars[name].set(value)

    class Led:
        """ Display a LED in any colour you fancy """

        def __init__(self, parent_frame):
            return  #pylint: disable=unreachable
            self.canvas = tk.Canvas(parent_frame, height=15, width=20)
            self.led = self.canvas.create_oval(5, 5, 15, 15)

        def set_colour(self, colour):
            """ Set the colour, e.g 'red'. '' is transparent """
            return
            self.canvas.itemconfig(
                self.led,
                fill=colour)

        def grid(self, **args):
            """ Pass on the tk grid() args """
            return
            self.canvas.grid(args)


def gui_main():
    """ Run the tab as a standalone frame """
    _root = tk.Tk()
    _root.title('%s' % (versionStr))
    tabConfigureFlash = ttk.Frame(
        _root, width=1200, height=1200, relief='sunken', borderwidth=5)
    tabConfigureFlash.grid()

    __o_tab = Tab(tabConfigureFlash)
    return _root, tabConfigureFlash


class Run:
    """ The external interface """
    controller_o = Controller()
    config_o = Config()
    xyPadding = 10
    pygame_event = None

    def tk_event_callback(self, _event):  # pylint: disable=no-self-use
        """ docstring """
        global tk_event  # pylint: disable=global-statement
        tk_event = _event

    def __init__(self, parentFrame, _root):
        """ Put this into the parent frame """
        self.root = _root
        self.parentFrame = parentFrame
        icon(self.root)
        _keyboard_control = False
        for name in headlight_controls:
            if self.config_o.get(name, 'Controller') == KEYBOARD:
                _keyboard_control = True
                break
        if _keyboard_control:
            pass  # self.root.bind('<KeyPress>', self.tk_event_callback)

    def pygame_callback(self, event):
        """ docstring """
        self.pygame_event = event
        # debug print(event) # This is called

    def running(self):
        """ docstring """
        global tk_event  # pylint: disable=global-statement
        tk_event = None
        self.pygame_event = None
        while True:  # pylint: disable=too-many-nested-blocks
            while not tk_event and not self.pygame_event:
                # Run pygame and tk to get latest input
                self.controller_o.pygame_tk_check(self.pygame_callback,
                                                  self.parentFrame)
            if tk_event:
                if tk_event == 'QUIT':
                    return 'QUIT'
                dik = KeycodeToDIK(tk_event.keycode)
                for cmd in headlight_controls:
                    if self.config_o.get(cmd, 'Controller') == KEYBOARD:
                        if dik == self.config_o.get(cmd, 'Control'):
                            return cmd
                tk_event = None
            if self.pygame_event:
                if self.pygame_event == 'QUIT':
                    return 'QUIT'
                if self.pygame_event == TIMER_EVENT:
                    return TIMER_EVENT
                try:
                    _button = str(self.pygame_event.button)
                    _joy = self.controller_o.controller_names[self.pygame_event.joy]
                    #print(_joy, _button)
                    for cmd in headlight_controls:
                        if self.config_o.get(cmd, 'Controller') == _joy:
                            if _button == self.config_o.get(cmd, 'Control'):
                                return cmd
                except BaseException:  # pylint: disable=bare-except
                    # not a joystick button
                    pass
                self.pygame_event = None
    def _get_controllers(self):
        return self.controller_o.controller_names


def run(_root, tabConfigureFlash):
    """ docstring """
    runWindow = tabConfigureFlash
    _o_run = Run(runWindow, _root)
    return _o_run


if __name__ == '__main__':
    # To run this tab by itself
    gui_main()
