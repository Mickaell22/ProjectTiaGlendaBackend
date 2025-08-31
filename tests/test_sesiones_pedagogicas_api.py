import requests
import json
import time
import sys
import os
from datetime import date, timedelta, datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.advanced_test_runner import AdvancedTestRunner, TestConfig

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_sesion_id = None
created_paciente_id = None
created_pedagogo_id = None
created_especialidad_id = None
created_cronograma_id = None


def print_test_info(test_name, status, data=None, error=None):
    """Función helper para logging de tests individuales"""
    if data and isinstance(data, dict):
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
    if error:
        print(f"   Error: {error}")


def test_login():
    """Autenticarse para obtener token"""
    global token

    login_data = {
        "usuario": "admin.norte",
        "contrasenia": "admin123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json=login_data,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("token"):
            token = response_data["data"]["token"]
            print_test_info("Login", "SUCCESS", {"message": "Token obtenido exitosamente"})
            return True
        else:
            print_test_info("Login", "FAILED", response_data)
            raise Exception(f"Login failed: {response_data}")

    except Exception as e:
        if "Login failed:" in str(e):
            raise e
        print_test_info("Login", "ERROR", error=str(e))
        raise Exception(f"Error en login: {str(e)}")


def test_database_connection():
    """Test 1: Verificar conexión a la base de datos"""
    try:
        response = requests.get(f"{BASE_URL}/api/test-db", timeout=10)
        
        success = response.status_code == 200
        response_data = response.json()
        
        print_test_info("Database Connection", "SUCCESS" if success else "FAILED", response_data)
        return success
            
    except Exception as e:
        print_test_info("Database Connection", "ERROR", error=str(e))
        return False


def setup_test_data():
    """Configurar datos necesarios para los tests"""
    global token, created_pedagogo_id, created_especialidad_id, created_paciente_id

    if not token:
        raise Exception("No hay token disponible para setup")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        # Obtener pedagogos disponibles
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/pedagogos-disponibles", 
                               headers=auth_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and data.get('data') and len(data['data']) > 0:
                created_pedagogo_id = data['data'][0]['id']
            
        # Obtener especialidades
        response = requests.get(f"{BASE_URL}/api/especialidades", 
                               headers=auth_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and data.get('data') and len(data['data']) > 0:
                created_especialidad_id = data['data'][0]['id']
        
        # Obtener estudiantes disponibles
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/estudiantes-disponibles", 
                               headers=auth_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and data.get('data') and len(data['data']) > 0:
                created_paciente_id = data['data'][0]['id']

        print_test_info("Setup Test Data", "SUCCESS", {
            "pedagogo_id": created_pedagogo_id,
            "especialidad_id": created_especialidad_id,
            "paciente_id": created_paciente_id
        })
        return True

    except Exception as e:
        print_test_info("Setup Test Data", "ERROR", error=str(e))
        return False


def test_get_sesiones_pedagogicas():
    """Test 2: Obtener todas las sesiones pedagogicas"""
    global token

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Sesiones Pedagogicas", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Sesiones Pedagogicas", "ERROR", error=str(e))
        return False


def test_create_sesion_pedagogica():
    """Test 3: Crear nueva sesion pedagogica"""
    global token, created_sesion_id, created_pedagogo_id, created_especialidad_id

    if not created_pedagogo_id or not created_especialidad_id:
        print_test_info("Create Sesion Pedagogica", "SKIPPED", error="Faltan datos de prueba")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    fecha_inicio = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    fecha_fin = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')

    sesion_data = {
        "titulo": "Matematicas Basicas - Test",
        "pedagogo_id": created_pedagogo_id,
        "especialidad_id": created_especialidad_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "dias_semana": ["lunes", "miercoles", "viernes"],
        "hora_inicio": "10:00",
        "duracion_minutos": 60,
        "numero_clases_programadas": 20,
        "nivel_academico": "primaria",
        "capacidad_maxima": 15,
        "modalidad": "presencial",
        "costo_total": 500.0,
        "costo_por_clase": 25.0,
        "periodo_academico": "2025-1",
        "observaciones": "Sesion de prueba para tests automaticos"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/sesiones-pedagogicas",
            headers=auth_headers,
            json=sesion_data,
            timeout=10
        )

        success = response.status_code == 200  # Changed from 201 to 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_sesion_id = response_data["data"]["id"]

        print_test_info("Create Sesion Pedagogica", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Create Sesion Pedagogica", "ERROR", error=str(e))
        return False


def test_create_sesion_validation_error():
    """Test 4: Probar validaciones al crear sesion pedagogica"""
    global token

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Datos invalidos (sin campos requeridos)
    invalid_data = {
        "titulo": "",
        "fecha_inicio": "invalid-date"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/sesiones-pedagogicas",
            headers=auth_headers,
            json=invalid_data,
            timeout=10
        )

        success = response.status_code == 400  # Esperamos error de validacion
        response_data = response.json()

        print_test_info("Create Sesion Validation Error", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Create Sesion Validation Error", "ERROR", error=str(e))
        return False


def test_get_sesion_by_id():
    """Test 5: Obtener sesion pedagogica por ID"""
    global token, created_sesion_id

    if not created_sesion_id:
        print_test_info("Get Sesion By ID", "SKIPPED", error="No hay sesion creada")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Sesion By ID", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Sesion By ID", "ERROR", error=str(e))
        return False


def test_update_sesion_pedagogica():
    """Test 6: Actualizar sesion pedagogica"""
    global token, created_sesion_id

    if not created_sesion_id:
        print_test_info("Update Sesion Pedagogica", "SKIPPED", error="No hay sesion creada")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    update_data = {
        "titulo": "Matematicas Avanzadas - Test Actualizado",
        "observaciones": "Sesion actualizada mediante test automatico",
        "capacidad_maxima": 20
    }

    try:
        response = requests.put(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}",
            headers=auth_headers,
            json=update_data,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Update Sesion Pedagogica", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Update Sesion Pedagogica", "ERROR", error=str(e))
        return False


def test_get_estudiantes_sesion():
    """Test 7: Obtener estudiantes de sesion pedagogica"""
    global token, created_sesion_id

    if not created_sesion_id:
        print_test_info("Get Estudiantes Sesion", "SKIPPED", error="No hay sesion creada")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}/estudiantes",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Estudiantes Sesion", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Estudiantes Sesion", "ERROR", error=str(e))
        return False


