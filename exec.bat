ECHO OFF
ECHO Moving files...

pushd "%~dp0"
set batdir=%cd%

mkdir "C:\Program Files\Autodesk\Maya2023\bin\plug-ins\forest_assets"
mkdir "C:\Program Files\Autodesk\Maya2023\bin\plug-ins\forest_assets"

robocopy "%batdir%" "C:\Program Files\Autodesk\Maya2023\bin\plug-ins" ForestPlugin.py

robocopy "%batdir%\forest_assets" "C:\Program Files\Autodesk\Maya2023\bin\plug-ins\forest_assets"

PAUSE