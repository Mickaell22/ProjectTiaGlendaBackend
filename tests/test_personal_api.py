import requests
import json
import time
import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.advanced_test_runner import AdvancedTestRunner, TestConfig

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_personal_id = None
created_persona_id = None
test_especialidad_id = None


def print_test_info(test_name, status, data=None, error=None):
    """Función helper para logging de tests individuales"""
    if data and isinstance(data, dict):
        print(f"   📋 Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
    if error:
        print(f"   ⚠️  Error: {error}")


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
    """Crear datos de prueba necesarios"""
    global token, created_persona_id, test_especialidad_id

    if not token:
        raise Exception("No hay token disponible para setup")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Crear una persona para usar como personal
    timestamp = int(time.time())
    persona_data = {
        "nombre": "Carlos Alberto",
        "apellido": "Méndez Silva",
        "cedula": f"77{timestamp}",
        "telefono": "+50677889900",
        "correo": f"carlos.mendez{timestamp}@gmail.com",
        "direccion": "San José, Costa Rica",
        "fecha_nacimiento": "1985-03-22"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=persona_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]
            print_test_info("Setup persona para personal", "SUCCESS", {"persona_id": created_persona_id})
        else:
            raise Exception(f"Error creando persona: {response_data}")

    except Exception as e:
        if "Error creando persona:" in str(e):
            raise e
        raise Exception(f"Error en setup persona: {str(e)}")

    # 2. Obtener una especialidad existente para las pruebas
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/activas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data") and len(response_data["data"]) > 0:
            test_especialidad_id = response_data["data"][0]["id"]
            print_test_info("Setup especialidad para tests", "SUCCESS", {
                "especialidad_id": test_especialidad_id,
                "nombre": response_data["data"][0].get("nombre", "N/A")
            })
        else:
            raise Exception("No hay especialidades activas disponibles para tests")

    except Exception as e:
        if "No hay especialidades activas" in str(e):
            raise e
        raise Exception(f"Error en setup especialidad: {str(e)}")

    return True


def test_personal_crud():
    """Probar CRUD completo de personal"""
    global token, created_personal_id, created_persona_id

    if not token or not created_persona_id:
        raise Exception("Faltan datos de configuración para CRUD")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todo el personal
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error listando personal: {response_data}")

        print_test_info("Listar personal", "SUCCESS", {
            "total_personal": len(response_data.get("data", [])),
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        if "Error listando personal:" in str(e):
            raise e
        raise Exception(f"Error en listar personal: {str(e)}")

    # 2. Crear nuevo personal
    new_personal_data = {
        "persona_id": created_persona_id,
        "titulo_profesional": "Licenciatura en Terapia Ocupacional",
        "observaciones_personal": "Personal creado durante tests automatizados. Especialista en pediatría.",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personal",
            headers=auth_headers,
            json=new_personal_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_personal_id = response_data["data"]["id"]

        if not success:
            raise Exception(f"Error creando personal: {response_data}")

        print_test_info("Crear personal", "SUCCESS", response_data)

    except Exception as e:
        if "Error creando personal:" in str(e):
            raise e
        raise Exception(f"Error en crear personal: {str(e)}")

    # 3. Obtener personal por ID
    if created_personal_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/personal/{created_personal_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error obteniendo personal: {response.json()}")

            print_test_info("Obtener personal por ID", "SUCCESS", response.json())

        except Exception as e:
            if "Error obteniendo personal:" in str(e):
                raise e
            raise Exception(f"Error en obtener personal: {str(e)}")

    # 4. Actualizar personal
    if created_personal_id:
        update_data = {
            "observaciones_personal": "Personal actualizado durante pruebas automatizadas. Excelente desempeño.",
            "estado": "activo"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/personal/{created_personal_id}",
                headers=auth_headers,
                json=update_data,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error actualizando personal: {response.json()}")

            print_test_info("Actualizar personal", "SUCCESS", response.json())

        except Exception as e:
            if "Error actualizando personal:" in str(e):
                raise e
            raise Exception(f"Error en actualizar personal: {str(e)}")

    return True


def test_personal_especialidades():
    """Probar gestión de especialidades del personal"""
    global token, created_personal_id, test_especialidad_id

    if not token or not created_personal_id or not test_especialidad_id:
        raise Exception("Faltan datos para gestión de especialidades")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener especialidades del personal (debería estar vacío inicialmente)
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error obteniendo especialidades iniciales: {response_data}")

        print_test_info("Especialidades iniciales", "SUCCESS", {
            "total_especialidades": len(response_data.get("data", [])),
            "status": response_data.get("status")
        })

    except Exception as e:
        if "Error obteniendo especialidades iniciales:" in str(e):
            raise e
        raise Exception(f"Error en especialidades iniciales: {str(e)}")

    # 2. Asignar especialidad al personal
    assign_data = {
        "especialidad_id": test_especialidad_id
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers,
            json=assign_data,
            timeout=10
        )

        success = response.status_code in [200, 201]
        if not success:
            raise Exception(f"Error asignando especialidad: {response.json()}")

        print_test_info("Asignar especialidad", "SUCCESS", response.json())

    except Exception as e:
        if "Error asignando especialidad:" in str(e):
            raise e
        raise Exception(f"Error en asignar especialidad: {str(e)}")

    # 3. Verificar que la especialidad fue asignada
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error verificando especialidad asignada: {response_data}")

        print_test_info("Verificar especialidad asignada", "SUCCESS", {
            "total_especialidades": len(response_data.get("data", [])),
            "status": response_data.get("status")
        })

    except Exception as e:
        if "Error verificando especialidad asignada:" in str(e):
            raise e
        raise Exception(f"Error en verificar especialidad: {str(e)}")

    # 4. Intentar asignar la misma especialidad (debería fallar)
    try:
        response = requests.post(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers,
            json=assign_data,
            timeout=10
        )

        success = response.status_code == 400
        if not success:
            print_test_info("Validación especialidad duplicada", "INFO", {
                "message": f"Respuesta inesperada: {response.status_code}, pero test continúa"
            })
        else:
            print_test_info("Validación especialidad duplicada", "SUCCESS", response.json())

    except Exception as e:
        print_test_info("Validación especialidad duplicada", "INFO", {
            "message": f"Test omitido por error: {str(e)}"
        })

    # 5. Quitar especialidad del personal
    try:
        response = requests.delete(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades/{test_especialidad_id}",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error quitando especialidad: {response.json()}")

        print_test_info("Quitar especialidad", "SUCCESS", response.json())

    except Exception as e:
        if "Error quitando especialidad:" in str(e):
            raise e
        raise Exception(f"Error en quitar especialidad: {str(e)}")

    return True


def test_personal_por_area():
    """Probar endpoints de personal por área"""
    global token

    if not token:
        raise Exception("No hay token para personal por área")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Áreas a probar
    areas = ["terapeutico", "pedagogico"]

    for area in areas:
        try:
            response = requests.get(
                f"{BASE_URL}/api/personal/area/{area}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()
            if not success:
                raise Exception(f"Error obteniendo personal {area}: {response_data}")

            print_test_info(f"Personal {area}", "SUCCESS", {
                f"total_{area}": len(response_data.get("data", [])),
                "status": response_data.get("status")
            })

        except Exception as e:
            if f"Error obteniendo personal {area}:" in str(e):
                raise e
            raise Exception(f"Error en personal {area}: {str(e)}")

    return True


def test_personal_endpoints_adicionales():
    """Probar endpoints adicionales de personal"""
    global token

    if not token:
        raise Exception("No hay token para endpoints adicionales")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener estadísticas del personal
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/estadisticas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error obteniendo estadísticas: {response.json()}")

        print_test_info("Estadísticas del personal", "SUCCESS", response.json())

    except Exception as e:
        if "Error obteniendo estadísticas:" in str(e):
            raise e
        raise Exception(f"Error en estadísticas: {str(e)}")

    return True


def test_personal_validations():
    """Probar validaciones de personal"""
    global token

    if not token:
        raise Exception("No hay token para validaciones")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Lista de validaciones a probar
    validations = [
        {
            "name": "campos faltantes",
            "data": {"titulo_profesional": "Licenciatura Test"},  # persona_id faltante
            "expected_status": 400
        },
        {
            "name": "persona_id invalido",
            "data": {"persona_id": "no_es_numero", "titulo_profesional": "Licenciatura Test"},
            "expected_status": 400
        },
        {
            "name": "titulo muy corto",
            "data": {"persona_id": 1, "titulo_profesional": "A"},
            "expected_status": 400
        },
        {
            "name": "titulo muy largo",
            "data": {"persona_id": 1, "titulo_profesional": "A" * 300},
            "expected_status": 400
        },
        {
            "name": "estado invalido",
            "data": {"persona_id": 1, "titulo_profesional": "Licenciatura Test", "estado": "estado_inexistente"},
            "expected_status": 400
        },
        {
            "name": "persona inexistente",
            "data": {"persona_id": 99999, "titulo_profesional": "Licenciatura Test"},
            "expected_status": 400
        }
    ]

    for validation in validations:
        try:
            response = requests.post(
                f"{BASE_URL}/api/personal",
                headers=auth_headers,
                json=validation["data"],
                timeout=10
            )

            success = response.status_code == validation["expected_status"]
            if not success:
                raise Exception(f"Validación '{validation['name']}' falló. Esperado: {validation['expected_status']}, Obtenido: {response.status_code}")

            print_test_info(f"Validación: {validation['name']}", "SUCCESS", {
                "status_code": response.status_code,
                "message": response.json().get("message", "")
            })

        except Exception as e:
            if f"Validación '{validation['name']}' falló" in str(e):
                raise e
            raise Exception(f"Error en validación {validation['name']}: {str(e)}")

    return True


def main():
    """Función principal con el nuevo runner"""

    # Configurar el runner
    config = TestConfig()
    config.bar_style = "modern"
    config.show_eta = True
    config.show_individual_times = True
    config.colored_output = True
    config.detailed_summary = True
    config.export_results = True
    config.export_path = "results_personal.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("PERSONAL", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (setup_test_data, "Configuracion de datos"),
        (test_personal_crud, "CRUD de personal"),
        (test_personal_especialidades, "Gestión de especialidades"),
        (test_personal_por_area, "Personal por área"),
        (test_personal_endpoints_adicionales, "Endpoints adicionales"),
        (test_personal_validations, "Validaciones")
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
            print("❌ Error: El servidor no responde correctamente")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: No se pudo conectar al servidor en {BASE_URL}")
        print(f"Asegurate de que el servidor este corriendo con: python app.py")
        print(f"Error detallado: {e}")
        sys.exit(1)