def test_add_estudiante_to_sesion():
    """Test 8: Agregar estudiante a sesion pedagogica"""
    global token, created_sesion_id, created_paciente_id

    if not created_sesion_id or not created_paciente_id:
        print_test_info("Add Estudiante To Sesion", "SKIPPED", error="Faltan datos de prueba")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    estudiante_data = {
        "paciente_id": created_paciente_id,
        "costo_estudiante": 25.0,
        "nivel_actual": "basico",
        "observaciones_estudiante": "Estudiante de prueba agregado por test automatico"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}/estudiantes",
            headers=auth_headers,
            json=estudiante_data,
            timeout=10
        )

        success = response.status_code == 200  # Changed from 201 to 200
        response_data = response.json()

        print_test_info("Add Estudiante To Sesion", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Add Estudiante To Sesion", "ERROR", error=str(e))
        return False


def test_get_cronograma_sesion():
    """Test 9: Obtener cronograma de sesion pedagogica"""
    global token, created_sesion_id

    if not created_sesion_id:
        print_test_info("Get Cronograma Sesion", "SKIPPED", error="No hay sesion creada")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}/cronograma",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Cronograma Sesion", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Cronograma Sesion", "ERROR", error=str(e))
        return False


def test_get_estadisticas():
    """Test 10: Obtener estadisticas de sesiones pedagogicas"""
    global token

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/estadisticas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Estadisticas", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Estadisticas", "ERROR", error=str(e))
        return False


def test_get_sesiones_by_pedagogo():
    """Test 11: Obtener sesiones por pedagogo"""
    global token, created_pedagogo_id

    if not created_pedagogo_id:
        print_test_info("Get Sesiones By Pedagogo", "SKIPPED", error="No hay pedagogo disponible")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/pedagogo/{created_pedagogo_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Sesiones By Pedagogo", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Sesiones By Pedagogo", "ERROR", error=str(e))
        return False


def test_get_clases_hoy():
    """Test 12: Obtener clases de hoy"""
    global token

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/hoy",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Clases Hoy", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Clases Hoy", "ERROR", error=str(e))
        return False


