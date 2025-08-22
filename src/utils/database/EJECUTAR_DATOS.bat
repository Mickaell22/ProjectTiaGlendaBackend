@echo off
chcp 65001 >nul 2>&1

:MENU
cls
echo.
echo ============================================
echo 🏥 CENTRO TIA GLENDA - GESTOR DE DATOS
echo ============================================
echo.
echo 📋 Selecciona una opción:
echo.
echo [1] 📥 CARGAR datos iniciales (centros, usuarios, pacientes)
echo [2] 🗑️  BORRAR todos los datos de prueba
echo [3] 📊 VERIFICAR estado de los datos
echo [4] ❌ SALIR
echo.
echo ============================================
set /p "opcion=🔸 Ingresa tu opción (1-4): "

if "%opcion%"=="1" goto CARGAR_DATOS
if "%opcion%"=="2" goto BORRAR_DATOS  
if "%opcion%"=="3" goto VERIFICAR_DATOS
if "%opcion%"=="4" goto SALIR

echo.
echo ❌ Opción inválida. Intenta de nuevo...
timeout /t 2 >nul
goto MENU

:CARGAR_DATOS
cls
echo.
echo ============================================
echo 🏥 CENTRO TIA GLENDA - CARGADOR DE DATOS
echo ============================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    echo 💡 Instalar Python desde: https://python.org
    pause
    goto MENU
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
        goto MENU
    )
)

echo ✅ psycopg2 disponible
echo.

echo 🚀 INICIANDO CARGA DE DATOS INICIALES...
echo ============================================
echo.

python 02_cargar_datos.py

echo.
echo ============================================
if %errorlevel% equ 0 (
    echo 🎉 ¡DATOS CARGADOS EXITOSAMENTE!
    echo ✨ El sistema está listo para crear usuarios
    echo 🚀 Siguiente paso: Ejecutar 'python app.py'
) else (
    echo ⚠️  La carga de datos tuvo problemas
    echo 💡 Revisar los mensajes de error arriba
)
echo ============================================

echo.
echo Presiona cualquier tecla para volver al menú...
pause >nul
goto MENU

:BORRAR_DATOS
cls
echo.
echo ============================================
echo 🗑️  CENTRO TIA GLENDA - BORRADOR DE DATOS
echo ============================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    echo 💡 Instalar Python desde: https://python.org
    pause
    goto MENU
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
        goto MENU
    )
)

echo ✅ psycopg2 disponible
echo.

echo 🗑️  INICIANDO BORRADO DE DATOS...
echo ============================================
echo.

python 04_limpiar_datos.py

echo.
echo ============================================
echo Presiona cualquier tecla para volver al menú...
pause >nul
goto MENU

:VERIFICAR_DATOS
cls
echo.
echo ============================================
echo 📊 CENTRO TIA GLENDA - VERIFICADOR DE DATOS
echo ============================================
echo.

cd /d "%~dp0"

echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado
    echo 💡 Instalar Python desde: https://python.org
    pause
    goto MENU
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
        goto MENU
    )
)

echo ✅ psycopg2 disponible
echo.

echo 📊 VERIFICANDO ESTADO DE LA BASE DE DATOS...
echo ============================================
echo.

python 03_verificar_sistema.py

echo.
echo ============================================
echo Presiona cualquier tecla para volver al menú...
pause >nul
goto MENU

:SALIR
cls
echo.
echo ============================================
echo 👋 ¡HASTA LUEGO!
echo ============================================
echo.
echo 🎉 Gracias por usar el gestor de datos de Centro Tía Glenda
echo.
exit /b 0