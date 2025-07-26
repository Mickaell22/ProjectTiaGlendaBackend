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
created_terapeuta_id = None
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
        "usuario": "admin",
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


def setup_test_data():
    """Crear datos de prueba necesarios (especialidad, terapeuta, paciente)"""
    global token, created_especialidad_id, created_terapeuta_id, created_paciente_id

    if not token:
        raise Exception("No hay token disponible para setup")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener especialidades disponibles
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data") and len(response_data["data"]) > 0:
            created_especialidad_id = response_data["data"][0]["id"]
            print_test_info("Obtener especialidad", "SUCCESS", {"especialidad_id": created_especialidad_id})
        else:
            raise Exception(f"Error obteniendo especialidades: {response_data}")

    except Exception as e:
        if "Error obteniendo especialidades:" in str(e):
            raise e
        raise Exception(f"Error en obtención de especialidades: {str(e)}")

    # 2. Obtener terapeutas disponibles
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/terapeutas-disponibles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data") and len(response_data["data"]) > 0:
            created_terapeuta_id = response_data["data"][0]["id"]
            print_test_info("Obtener terapeuta", "SUCCESS", {"terapeuta_id": created_terapeuta_id})
        else:
            raise Exception(f"Error obteniendo terapeutas: {response_data}")

    except Exception as e:
        if "Error obteniendo terapeutas:" in str(e):
            raise e
        raise Exception(f"Error en obtención de terapeutas: {str(e)}")

    # 3. Obtener pacientes disponibles
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/pacientes-disponibles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data") and len(response_data["data"]) > 0:
            created_paciente_id = response_data["data"][0]["id"]
            print_test_info("Obtener paciente", "SUCCESS", {"paciente_id": created_paciente_id})
        else:
            raise Exception(f"Error obteniendo pacientes: {response_data}")

    except Exception as e:
        if "Error obteniendo pacientes:" in str(e):
            raise e
        raise Exception(f"Error en obtención de pacientes: {str(e)}")


def test_sesiones_terapia_crud():
    """Probar CRUD completo de sesiones de terapia"""
    global token, created_sesion_id, created_especialidad_id, created_terapeuta_id, created_paciente_id

    if not token or not created_especialidad_id or not created_terapeuta_id:
        raise Exception("Faltan datos de configuración para CRUD")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todas las sesiones de terapia
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test_info("Listar sesiones", "SUCCESS" if success else "FAILED", {
            "total_sesiones": len(response_data.get("data", [])) if success else 0,
            "status_code": response.status_code
        })

        if not success:
            raise Exception(f"Error listando sesiones: {response_data}")

    except Exception as e:
        if "Error listando sesiones:" in str(e):
            raise e
        raise Exception(f"Error en listado de sesiones: {str(e)}")

    # 2. Crear nueva sesión de terapia
    fecha_inicio = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    fecha_fin = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    sesion_data = {
        "titulo": f"Sesión de Prueba {int(time.time())}",
        "terapeuta_id": created_terapeuta_id,
        "especialidad_id": created_especialidad_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "dias_semana": ["lunes", "miercoles", "viernes"],  # SIN TILDES
        "hora_inicio": "09:00",
        "duracion_minutos": 45,
        "numero_sesiones_contratadas": 12,
        "costo_total": 240000.0,
        "meses_contrato": 1,
        "observaciones": "Sesión de prueba para testing automatizado"
    }

    if created_paciente_id:
        sesion_data["pacientes"] = [{
            "paciente_id": created_paciente_id,
            "fecha_incorporacion": fecha_inicio,
            "costo_paciente": 240000.0,
            "observaciones_paciente": "Paciente de prueba"
        }]

    try:
        response = requests.post(
            f"{BASE_URL}/api/sesiones-terapia",
            headers=auth_headers,
            json=sesion_data,
            timeout=15
        )

        success = response.status_code in [200, 201]
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_sesion_id = response_data["data"]["id"]
            print_test_info("Crear sesión", "SUCCESS", {
                "sesion_id": created_sesion_id,
                "codigo_sesion": response_data["data"].get("codigo_sesion")
            })
        else:
            print_test_info("Crear sesión", "FAILED", response_data)
            raise Exception(f"Error creando sesión: {response_data}")

    except Exception as e:
        if "Error creando sesión:" in str(e):
            raise e
        raise Exception(f"Error en creación de sesión: {str(e)}")

    # 3. Obtener sesión específica
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("id") == created_sesion_id:
            print_test_info("Obtener sesión", "SUCCESS", {
                "sesion_id": response_data["data"]["id"],
                "titulo": response_data["data"]["titulo"],
                "estado": response_data["data"]["estado"]
            })
        else:
            raise Exception(f"Error obteniendo sesión: {response_data}")

    except Exception as e:
        if "Error obteniendo sesión:" in str(e):
            raise e
        raise Exception(f"Error en obtención de sesión: {str(e)}")

    # 4. Actualizar sesión
    update_data = {
        "titulo": f"Sesión Actualizada {int(time.time())}",
        "terapeuta_id": created_terapeuta_id,
        "especialidad_id": created_especialidad_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "dias_semana": ["lunes", "miercoles"],  # SIN TILDES
        "hora_inicio": "10:00",
        "duracion_minutos": 60,
        "numero_sesiones_contratadas": 10,
        "costo_total": 300000.0,
        "meses_contrato": 1,
        "estado": "activo",
        "observaciones": "Sesión actualizada en testing"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}",
            headers=auth_headers,
            json=update_data,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            print_test_info("Actualizar sesión", "SUCCESS", {
                "sesion_id": response_data.get("data", {}).get("id"),
                "mensaje": response_data.get("message")
            })
        else:
            raise Exception(f"Error actualizando sesión: {response_data}")

    except Exception as e:
        if "Error actualizando sesión:" in str(e):
            raise e
        raise Exception(f"Error en actualización de sesión: {str(e)}")


