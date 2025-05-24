@echo off
REM Set the paths for the NiceGUI resources
REM set NICEGUI_STATIC="D:\yahia\Desktop\Debt Tracking System\.venv\Lib\site-packages\nicegui\static\sad_face.svg;nicegui/static"
REM set NICEGUI_TEMPLATES="D:\yahia\Desktop\Debt Tracking System\.venv\Lib\site-packages\nicegui\templates;nicegui/templates"
set NICE_GUI="D:\yahia\Desktop\Debt Tracking System\.venv\Lib\site-packages\nicegui;nicegui"

REM Set the path to the script
set SCRIPT_PATH="D:/yahia/Desktop/Debt Tracking System/Launcher.py"

REM Run pyinstaller with the required options
pyinstaller --noconfirm --onefile --add-data %NICE_GUI% --console %SCRIPT_PATH%

pause
