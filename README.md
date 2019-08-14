# rF2headlights
Flash the headlights in rFactor 2 when a button is pressed.
Also offers controls to turn headlights on or off, regardless of whether they are on at the time (as opposed to rFactor's control which just toggles them).
Also can flash when pit limiter on and flash when in pit lane.

It reads the shared memory to find whether the lights are on or off prior to flashing them.  As the headlight control is a toggle it reads it again to check they are in the same state afterwards in case a command was missed.

