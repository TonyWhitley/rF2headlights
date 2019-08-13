"""
Set values in headlightControls.ini to configure headlight controls
"""
# pylint: disable=invalid-name
# pylint: disable=ad-indentation

BUILD_REVISION = 14 # The git commit count
versionStr = 'Headlight Controls Configurer V0.1.%d' % BUILD_REVISION
versionDate = '2019-08-13'

# Python 3
import tkinter as tk
from tkinter import ttk
import tkinter.font as font 

from configIni import Config
from wheel import Controller

headlight_controls = {
  'Toggle headlights'   : {
      'tkButton':None,
      'tkLabel':None,
      'ControllerName':None,
      'svControllerName':None,
      'svControl':None,
      },
  'Flash headlights'    : {
      'tkButton':None,
      'tkLabel':None,
      'ControllerName':None,
      'svControllerName':None,
      'svControl':None,
      },
  'Headlights on'       : {
      'tkButton':None,
      'tkLabel':None,
      'ControllerName':None,
      'svControllerName':None,
      'svControl':None,
      },
  'Headlights off'      : {
      'tkButton':None,
      'tkLabel':None,
      'ControllerName':None,
      'svControllerName':None,
      'svControl':None,
      }
  }

rfactor_headlight_control = {
  'rFactor Toggle' : {
      'tkButton':None,
      'tkLabel':None,
      'ControllerName':None,
      'svControllerName':None,
      'svControl':None,
      }
  }

tk_event = None
root = None

#########################
# The tab's public class:
#########################
class Tab:
  parentFrame = None
  controller_o = Controller()
  config_o = Config()
  root = None
  xyPadding = 10
  
  def tk_event_callback(self, _event):
    global tk_event
    tk_event = _event

  def __init__(self, parentFrame, root):
    """ Put this into the parent frame """
    self.root = root
    self.parentFrame = parentFrame
    root.bind('<KeyPress>', self.tk_event_callback)

    self.headlight_controls_o = headlightControlsFrame(self.parentFrame)
    self.headlight_controls_o.tkFrame_headlight_control.grid(column=0, row=2, sticky='new', padx=self.xyPadding, rowspan=2)
    
    self.rf_headlight_control_o = rFactorHeadlightControlFrame(self.parentFrame)
    self.rf_headlight_control_o.tkFrame_headlight_control.grid(column=1, row=2, sticky='new', padx=self.xyPadding, rowspan=2)

    #############################
    buttonFont = font.Font(weight='bold', size=10)

    self.tkButtonSave = tk.Button(
        parentFrame,
        text="Save configuration",
        width=20,
        height=2,
        background='green',
        font=buttonFont,
        command=self.save)
    self.tkButtonSave.grid(column=1, row=4, pady=25)
    #############################

    self.controller_o.run(self.tk_event_callback, parentFrame)

  def save(self):
    self.headlight_controls_o.save()
    self.rf_headlight_control_o.save()
    self.config_o.write()

  def getSettings(self):
    """ Return the settings for this tab """
    return ['Options']

  def setSettings(self, settings):
    """ Set the settings for this tab """
    pass

