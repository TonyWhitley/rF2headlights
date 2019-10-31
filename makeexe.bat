@echo off
setlocal
set _env=env
call pyInstallerSetup %_env%

::   --debug=imports
::  --clean
::  --paths env\Lib\site-packages
::  --hidden-import pygame.base


rem  --exclude-module tests ^
rem  --exclude-module WindowsVersionFile ^
rem --icon doesn't seem to do anything
rem --noconsole removes the console in the background but for now
rem             it's best to keep it for error messages

pyinstaller ^
  --onefile ^
  --distpath . ^
  --add-data resources\headlight.ico;. ^
  --icon resources\headlight.ico ^
  --paths %_env%\Lib\site-packages ^
  --paths %_env% ^
  --debug all  ^
  "%~dp0\rF2headlights.py"

if exist version.txt pyi-set_version version.txt rF2headlights.exe
pause

