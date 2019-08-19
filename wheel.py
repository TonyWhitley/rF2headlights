# G25 wheel class

import locale
import sys
import pygame

"""
G25 Axes:
  0 -ve      Left
  0 +ve      Right
  1          ???
  2 1 -> -1  Accelerator
  3 1 -> -1  Brake
  4 1 -> -1  Clutch
"""


class Controller:
    """ docstring """
    error_string = ''
    error = False
    num_controllers = 0
    num_buttons = 0
    num_axes = 0
    controller_names = []
    controller_name = None
    controller = None

    def get_name(self, controller):
        """
        pygame's get_name() can give an exception "invalid utf-8 character"
        """
        _name = 'Error getting controller name'
        try:
            _name = controller.get_name()
            # _name = 'Logitech® G27 Shifter' # DEBUG 2
            # print('DEBUG pygame version: %s' % pygame.version.ver)
        except UnicodeError as _e:
            print('Default locale')  # DEBUG
            print(_e.object.decode(locale.getdefaultlocale()[1]))  # DEBUG
            _name = 'Unicode error getting controller name'
        except: # pylint: disable=bare-except
            _name = 'Other error getting controller name'
            print("Unexpected error:", sys.exc_info()[0])
        return _name.strip()  # e.g. strip spaces from "usb gamepad   "

    def __init__(self):
        pygame.init()
        # pygame.display.set_mode(size=(1,1))
        pygame.event.set_blocked(pygame.MOUSEMOTION)  # Don't want mouse events
        self.num_controllers = pygame.joystick.get_count()
        if self.num_controllers < 1:
            self.error_string = 'No Controllers'
            self.error = True
            return

        self.controller_names = []
        for j in range(self.num_controllers):
            _j = pygame.joystick.Joystick(j)
            _j.init()
            self.controller_names.append(self.get_name(_j))

    def start_pit_check_timer(self):
        """
        Start a one second timer to check for pit entry and / or
        pit limiter being turned on
        """
        pygame.time.set_timer(pygame.USEREVENT+1, 1000) # Every second

    def select_controller(self, controller_name):
        """ docstring """
        self.controller = pygame.joystick.Joystick(0)  # fallback value
        for j in range(self.num_controllers):
            _j = pygame.joystick.Joystick(j)
            if self.get_name(_j) == controller_name:
                self.controller = pygame.joystick.Joystick(j)

        # self.controller.init()
        self.num_axes = self.controller.get_numaxes()
        self.num_buttons = self.controller.get_numbuttons()
        self.controller_name = self.controller.get_name().strip()
        if self.controller_name != controller_name:
            self.error_string = 'Controller is "%s" not "%s"' % (
                self.controller_name, controller_name)
            self.error = True
            return

    def get_axis(self, axis):
        """ return 100 clutch released, 0 clutch pressed """
        axis_value = self.controller.get_axis(axis)
        # 1 is released, -1 is pressed
        return int((axis_value * 50)) + 50

    def get_button_state(self, button_number):
        """ docstring """
        state = self.controller.get_button(button_number)
        if state:
            result = 'D'
        else:
            result = 'U'
        return result

    def pygame_tk_check(self, callback, tk_main_dialog=None):
        """ Run pygame and tk to get latest events """
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                callback('QUIT')
            # Possible controller actions: JOYAXISMOTION JOYBALLMOTION
            #                              JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYAXISMOTION:
                # ignore callback(event)
                pass
            if event.type == pygame.JOYBUTTONDOWN:
                callback(event)
            if event.type == pygame.JOYBUTTONUP:
                # ignore callback(event)
                pass
            if event.type == pygame.KEYDOWN:
                callback(event)
            if event.type == pygame.USEREVENT+1:
                callback('TIMER_EVENT')
        if tk_main_dialog:  # Tk is running as well
            try:
                tk_main_dialog.update()
            except: # pylint: disable=bare-except
                # tk_main_dialog has been destroyed.
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT))
        return True

    def run(self, callback, tk_main_dialog=None):
        """ Run pygame and tk event loops """
        while self.pygame_tk_check(callback, tk_main_dialog):
            pass
