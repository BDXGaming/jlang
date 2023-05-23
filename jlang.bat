@echo off

set "file=%~1"
set "remainder="

for %%i in (%*) do (
  if /I not "%%~i"=="%file%" (
    if defined remainder (
      set "remainder=!remainder! %%~i"
    ) else (
      set "remainder=%%~i"
    )
  )
)

echo "From bat"
set "cmd=python {BASEDIR}\jlang.py %file% %remainder%"
%cmd%