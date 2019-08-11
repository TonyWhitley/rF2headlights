# Set values in headlightControls.ini to configure headlight controls

BUILD_REVISION = 33 # The git commit count
versionStr = 'Headlight Controls Configurer V0.1.%d DEBUG' % BUILD_REVISION
versionDate = '2019-08-11'

# Python 3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as font 

from configIni import Config
from wheel import Controller

headlight_controls = {
                #tkButton, 
                      #tkLabel, 
                            #tkStringVar, 
                                  #JoystickButton
  'Toggle'   : [None, None, None, 8],
  'Flash'    : [None, None, None, 9],
  'On'       : [None, None, None, 10],
  'Off'      : [None, None, None, 11]
  }

rfactor_headlight_control = {
                #tkButton, 
                      #tkLabel, 
                            #tkStringVar, 
                                  #JoystickButton
  'Toggle'      : [None, None, None, 8]
  }

#########################
# The tab's public class:
#########################
class Tab:
  parentFrame = None
  controller_o = Controller()
  config_o = Config()
  xyPadding = 10

  def dummy(self):
    pass

  def __init__(self, parentFrame):
    """ Put this into the parent frame """
    self.parentFrame = parentFrame

    self.headlight_controls_o = headlightControlsFrame(self.parentFrame)
    self.headlight_controls_o.tkFrame_headlight_controls.grid(column=0, row=2, sticky='new', padx=self.xyPadding, rowspan=2)
    
    self.rf_headlight_control_o = rFactorHeadlightControlFrame(self.parentFrame)
    self.rf_headlight_control_o.tkFrame_rfactor_headlight_control.grid(column=1, row=2, sticky='new', padx=self.xyPadding, rowspan=2)

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

    self.controller_o.run(self.dummy, parentFrame)

  def controllerChoice(self, parent, tkvar):
    # List with options
    choices = self.controller_o.controllerNames

    tkvar.set(choices[0]) # set the default option
 
    popupMenu = tk.OptionMenu(parent, tkvar, *choices)
    tk.Label(parent, text="Choose a controller").grid(row = 0, column = 0)
    popupMenu.grid(row=0, column=1)
 
    #############################
    # on change dropdown value
    def change_dropdown(*args):
        name = tkvar.get()
        #self.controller_o.del()
        self.controller_o.selectController(name)

    # link function to change dropdown
    tkvar.trace('w', change_dropdown)

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

class headlightControlsFrame(Tab):
  tkFrame_headlight_controls = None
  def __init__(self, parentFrame):
    self.tkFrame_headlight_controls = tk.LabelFrame(parentFrame, text='Headlight Controls', padx=self.xyPadding,  pady=self.xyPadding)

    # Create a Tkinter variable
    self.headlight_controls_Controller = tk.StringVar(parentFrame)

    self.controllerChoice(self.tkFrame_headlight_controls, self.headlight_controls_Controller)

    ##########################################################
    for _control, (name, control) in enumerate(headlight_controls.items()):
      headlight_controls[name][0] = tk.Button(self.tkFrame_headlight_controls, text='Select ' + name, width=12, 
                                 command=lambda n=name, w=super().controller_o: self.set_control(n,w))
      headlight_controls[name][0].grid(row = _control+2, sticky='w', pady=3)
      control[3] = super().config_o.get('headlight controls', name)
      headlight_controls[name][1] = tk.Label(self.tkFrame_headlight_controls, 
                                text=control[3], fg = 'SystemInactiveCaptionText',
                                relief=tk.GROOVE, width=1,
                                borderwidth=4, anchor='e', padx=4)
      headlight_controls[name][1].grid(row = _control+2, column=1, sticky='w')
      headlight_controls[name][2] = tk.StringVar()
    for name, control in headlight_controls.items():
      control[2].set(super().config_o.get('headlight controls', name))

    self.headlight_controls_Controller.set(super().config_o.get('headlight controls', 'controller'))

  def set_control(self, name, controller_o):
    messagebox.showinfo('', 'Press the control for %s then press OK' % name)
    # Run pygame and tk to get latest input
    controller_o.pygame_tk_check(self.dummy, self.parentFrame)
    for g in range(controller_o.num_buttons):
      if controller_o.getButtonState(g) == 'D':
        headlight_controls[name][2].set(g)
        headlight_controls[name][1].configure(text=str(g))
        return g
    messagebox.showerror('No control pressed', 'Input not changed')
  def save(self):
    self.config_o.set('headlight controls','controller', self.headlight_controls_Controller.get())
    for name, control in headlight_controls.items():
      self.config_o.set('headlight controls', name, control[2].get())

