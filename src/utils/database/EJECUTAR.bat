@echo off
chcp 65001 >nul 2>&1
echo.
echo ============================================
echo 🏥 CENTRO TIA GLENDA - EJECUTOR SIMPLE
echo ============================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    echo 💡 Instalar Python desde: https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

echo 🔍 Verificando/instalando psycopg2...
python -c "import psycopg2" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚙️  Instalando psycopg2-binary...
    pip install psycopg2-binary
    if %errorlevel% neq 0 (
        echo ❌ Error instalando psycopg2
        echo 💡 Ejecutar como administrador o verificar conexión a internet
        pause
        exit /b 1
    )
)

echo ✅ psycopg2 disponible
echo.

echo 🚀 INICIANDO CREACIÓN DE ESTRUCTURA...
echo ============================================
echo.

python ejecutar_estructura_directo.py

echo.
echo ============================================
if %errorlevel% equ 0 (
    echo 🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!
    echo ✨ La base de datos está lista para usar
) else (
    echo ⚠️  El proceso tuvo problemas
    echo 💡 Revisar los mensajes de error arriba
)
echo ============================================

echo.
echo Presiona cualquier tecla para continuar...
pause >nul