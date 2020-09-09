@ECHO off

setlocal EnableDelayedExpansion

set c_version=""
IF EXIST "%appdata%/typhoon/2019.4" (set c_version=2019.4)
IF EXIST "%appdata%/typhoon/2019.4 SP1" (set c_version=2019.4 SP1)
IF EXIST "%appdata%/typhoon/2019.4 SP2" (set c_version=2019.4 SP2)
IF EXIST "%appdata%/typhoon/2019.4" (set c_version=2020.1)
IF EXIST "%appdata%/typhoon/2019.4 SP1" (set c_version=2020.1SP1)
IF EXIST "%appdata%/typhoon/2019.4 SP2" (set c_version=2020.1 SP2)
IF EXIST "%appdata%/typhoon/2020.2" (set c_version=2020.2)
IF %c_version%=="" (ECHO No compatible Typhoon HIL Control Center installation found. Make sure to run the Typhoon Schematic Editor once before running this installation script. & pause & exit)

cd "%~dp0"
set path_to_this_folder=%~dp0\
set appdata_folder=%appdata%
set path_to_userlibs=%appdata%\typhoon\%c_version%\user-libs
echo %~dp0
xcopy /E /I "%path_to_this_folder:~0,-2%\gui" "%appdata_folder%\xyce-typhoon-hil-interface\gui"
xcopy /E /I "%path_to_this_folder:~0,-2%\libs" "%appdata_folder%\xyce-typhoon-hil-interface\libs"
xcopy /E /I "%path_to_this_folder:~0,-2%\schematic_converter" "%appdata_folder%\xyce-typhoon-hil-interface\schematic_converter"
xcopy "%path_to_this_folder:~0,-2%\__init__.py" "%appdata_folder%\xyce-typhoon-hil-interface"
xcopy "%path_to_this_folder:~0,-2%\libs\xyce.tlib" "%path_to_userlibs%"
xcopy /E /I "%path_to_this_folder:~0,-2%\libs\Xyce" "%path_to_userlibs%\Xyce"
setx TYPHOON_XYCE_INTERFACE "%appdata_folder%\xyce-typhoon-hil-interface"
IF %ERRORLEVEL% NEQ 0 (ECHO There was a problem with the installation.) ELSE (ECHO Installation sucessful.)
pause