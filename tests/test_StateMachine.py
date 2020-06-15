import unittest
from StateMachine import State
from StateMachine import StateMachine
from rF2headlights import HeadlightsState, HeadlightsAction
class MouseAction:
    def __init__(self, action):
        self.action = action
    def __str__(self): return self.action
    def __cmp__(self, other):
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)

# Static fields; an enumeration of events:
MouseAction.appears = MouseAction("mouse appears")
MouseAction.runsAway = MouseAction("mouse runs away")
MouseAction.enters = MouseAction("mouse enters trap")
MouseAction.escapes = MouseAction("mouse escapes")
MouseAction.trapped = MouseAction("mouse trapped")
MouseAction.removed = MouseAction("mouse removed")

# A different subclass for each state:

class Waiting(State):
    def run(self):
        print("Waiting: Broadcasting cheese smell")

    def next(self, input):
        if input == MouseAction.appears:
            return MouseTrap.luring
        return MouseTrap.waiting

class Luring(State):
    def run(self):
        print("Luring: Presenting Cheese, door open")

    def next(self, input):
        if input == MouseAction.runsAway:
            return MouseTrap.waiting
        if input == MouseAction.enters:
            return MouseTrap.trapping
        return MouseTrap.luring

class Trapping(State):
    def run(self):
        print("Trapping: Closing door")

    def next(self, input):
        if input == MouseAction.escapes:
            return MouseTrap.waiting
        if input == MouseAction.trapped:
            return MouseTrap.holding
        return MouseTrap.trapping

class Holding(State):
    def run(self):
        print("Holding: Mouse caught")

    def next(self, input):
        if input == MouseAction.removed:
            return MouseTrap.waiting
        return MouseTrap.holding

class MouseTrap(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, MouseTrap.waiting)

# Static variable initialization:
MouseTrap.waiting = Waiting()
MouseTrap.luring = Luring()
MouseTrap.trapping = Trapping()
MouseTrap.holding = Holding()

class Test_mouse_StateMachine(unittest.TestCase):
    def test_runAll(self):
        moves = ['mouse appears']
        x = map(MouseAction, moves)
        MouseTrap().runAll(x)

    def test_runOne(self):
        MouseTrap().runOne('mouse appears')
        print('OK')

class Test_headlights_StateMachine(unittest.TestCase):

    def test_headlights_runOne(self):
        hsm = HeadlightsState()
        next = hsm.runOne(HeadlightsAction.rfactor_running)
        self.assertEquals(next, HeadlightsState.rfactor_running)
        next = hsm.runOne(HeadlightsAction.E)
        self.assertEquals(next, HeadlightsState.rfactor_running)


if __name__ == '__main__':
    unittest.main()
