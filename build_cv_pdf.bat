@echo off
setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"
set "LATEX_DIR=%REPO_DIR%assets\latex"
set "BUILD_DIR=%LATEX_DIR%\build"
set "OUT_DIR=%REPO_DIR%assets\pdf"
set "JOB=ZhaominWu"
set "OUTPUT_PDF=%OUT_DIR%\%JOB%.pdf"

set "PDFLATEX="
for /f "delims=" %%I in ('where pdflatex 2^>nul') do (
  if not defined PDFLATEX set "PDFLATEX=%%I"
)
if not defined PDFLATEX (
  if exist "C:\texlive\2022\bin\win32\pdflatex.exe" set "PDFLATEX=C:\texlive\2022\bin\win32\pdflatex.exe"
)
if not defined PDFLATEX (
  echo Error: pdflatex was not found on PATH and no TeX Live install was detected.
  echo Install TeX Live or MiKTeX, or add pdflatex to PATH.
  pause
  exit /b 1
)

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

pushd "%LATEX_DIR%" >nul

"%PDFLATEX%" -interaction=nonstopmode -halt-on-error -jobname=%JOB% -output-directory=build %JOB%.tex
if errorlevel 1 goto :build_failed

"%PDFLATEX%" -interaction=nonstopmode -halt-on-error -jobname=%JOB% -output-directory=build %JOB%.tex
if errorlevel 1 goto :build_failed

copy /Y "build\%JOB%.pdf" "%OUTPUT_PDF%" >nul
if errorlevel 1 goto :build_failed

popd >nul
echo.
echo Built %OUTPUT_PDF%
pause
exit /b 0

:build_failed
popd >nul
echo.
echo Build failed.
pause
exit /b 1