def test_cronograma_sesiones():
    """Probar funcionalidades del cronograma de sesiones"""
    global token, created_sesion_id, created_cronograma_id

    if not token or not created_sesion_id:
        raise Exception("Faltan datos para pruebas de cronograma")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener cronograma de la sesión
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}/cronograma",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data"):
            cronograma = response_data["data"]
            if len(cronograma) > 0:
                created_cronograma_id = cronograma[0]["id"]
            print_test_info("Obtener cronograma", "SUCCESS", {
                "total_sesiones_programadas": len(cronograma),
                "cronograma_id": created_cronograma_id
            })
        else:
            raise Exception(f"Error obteniendo cronograma: {response_data}")

    except Exception as e:
        if "Error obteniendo cronograma:" in str(e):
            raise e
        raise Exception(f"Error en obtención de cronograma: {str(e)}")

    # 2. Generar cronograma (si no existe)
    if not created_cronograma_id:
        try:
            response = requests.post(
                f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}/cronograma/generar",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()

            if success:
                print_test_info("Generar cronograma", "SUCCESS", {
                    "sesion_id": response_data.get("data", {}).get("sesion_id"),
                    "mensaje": response_data.get("message")
                })

                # Obtener cronograma nuevamente para conseguir el ID
                response = requests.get(
                    f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}/cronograma",
                    headers=auth_headers,
                    timeout=10
                )

                if response.status_code == 200:
                    cronograma_data = response.json()
                    if cronograma_data.get("data") and len(cronograma_data["data"]) > 0:
                        created_cronograma_id = cronograma_data["data"][0]["id"]
            else:
                raise Exception(f"Error generando cronograma: {response_data}")

        except Exception as e:
            if "Error generando cronograma:" in str(e):
                raise e
            raise Exception(f"Error en generación de cronograma: {str(e)}")

    # 3. Marcar sesión como realizada (si tenemos cronograma)
    if created_cronograma_id:
        try:
            realizacion_data = {
                "observaciones": "Sesión realizada exitosamente en testing"
            }

            response = requests.put(
                f"{BASE_URL}/api/cronograma-sesiones/{created_cronograma_id}/realizar",
                headers=auth_headers,
                json=realizacion_data,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()

            if success:
                print_test_info("Marcar sesión realizada", "SUCCESS", {
                    "cronograma_id": response_data.get("data", {}).get("cronograma_id"),
                    "mensaje": response_data.get("message")
                })
            else:
                print_test_info("Marcar sesión realizada", "WARNING", {
                    "status_code": response.status_code,
                    "response": response_data
                })

        except Exception as e:
            print_test_info("Marcar sesión realizada", "WARNING", error=str(e))


def test_gestion_pacientes():
    """Probar gestión de pacientes en sesiones"""
    global token, created_sesion_id, created_paciente_id

    if not token or not created_sesion_id:
        raise Exception("Faltan datos para pruebas de gestión de pacientes")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener pacientes de la sesión
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}/pacientes",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            pacientes = response_data.get("data", [])
            print_test_info("Obtener pacientes de sesión", "SUCCESS", {
                "total_pacientes": len(pacientes)
            })
        else:
            raise Exception(f"Error obteniendo pacientes de sesión: {response_data}")

    except Exception as e:
        if "Error obteniendo pacientes de sesión:" in str(e):
            raise e
        raise Exception(f"Error en obtención de pacientes: {str(e)}")

    # 2. Agregar paciente a sesión (si no está ya)
    if created_paciente_id:
        try:
            paciente_data = {
                "paciente_id": created_paciente_id,
                "fecha_incorporacion": datetime.now().strftime('%Y-%m-%d'),
                "costo_paciente": 20000.0,
                "observaciones_paciente": "Paciente agregado en testing"
            }

            response = requests.post(
                f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}/pacientes",
                headers=auth_headers,
                json=paciente_data,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()

            if success:
                print_test_info("Agregar paciente a sesión", "SUCCESS", {
                    "paciente_id": created_paciente_id,
                    "mensaje": response_data.get("message")
                })
            else:
                print_test_info("Agregar paciente a sesión", "WARNING", {
                    "status_code": response.status_code,
                    "response": response_data
                })

        except Exception as e:
            print_test_info("Agregar paciente a sesión", "WARNING", error=str(e))


