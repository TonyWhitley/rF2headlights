import json
import os

def read_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()
    return None # File not found

class Json:
    def __init__(self, filepath):
        self.json_str = read_file(filepath)
        self.dict = json.loads(self.json_str)

    def get_item(self, item_name):
        for section, items in self.dict.items():
            if item_name in items:
                value = items[item_name]
                return value
        return ''

if __name__ == "__main__":
    # Test
    from configIni import Config
    from pyDirectInputKeySend.directInputKeySend import rfKeycodeToDIK
    _CONFIG_O = Config()
    _controller_file = _CONFIG_O.get_controller_file()
    _JSON_O = Json(_controller_file)
    headlight_control = _JSON_O.get_item("Control - Headlights")
    print(F'headlight_control: {headlight_control}')
    keycode = rfKeycodeToDIK(headlight_control[1])
    rf2headlights_keycode = _CONFIG_O.get('rFactor Toggle', 'Control')
    if keycode == rf2headlights_keycode:
        print(F'Match: {keycode}')
    else:
        print(F"Doesn't match: rF2 keycode {keycode} : rf2headlights keycode {rf2headlights_keycode}")

