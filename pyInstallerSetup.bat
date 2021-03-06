@echo on

if '%1' == '' goto noEnv
setlocal
set env=%1

set path=c:\Python36;c:\Python36\scripts;%path%
set path=%path%;C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64

if exist %env%\scripts goto envReady
echo Installing virtual env "%env%"
python -m pip install -r requirements.txt

:envReady
echo Using %env%\scripts
set path=%env%\Scripts;%path%
python.exe -m venv %env%
call %env%\Scripts\activate

python -V | find "3.7"
if errorlevel 1 goto not37
python -V
echo pyinstaller only works with versions up to 3.6
pause
goto :eof

:noEnv
echo Virtual environment must be specified
echo e.g.  %~n0 env
pause
goto :eof

:not37
if exist %env%\Lib\site-packages\enum echo enum is present and has been seen to break pyinstaller
goto :eof
