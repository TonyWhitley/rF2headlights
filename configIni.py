from configparser import ConfigParser
import os

configFileName = 'headlightControls.ini'
sections = ['Toggle headlights',
            'Flash headlights',
            'Headlights on',
            'Headlights off',
            'rFactor Toggle']
miscValues = {
  'pit_limiter'     : '1',    # 1: flash headlights when pit limiter on
  'pit_lane'        : '1',    # 1: flash headlights when in pit lane
  }


class Config:
  def __init__(self):
    # instantiate
    self.config = ConfigParser()

    # set default values
    for section in sections:
        self.set(section, 'Controller', 'Not yet selected')
        self.set(section, 'Control', '0')
    for val, default in miscValues.items():
        self.set('miscellaneous', val, default)
    
    # if there is an existing file parse values over those
    if os.path.exists(configFileName):
      self.config.read(configFileName)
    else:
      self.write()
      # then configure the controller(s)
      from gui import main
      main()
      self.config.read(configFileName)

  def set(self, section, val, value):
    # update existing value
    if not self.config.has_section(section):
      self.config.add_section(section)
    self.config.set(section, val, value)

  def get(self, section, val):
    try:
      # get existing value
      return self.config.get(section, val)
      if val in ['controller'] :
        return self.config.get(section, val)
      else:
        return self.config.getint(section, val)
    except: # No such section in file
      self.set(section, val, '')
      return None

  def write(self):
    # save to a file
    with open(configFileName, 'w') as configfile:
        self.config.write(configfile)

if __name__ == "__main__":
  _config_o = Config()
  section = 'headlight controls'
  val = 'controller'
  value = _config_o.get(section, val)
  if value:
    if val == 'controller':
      print('%s/%s: %s' % (section, val, value))
    else:
      print('%s/%s: %d' % (section, val, value))
  else:
    print('%s/%s: <None>' % (section, val))
  _config_o.write()
