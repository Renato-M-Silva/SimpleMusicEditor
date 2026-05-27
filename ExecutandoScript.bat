@echo off
chcp 65001 > nul
title Menu de Scripts Python

:MENU
cls
echo ====================================
echo   Escolha qual script executar:
echo ====================================
echo.

setlocal enabledelayedexpansion
set "script_count=0"
set "scripts_array="

:: Percorre todos os arquivos .py na pasta atual e os adiciona à lista
for %%f in (*.py) do (
    set /a script_count+=1
    set "scripts_array[!script_count!]=%%f"
    echo !script_count!. %%f
)

echo.
echo 0. Sair
echo ====================================
echo.

set /p "escolha=Digite o numero da opcao e pressione ENTER: "

if "%escolha%"=="0" goto SAIR

:: Valida a entrada do usuario
if not "%escolha%" geq "1" goto MENU_INVALIDA
if not "%escolha%" leq "%script_count%" goto MENU_INVALIDA

:: Executa o script selecionado
set "script_to_run=!scripts_array[%escolha%]!"
if defined script_to_run (
    start "" python "!script_to_run!"
    goto END
) else (
    goto MENU_INVALIDA
)

:MENU_INVALIDA
echo.
echo Opcao invalida! Pressione qualquer tecla para tentar novamente.
pause > nul
goto MENU

:SAIR
echo.
echo Saindo...
timeout /t 1 /nobreak > nul
goto END

:END
endlocal
exit