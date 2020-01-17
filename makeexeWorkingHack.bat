::@echo off
setlocal

python -V | find "3.8"
if errorlevel 1 goto not38
::python -V
echo pyinstaller only works with versions up to 3.7
pause
goto :eof

:not38
rem set path=c:\Python36;c:\Python36\scripts;%path%
rem set path=%path%;"C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64"

pyinstaller -v
@echo.


if exist env\scripts 	echo Using env\scripts
if exist env\scripts 	set path=env\Scripts;%path%
if not exist env\scripts	python.exe -m venv env && env/Scripts/activate && python -m pip install -r requirements.txt

::   --debug=imports
::  --clean
::  --paths env\Lib\site-packages
::  --hidden-import pygame.base

pyinstaller ^
  --onefile ^
  --distpath . ^
  --paths env\lib\site-packages ^
  --exclude-module tests ^
  --exclude-module WindowsVersionFile ^
  --add-data resources\headlight.ico;. ^
  --icon resources\headlight.ico ^
  --noconsole  ^
  "%~dp0\rF2headlights.py "

pause

if not exist version.txt goto :pause
echo Setting version properties in rF2headlights.exe to version.txt
echo on
pyi-set_version version.txt rF2headlights.exe

echo Now to make debug version
pause

pyinstaller ^
  --onefile ^
  --distpath debug ^
  --paths env\lib\site-packages ^
  --exclude-module tests ^
  --exclude-module WindowsVersionFile ^
  --add-data resources\headlight.ico;. ^
  --icon resources\headlight.ico ^
  --debug=all  ^
  --name rF2headlightsDEBUG ^
  "%~dp0\rF2headlights.py "

:pause
pause

