::
:: This script assumes it has been run from the top level directory
:: as .\bin\build_model.bat
::
@echo off

::
:: determining toplevel of repository using git if possible
:: defaults to the current working directory
::
set REPO_HOME=.
set USE_GIT=
:: first checking that git command exists
where git >nul 2>nul
if /I "%errorlevel%" == "0" (
    set USE_GIT=yes
    git rev-parse --show-toplevel >nul 2>nul
)
:: checking if directory is actually a repository
if DEFINED USE_GIT (
    if /I "%errorlevel%" NEQ "0" (
        set USE_GIT=
    )
)
if DEFINED USE_GIT (
    for /f %%i in ('git rev-parse --show-toplevel') do set REPO_HOME=%%i
)

::
:: building flow model from source
cd "%REPO_HOME%"
if NOT EXIST "source\dist" (
    mkdir "source\dist"
)
make %1 MODELNAME=apm-lcl-model.exe -C source
move source\dist\apm-lcl-model.exe .
