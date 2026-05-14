@echo off
setlocal

set "REPO_DIR=%~dp0"

where wsl.exe >nul 2>nul
if errorlevel 1 (
  echo Error: wsl.exe was not found. Run build_cv_pdf.sh from a Linux/WSL shell instead.
  pause
  exit /b 1
)

wsl.exe bash -lc "cd ""$(wslpath '%REPO_DIR%')"" && ./build_cv_pdf.sh"
if errorlevel 1 (
  echo.
  echo Build failed.
  pause
  exit /b 1
)

echo.
echo Built assets\pdf\ZhaominWu.pdf
pause
