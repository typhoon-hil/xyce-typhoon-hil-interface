@ECHO off

setlocal EnableDelayedExpansion

ECHO:
ECHO ---------------------------------------------------------------------------
ECHO Installing / updating the xyce-typhoon-hil-interface files...


set version_file=""

FOR /F "delims=;" %%A IN ("%TYPHOONPATH%") DO (
      set version_file=%%A\.version
   )

set /p c_version= < !version_file!

IF "!c_version!" ==  "" (
ECHO ---------------------------------------------------------------------------
ECHO No compatible Typhoon HIL Control Center version was found.
goto :eof
)

set c_version="!c_version!"

ECHO:
ECHO The library will be copied to the latest Typhoon HIL Control Center version found: !c_version!
ECHO:

pause

ECHO:
ECHO ---------------------------------------------------------------------------
ECHO Copying the converter files and library...
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

ECHO Files copied sucessfully.

ECHO:
ECHO ---------------------------------------------------------------------------
ECHO Setting the TYPHOON_XYCE_INTERFACE user environment variable...

setx TYPHOON_XYCE_INTERFACE "%appdata_folder%\xyce-typhoon-hil-interface"
IF %ERRORLEVEL% NEQ 0 (
ECHO ---------------------------------------------------------------------------
ECHO The environment variable could not be set.
ECHO There was a problem with the installation.
ECHO:

) ELSE (
ECHO:
ECHO ---------------------------------------------------------------------------
ECHO Installation complete.
ECHO:
)

pause
