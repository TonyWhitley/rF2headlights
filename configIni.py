""" docstring """
from configparser import ConfigParser
import os

CONFIG_FILE_NAME = 'headlightControls.ini'
SECTIONS = [
    'Toggle headlights',
    'Flash headlights',
    'Headlights on',
    'Headlights off',
    'rFactor Toggle',
]
MISC_VALUES = {
    'pit_limiter': '1',  # 1: flash headlights when pit limiter on
    'pit_lane': '1',     # 1: flash headlights when in pit lane
}


class Config:
    """ docstring """
    def __init__(self):
        # instantiate
        self.config = ConfigParser()

        # set default values
        for _section in SECTIONS:
            self.set(_section, 'Controller', 'Not yet selected')
            self.set(_section, 'Control', '0')
        for _val, default in MISC_VALUES.items():
            self.set('miscellaneous', _val, default)

        # if there is an existing file parse values over those
        if os.path.exists(CONFIG_FILE_NAME):
            self.config.read(CONFIG_FILE_NAME)
        else:
            self.write()
            # then configure the controller(s)
            from gui import main

            main()
            self.config.read(CONFIG_FILE_NAME)

    def set(self, _section, _val, _value):
        """ update existing value """
        if not self.config.has_section(_section):
            self.config.add_section(_section)
        self.config.set(_section, _val, _value)

    def get(self, _section, _val):
        """ get a config value """
        try:
            # get existing value
            return self.config.get(_section, _val)
        except:  # pylint: disable=bare-except
            # No such section in file
            self.set(_section, _val, '')
            return None

    def write(self):
        """ save to a file """
        with open(CONFIG_FILE_NAME, 'w') as configfile:
            self.config.write(configfile)


if __name__ == "__main__":
    _CONFIG_O = Config()
    SECTION = 'headlight controls'
    VAL = 'controller'
    VAL = _CONFIG_O.get(SECTION, VAL)
    if VAL:
        if VAL == 'controller':
            print('%s/%s: %s' % (SECTION, VAL, VAL))
        else:
            print('%s/%s: %d' % (SECTION, VAL, VAL))
    else:
        print('%s/%s: <None>' % (SECTION, VAL))
    _CONFIG_O.write()