def test_get_estudiantes_disponibles():
    """Test 13: Obtener estudiantes disponibles"""
    global token

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/estudiantes-disponibles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Estudiantes Disponibles", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Estudiantes Disponibles", "ERROR", error=str(e))
        return False


def test_get_pedagogos_disponibles():
    """Test 14: Obtener pedagogos disponibles"""
    global token

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas/pedagogos-disponibles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Get Pedagogos Disponibles", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Get Pedagogos Disponibles", "ERROR", error=str(e))
        return False


def test_remove_estudiante_from_sesion():
    """Test 15: Remover estudiante de sesion pedagogica"""
    global token, created_sesion_id, created_paciente_id

    if not created_sesion_id or not created_paciente_id:
        print_test_info("Remove Estudiante From Sesion", "SKIPPED", error="Faltan datos de prueba")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}/estudiantes/{created_paciente_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Remove Estudiante From Sesion", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Remove Estudiante From Sesion", "ERROR", error=str(e))
        return False


def test_access_without_token():
    """Test 16: Probar acceso sin token de autenticacion"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-pedagogicas",
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        success = response.status_code == 401  # Esperamos error de autenticacion
        response_data = response.json()

        print_test_info("Access Without Token", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Access Without Token", "ERROR", error=str(e))
        return False


def test_delete_sesion_pedagogica():
    """Test 17: Eliminar sesion pedagogica (requiere admin)"""
    global token, created_sesion_id

    if not created_sesion_id:
        print_test_info("Delete Sesion Pedagogica", "SKIPPED", error="No hay sesion creada")
        return True

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(
            f"{BASE_URL}/api/sesiones-pedagogicas/{created_sesion_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        print_test_info("Delete Sesion Pedagogica", "SUCCESS" if success else "FAILED", response_data)
        return success

    except Exception as e:
        print_test_info("Delete Sesion Pedagogica", "ERROR", error=str(e))
        return False


def main():
    """Función principal con el runner de tests"""

    # Configurar el runner
    config = TestConfig()
    config.bar_style = "modern"
    config.show_eta = True
    config.show_individual_times = True
    config.colored_output = True
    config.detailed_summary = True
    config.export_results = True
    config.export_path = "results_sesiones_pedagogicas.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("SESIONES PEDAGOGICAS", config)

    # Tests a ejecutar
    tests_to_run = [
        (test_login, "Login y Autenticacion"),
        (test_database_connection, "Conexion Base de Datos"),
        (setup_test_data, "Setup Datos de Prueba"),
        (test_get_sesiones_pedagogicas, "Obtener Sesiones Pedagogicas"),
        (test_create_sesion_pedagogica, "Crear Sesion Pedagogica"),
        (test_create_sesion_validation_error, "Validaciones Crear Sesion"),
        (test_get_sesion_by_id, "Obtener Sesion por ID"),
        (test_update_sesion_pedagogica, "Actualizar Sesion"),
        (test_get_estudiantes_sesion, "Obtener Estudiantes Sesion"),
        (test_add_estudiante_to_sesion, "Agregar Estudiante"),
        (test_get_cronograma_sesion, "Obtener Cronograma"),
        (test_get_estadisticas, "Obtener Estadisticas"),
        (test_get_sesiones_by_pedagogo, "Sesiones por Pedagogo"),
        (test_get_clases_hoy, "Clases de Hoy"),
        (test_get_estudiantes_disponibles, "Estudiantes Disponibles"),
        (test_get_pedagogos_disponibles, "Pedagogos Disponibles"),
        (test_remove_estudiante_from_sesion, "Remover Estudiante"),
        (test_access_without_token, "Acceso Sin Token"),
        (test_delete_sesion_pedagogica, "Eliminar Sesion")
    ]

    for test_func, test_name in tests_to_run:
        runner.add_test(test_func, test_name)

    # Ejecutar todas las pruebas
    results = runner.run()

    # Retornar código de salida apropiado
    return 0 if results["success"] else 1


if __name__ == "__main__":
    # Verificar que el servidor este corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            exit_code = main()
            sys.exit(exit_code)
        else:
            print("Error: El servidor no responde correctamente")
            sys.exit(1)
    except Exception as e:
        print(f"Error: No se pudo conectar al servidor en {BASE_URL}")
        print(f"Asegurate de que el servidor este corriendo con: python app.py")
        print(f"Error detallado: {e}")
        sys.exit(1)