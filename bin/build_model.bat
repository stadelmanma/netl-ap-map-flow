::
:: This script assumes it has been run from the top level directory
:: as .\bin\build_model
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
    echo %errorlevel%
    if /I "%errorlevel%" NEQ "0" (
        set USE_GIT=
    )
)
if DEFINED USE_GIT (
    for /f %%i in ('git rev-parse --show-toplevel') do set REPO_HOME=%%i
)
echo %REPO_HOME%

::
:: building flow model from source
cd "%REPO_HOME%/source"
make %1 MODELNAME=APM-MODEL.EXE
cd %REPO_HOME%
move source\APM-MODEL.EXE .

::
:: handles creating a directory junction for the module if needed
:: this allows global import ApertureMapModelTools statments
::
:: getting python command if one exists
set PYTHON_EXE=python3
where %PYTHON_EXE% >nul 2>nul
if /I "%errorlevel%" NEQ "0" (
    set PYTHON_EXE=python
)
where %PYTHON_EXE% >nul 2>nul
if /I "%errorlevel%" NEQ "0" (
   exit /B
)
:: storing path to Python user site directory
for /f %%i in ('python -m site --user-site') do set SITE_PATH=%%i
:: Creating site directory first if necessary 
if NOT EXIST "%SITE_PATH%" (
    mkdir "%SITE_PATH%"
)
:: Symlinking the module into Python site
if NOT EXIST "%SITE_PATH%\ApertureMapModelTools" (
    mklink /J "%SITE_PATH%\ApertureMapModelTools" "%REPO_HOME%\ApertureMapModelTools"
    :: Checking return code of mklink command
    if /I "%errorlevel%" NEQ "0" (
        echo Error code %errorlevel% when attempting to symlink ApertureMapModelTools module
    ) else (
        echo Succesfully symlinked ApertureMapModelTools module to Python site
    )
)
