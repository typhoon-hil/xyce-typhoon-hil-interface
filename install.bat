@ECHO off

set path_to_this_folder=%~dp0\
setx /M TYPHOON_XYCE_INTERFACE "%path_to_this_folder%"
IF %ERRORLEVEL% NEQ 0 (ECHO Make sure you are running this batch script in Administrator mode.) ELSE (ECHO Installation sucessful.)
pause