class rFactorHeadlightControlFrame(Tab):
  tkFrame_rfactor_headlight_control = None
  def __init__(self, parentFrame):
    self.tkFrame_rfactor_headlight_control = tk.LabelFrame(parentFrame, text='rFactor Headlight Control', padx=self.xyPadding,  pady=self.xyPadding)

    # Create a Tkinter variable
    self.headlight_controls_Controller = tk.StringVar(parentFrame)

    #tbd Controller choice includes keyboard
    self.controllerChoice(self.tkFrame_rfactor_headlight_control, self.headlight_controls_Controller)

    ##########################################################
    for _control, (name, control) in enumerate(rfactor_headlight_control.items()):

      headlight_controls[name][0] = tk.Button(self.tkFrame_rfactor_headlight_control, text='Select ' + name, width=12, 
                                 command=lambda n=name, w=super().controller_o: self.set_control(n,w))
      headlight_controls[name][0].grid(row = _control+2, sticky='w', pady=3)
      control[3] = super().config_o.get('rfactor headlight control', name)
      headlight_controls[name][1] = tk.Label(self.tkFrame_rfactor_headlight_control, 
                                text=control[3], fg = 'SystemInactiveCaptionText',
                                relief=tk.GROOVE, width=1,
                                borderwidth=4, anchor='e', padx=4)
      headlight_controls[name][1].grid(row = _control+2, column=1, sticky='w')
      headlight_controls[name][2] = tk.StringVar()
    for name, control in headlight_controls.items():
      control[2].set(super().config_o.get('rfactor headlight control', name))

    self.headlight_controls_Controller.set(super().config_o.get('rfactor headlight control', 'controller'))

    ##########################################################
    self._separator = ttk.Separator(self.tkFrame_rfactor_headlight_control, orient="horizontal")
    self._separator.grid(row=3, column=0, sticky="we", columnspan=2)
    ##########################################################
    self.pit_limiter = tk.IntVar()
    self.tkCheckbutton_GearClutchDamage = tk.Checkbutton(self.tkFrame_rfactor_headlight_control, 
                                                         var=self.pit_limiter,
                                                         text='Flash when pit limiter')

    self.tkCheckbutton_GearClutchDamage.grid(sticky='w', columnspan=2)
    x = self.config_o.get('miscellaneous', 'pit_limiter')
    if not x:
      x = 0
    self.pit_limiter.set(x)

    ##########################################################
    self.pit_lane = tk.IntVar()
    self.tkCheckbutton_GearClutchDamage = tk.Checkbutton(self.tkFrame_rfactor_headlight_control, 
                                                         var=self.pit_lane,
                                                         text='Flash when in pit lane')

    self.tkCheckbutton_GearClutchDamage.grid(sticky='w', columnspan=2)
    x = self.config_o.get('miscellaneous', 'pit_lane')
    if not x:
      x = 0
    self.pit_lane.set(x)

  def set_control(self, name, controller_o):
    messagebox.showinfo('', 'Press the control for %s then press OK' % name)
    # Run pygame and tk to get latest input
    controller_o.pygame_tk_check(self.dummy, self.parentFrame)
    for g in range(controller_o.num_buttons):
      if controller_o.getButtonState(g) == 'D':
        rfactor_headlight_control[name][2].set(g)
        rfactor_headlight_control[name][1].configure(text=str(g))
        return g
    messagebox.showerror('No control pressed', 'Input not changed')
  def save(self):
    self.config_o.set('rfactor headlight control','controller', self.headlight_controls_Controller.get())
    for name, control in rfactor_headlight_control.items():
      self.config_o.set('rfactor headlight control', name, control[2].get())
  
def main():
  root = tk.Tk()
  root.title('%s' % (versionStr))
  tabOptions = ttk.Frame(root, width=1200, height=1200, relief='sunken', borderwidth=5)
  tabOptions.grid()
    
  o_tab = Tab(tabOptions)
  root.mainloop()

if __name__ == '__main__':
  # To run this tab by itself for development
  main()