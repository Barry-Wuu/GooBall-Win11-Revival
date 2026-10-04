@echo off
REM ============================================================
REM  GooBall 1.0.2  -  Windows original player
REM  Source: archive.org/item/GooBall  (2007 community upload)
REM  Engine: Unity 1.x standalone  Renderer: OpenGL  Script: Mono/Boo
REM
REM  Controls (after the space-jump patch):
REM    Arrow keys / Right+Left   = roll the ball
REM    SPACE                     = jump          (was: Mac Command key)
REM    Left Alt                  = stick to surface
REM
REM  If it black-screens and exits, read Data\output_log.txt
REM ============================================================
cd /d "%~dp0win"
if not exist "GooBall.exe" (
  echo [ERROR] GooBall.exe not found in %cd%
  pause
  exit /b 1
)
start "" "GooBall.exe" %*
