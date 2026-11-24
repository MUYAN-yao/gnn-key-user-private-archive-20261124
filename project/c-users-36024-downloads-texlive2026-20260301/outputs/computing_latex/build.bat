@echo off
setlocal
cd /d "%~dp0"
where pdflatex >nul 2>nul
if errorlevel 1 set "PATH=C:\texlive\2026\bin\windows;%PATH%"
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error manuscript.tex
if errorlevel 1 goto failed
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error manuscript.tex
if errorlevel 1 goto failed
echo.
echo Successfully compiled manuscript.pdf.
pause
exit /b 0
:failed
echo.
echo Compilation failed. Please inspect manuscript.log.
pause
exit /b 1
