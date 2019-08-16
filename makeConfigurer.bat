@echo off

call pyInstallerSetup env

::   --debug=imports 
::  --clean 
::  --paths env\Lib\site-packages 
::  --hidden-import pygame.base 

rem --icon doesn't seem to do anything
rem --noconsole removes the console in the background but for now
rem             it's best to keep it for error messages
pyinstaller ^
  --onefile ^
  --distpath . ^
  --name rF2headlightsConfigurer ^
  --add-data resources\headlight.ico;. ^
  --icon resources\headlight.ico ^
  "%~dp0\gui.py "
pause

