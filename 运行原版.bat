@echo off
REM ============================================================
REM  GooBall 1.0.2  -  Windows original player
REM  Source: archive.org/item/GooBall  (2007 community upload)
REM  Engine: Unity 1.x standalone  Renderer: OpenGL  Script: Mono/Boo
REM
REM  Requirements:
REM    - 32-bit Windows (Win7/10/11 OK)
REM    - OpenGL 1.4+  (all GPUs since 2005)
REM    - If it black-screens and exits, read Data\output_log.txt
REM ============================================================
cd /d "%~dp0win"
if not exist "GooBall.exe" (
  echo [ERROR] GooBall.exe not found in %cd%
  pause
  exit /b 1
)
start "" "GooBall.exe" %*
