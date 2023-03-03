@echo off
 
if not "%~0"=="%~dp0.\%~nx0" (
     start /min cmd /c,"%~dp0.\%~nx0" %*
     exit
)

cd %~dp0
cd kirameki\WPy64-39100\scripts
python %~dp0\kirameki\setting-gui.py
