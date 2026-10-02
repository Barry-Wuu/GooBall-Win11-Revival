@echo off
rem GooBall Revival launcher (ASCII-only content, encoding-safe)
rem Game root: this file's directory; game files live in .\game
cd /d "%~dp0game"
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start "" http://localhost:8143/index.html"
where py >nul 2>nul
if %errorlevel%==0 (
  py -m http.server 8143
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    python -m http.server 8143
  ) else (
    if exist "D:\B++\Py313\python.exe" (
      "D:\B++\Py313\python.exe" -m http.server 8143
    ) else (
      echo Python not found. Please install Python 3.
      pause
    )
  )
)