def test_endpoints_adicionales():
    """Probar endpoints adicionales de sesiones de terapia"""
    global token, created_terapeuta_id

    if not token:
        raise Exception("No hay token para pruebas adicionales")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener estadísticas
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/estadisticas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data"):
            stats = response_data["data"]
            print_test_info("Obtener estadísticas", "SUCCESS", {
                "total_sesiones": stats.get("sesiones", {}).get("total", 0),
                "sesiones_activas": stats.get("sesiones", {}).get("activas", 0)
            })
        else:
            raise Exception(f"Error obteniendo estadísticas: {response_data}")

    except Exception as e:
        if "Error obteniendo estadísticas:" in str(e):
            raise e
        raise Exception(f"Error en obtención de estadísticas: {str(e)}")

    # 2. Obtener sesiones de hoy
    try:
        response = requests.get(
            f"{BASE_URL}/api/sesiones-terapia/hoy",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            sesiones_hoy = response_data.get("data", [])
            print_test_info("Obtener sesiones de hoy", "SUCCESS", {
                "total_sesiones_hoy": len(sesiones_hoy)
            })
        else:
            raise Exception(f"Error obteniendo sesiones de hoy: {response_data}")

    except Exception as e:
        if "Error obteniendo sesiones de hoy:" in str(e):
            raise e
        raise Exception(f"Error en obtención de sesiones de hoy: {str(e)}")

    # 3. Obtener sesiones por terapeuta
    if created_terapeuta_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/sesiones-terapia/terapeuta/{created_terapeuta_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()

            if success:
                sesiones_terapeuta = response_data.get("data", [])
                print_test_info("Obtener sesiones por terapeuta", "SUCCESS", {
                    "total_sesiones_terapeuta": len(sesiones_terapeuta),
                    "terapeuta_id": created_terapeuta_id
                })
            else:
                raise Exception(f"Error obteniendo sesiones por terapeuta: {response_data}")

        except Exception as e:
            if "Error obteniendo sesiones por terapeuta:" in str(e):
                raise e
            raise Exception(f"Error en obtención de sesiones por terapeuta: {str(e)}")


def test_cleanup():
    """Limpiar datos de prueba - cancelar sesión creada"""
    global token, created_sesion_id

    if not token or not created_sesion_id:
        print_test_info("Cleanup", "SKIPPED", {"reason": "No hay datos para limpiar"})
        return

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.delete(
            f"{BASE_URL}/api/sesiones-terapia/{created_sesion_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            print_test_info("Cleanup - Cancelar sesión", "SUCCESS", {
                "sesion_id": created_sesion_id,
                "mensaje": response_data.get("message")
            })
        else:
            print_test_info("Cleanup - Cancelar sesión", "WARNING", {
                "status_code": response.status_code,
                "response": response_data
            })

    except Exception as e:
        print_test_info("Cleanup", "WARNING", error=str(e))


def main():
    """Función principal que ejecuta todas las pruebas"""
    print("\n=== INICIANDO TESTS DE SESIONES DE TERAPIA ===\n")

    # Configuracion del runner
    config = TestConfig()
    config.show_progress_bar = True
    config.show_individual_times = True
    config.colored_output = True
    config.detailed_summary = True
    config.export_results = True
    config.export_path = "results_sesiones_terapia.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("SESIONES DE TERAPIA", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (setup_test_data, "Configuracion de datos"),
        (test_sesiones_terapia_crud, "CRUD de sesiones"),
        (test_cronograma_sesiones, "Gestión de cronograma"),
        (test_gestion_pacientes, "Gestión de pacientes"),
        (test_endpoints_adicionales, "Endpoints adicionales"),
        (test_cleanup, "Limpieza de datos")
    ]

    for test_func, test_name in tests_to_run:
        runner.add_test(test_func, test_name)

    # Ejecutar todas las pruebas
    results = runner.run()

    # Retornar código de salida apropiado para CI/CD
    return 0 if results["success"] else 1


if __name__ == "__main__":
    # Verificar que el servidor este corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            exit_code = main()
            sys.exit(exit_code)
        else:
            print("ERROR: El servidor no responde correctamente")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: No se pudo conectar al servidor en {BASE_URL}")
        print(f"Asegurate de que el servidor este corriendo con: python app.py")
        print(f"Error detallado: {e}")
        sys.exit(1)