class ControlFrame(Tab):
  """ Generic frame with a list of controls """
  tkFrame_headlight_control = None
  def __init__(self, parentFrame, _headlight_controls):
    global root

    self.parentFrame = parentFrame
    self.headlight_controls = _headlight_controls
    self.tkFrame_headlight_control = tk.LabelFrame(parentFrame,
                                                   text='rFactor Headlight Control',
                                                   padx=self.xyPadding,
                                                   pady=self.xyPadding)

    tk.Label(self.tkFrame_headlight_control,
             text="Controller").grid(row=0, column=1)
    tk.Label(self.tkFrame_headlight_control,
             text="Control").grid(row=0, column=2)

    ##########################################################
    for _control_num, (name, control) in enumerate(self.headlight_controls.items()):
      _control_line = self.headlight_controls[name]
      ##########################################################
      _control_line['tkButton'] = tk.Button(self.tkFrame_headlight_control,
                                            text='Select ' + name,
                                            width=20,
                                            command=lambda n=name,
                                            w=super().controller_o: self.set_control(n,w))
      _control_line['tkButton'].grid(row = _control_num+2,
                                     sticky='w',
                                     pady=3)
      ##########################################################
      _control_line['svControllerName'] = tk.StringVar()
      _control_line['svControllerName'].set(super().config_o.get(name, 'Controller'))
      _control_line['ControllerName'] = tk.Label(self.tkFrame_headlight_control,
                                                textvariable=control['svControllerName'],
                                                fg='SystemInactiveCaptionText',
                                                relief=tk.GROOVE,
                                                borderwidth=4,
                                                anchor='e',
                                                padx=4)
      _control_line['ControllerName'].grid(row = _control_num+2,
                                           column=1,
                                           sticky='w')
      ##########################################################
      _control_line['svControl'] = tk.StringVar()
      _control_line['svControl'].set(super().config_o.get(name, 'Control'))
      _control_line['tkLabel'] = tk.Label(self.tkFrame_headlight_control,
                                          textvariable=control['svControl'],
                                          fg='SystemInactiveCaptionText',
                                          relief=tk.GROOVE,
                                          width=1,
                                          borderwidth=4,
                                          anchor='e',
                                          padx=4)
      _control_line['tkLabel'].grid(row=_control_num+2,
                                    column=2,
                                    sticky='w')

  def pygame_callback(self, event):
     """ docstring """
     #print(event)
     self.pygame_event = event

  def set_control(self, name, controller_o):
    """ docstring """
    global tk_event
    tk_event = None
    self.pygame_event = None
    while not tk_event and not self.pygame_event:
        # Run pygame and tk to get latest input
        controller_o.pygame_tk_check(self.pygame_callback, self.parentFrame)
    if tk_event:
        self.headlight_controls[name]['svControl'].set(tk_event.char)
        self.headlight_controls[name]['tkLabel'].configure(text=str(tk_event.char))
        self.headlight_controls[name]['ControllerName'].configure(text='keyboard')
        self.headlight_controls[name]['svControllerName'].set('keyboard')
        return tk_event.char
    if self.pygame_event:
        _button = self.pygame_event.button
        _joy = controller_o.controllerNames[self.pygame_event.joy]
        self.headlight_controls[name]['svControl'].set(_button)
        self.headlight_controls[name]['tkLabel'].configure(text=str(_button))
        self.headlight_controls[name]['ControllerName'].configure(text=_joy)
        self.headlight_controls[name]['svControllerName'].set(_joy)
        return _button

  def save(self):
    for name, control in self.headlight_controls.items():
        self.config_o.set(name, 'Controller', control['svControllerName'].get())
        self.config_o.set(name, 'Control', control['svControl'].get())

class rFactorHeadlightControlFrame(ControlFrame):
    """ docstring """
    def __init__(self, parentFrame):
        super().__init__(parentFrame, rfactor_headlight_control)
        ##########################################################
        self._separator = ttk.Separator(self.tkFrame_headlight_control,
                                        orient="horizontal")
        self._separator.grid(row=3,
                             column=0,
                             sticky="we",
                             columnspan=2)
        ##########################################################
        self.pit_limiter = tk.IntVar()
        self.tkCheckbutton_pitLimiter = tk.Checkbutton(self.tkFrame_headlight_control,
                                                       var=self.pit_limiter,
                                                       text='Flash when pit limiter')

        self.tkCheckbutton_pitLimiter.grid(sticky='w',
                                           columnspan=2)
        x = self.config_o.get('miscellaneous', 'pit_limiter')
        if not x:
            x = 0
        self.pit_limiter.set(x)

        ##########################################################
        self.pit_lane = tk.IntVar()
        self.tkCheckbutton_pitLane = tk.Checkbutton(self.tkFrame_headlight_control,
                                                    var=self.pit_lane,
                                                    text='Flash when in pit lane')

        self.tkCheckbutton_pitLane.grid(sticky='w',
                                        columnspan=2)
        x = self.config_o.get('miscellaneous', 'pit_lane')
        if not x:
            x = 0
        self.pit_lane.set(x)

    def save(self):
        super().save()
        self.config_o.set('miscellaneous', 'pit_limiter', str(self.pit_limiter.get()))
        self.config_o.set('miscellaneous', 'pit_lane', str(self.pit_lane.get()))

class headlightControlsFrame(ControlFrame):
    """ docstring """
    def __init__(self, parentFrame):
        super().__init__(parentFrame, headlight_controls)

def main():
    """ docstring """
    _root = tk.Tk()
    _root.title('%s' % (versionStr))
    tabOptions = ttk.Frame(root, width=1200, height=1200, relief='sunken', borderwidth=5)
    tabOptions.grid()

    __o_tab = Tab(tabOptions, _root)
    #root.mainloop()

if __name__ == '__main__':
    # To run this tab by itself for development
    main()
