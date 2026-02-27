@echo off
REM Launch the SQL Compare GUI
python "%~dp0sql_compare.py" %*
if %ERRORLEVEL% NEQ 0 pause
