::
:: This script assumes it has been run from the top level directory
:: as .\bin\build_model
::

:: storing path to Python user site directory
for /f %%i in ('python -m site --user-site') do set SITE_PATH=%%i

:: Creating site directory first if necessary 
if NOT EXIST "%SITE_PATH%" (
    mkdir %SITE_PATH%
)

:: Symlinking the module into Python site to allow direct import statements
if NOT EXIST "%SITE_PATH%\ApertureMapModelTools" (
    mklink /J %SITE_PATH%\ApertureMapModelTools .\ApertureMapModelTools
    :: Checking return code of mklink command
    if /I "%errorlevel%" NEQ "0" (
        echo Error code %errorlevel% when attempting to symlink ApertureMapModelTools module
    ) else (
        echo Succesfully symlinked ApertureMapModelTools module to Python site
    )
)
