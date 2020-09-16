@ECHO off

setlocal EnableDelayedExpansion

ECHO Installing / updating the xyce-typhoon-hil-interface files

set c_version="2020.2"

cd "%~dp0"
set path_to_this_folder=%~dp0\
set appdata_folder=%appdata%
set path_to_userlibs="%appdata%\typhoon\%c_version%\user-libs"
set path=%path%;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\
xcopy /E /I /Y "%path_to_this_folder:~0,-2%\gui" "%appdata_folder%\xyce-typhoon-hil-interface\gui" > NUL
xcopy /E /I /Y "%path_to_this_folder:~0,-2%\libs" "%appdata_folder%\xyce-typhoon-hil-interface\libs" > NUL
xcopy /E /I /Y "%path_to_this_folder:~0,-2%\schematic_converter" "%appdata_folder%\xyce-typhoon-hil-interface\schematic_converter" > NUL
xcopy /Y "%path_to_this_folder:~0,-2%\libs\Xyce.tlib" "%path_to_userlibs%\" > NUL
xcopy /Y "%path_to_this_folder:~0,-2%\__init__.py" "%appdata_folder%\xyce-typhoon-hil-interface\" > NUL
xcopy /E /I /Y "%path_to_this_folder:~0,-2%\libs\Xyce" "%path_to_userlibs%\Xyce" > NUL

setx TYPHOON_XYCE_INTERFACE "%appdata_folder%\xyce-typhoon-hil-interface"
IF %ERRORLEVEL% NEQ 0 (ECHO There was a problem with the installation.) ELSE (ECHO Files copied sucessfully.)

sleep 2
