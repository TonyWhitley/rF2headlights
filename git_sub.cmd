echo git bash commands to load submodules
rem Automated login
git config --global credential.helper wincred
git init

rmdir --ignore-fail-on-non-empty pyDirectInputKeySend
git submodule add -f https://github.com/TonyWhitley/pyDirectInputKeySend                                                 
rmdir --ignore-fail-on-non-empty pyRfactor2SharedMemory
git submodule add -f https://github.com/TonyWhitley/pyRfactor2SharedMemory                               
rmdir --ignore-fail-on-non-empty WindowsVersionFile
git submodule add -f https://github.com/TonyWhitley/WindowsVersionFile                               
