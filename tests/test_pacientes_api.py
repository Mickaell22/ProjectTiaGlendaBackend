import requests
import json
import time
import sys
import os
from datetime import date, timedelta

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.advanced_test_runner import AdvancedTestRunner, TestConfig

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_paciente_id = None
created_persona_id = None
created_tutor_id = None


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
    """Crear datos de prueba necesarios"""
    global token, created_persona_id, created_tutor_id

    if not token:
        raise Exception("No hay token disponible para setup")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Crear una persona para usar como tutor
    tutor_persona_data = {
        "nombre": "María Elena",
        "apellido": "Jiménez Mora",
        "cedula": f"88{int(time.time())}",
        "telefono": "+50688776655",
        "correo": f"maria.jimenez.{int(time.time())}@email.com",
        "direccion": "Heredia, Costa Rica",
        "fecha_nacimiento": "1985-08-20"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=tutor_persona_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            tutor_persona_id = response_data["data"]["id"]
            print_test_info("Crear persona para tutor", "SUCCESS", {"persona_id": tutor_persona_id})
        else:
            raise Exception(f"Error creando persona tutor: {response_data}")

    except Exception as e:
        if "Error creando persona tutor:" in str(e):
            raise e
        raise Exception(f"Error en creación persona tutor: {str(e)}")

    # 2. Crear el tutor
    tutor_data = {
        "persona_id": tutor_persona_id,
        "parentesco": "madre",
        "es_contacto_emergencia": True,
        "observaciones_tutor": "Madre responsable, disponible en horarios matutinos"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=tutor_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_tutor_id = response_data["data"]["id"]
            print_test_info("Crear tutor", "SUCCESS", {"tutor_id": created_tutor_id})
        else:
            raise Exception(f"Error creando tutor: {response_data}")

    except Exception as e:
        if "Error creando tutor:" in str(e):
            raise e
        raise Exception(f"Error en creación tutor: {str(e)}")

    # 3. Crear una persona para usar como paciente
    paciente_persona_data = {
        "nombre": "Santiago",
        "apellido": "Jiménez López",
        "cedula": f"77{int(time.time())}",
        "telefono": "+50677665544",
        "correo": f"santiago.jimenez.{int(time.time())}@email.com",
        "direccion": "Heredia, Costa Rica",
        "fecha_nacimiento": "2015-03-10"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=paciente_persona_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]
            print_test_info("Crear persona para paciente", "SUCCESS", {"persona_id": created_persona_id})
            return True
        else:
            raise Exception(f"Error creando persona paciente: {response_data}")

    except Exception as e:
        if "Error creando persona paciente:" in str(e):
            raise e
        raise Exception(f"Error en creación persona paciente: {str(e)}")


def test_pacientes_crud():
    """Probar CRUD completo de pacientes"""
    global token, created_paciente_id, created_persona_id, created_tutor_id

    if not token or not created_persona_id or not created_tutor_id:
        raise Exception("Faltan datos de configuración para CRUD")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todos los pacientes
    try:
        response = requests.get(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test_info("Listar pacientes", "SUCCESS" if success else "FAILED", {
            "total_pacientes": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

        if not success:
            raise Exception(f"Error listando pacientes: {response_data}")

    except Exception as e:
        if "Error listando pacientes:" in str(e):
            raise e
        raise Exception(f"Error en listar pacientes: {str(e)}")

    # 2. Crear nuevo paciente
    fecha_ingreso = (date.today() - timedelta(days=30)).isoformat()  # Hace 30 días

    new_paciente_data = {
        "persona_id": created_persona_id,
        "tutor_id": created_tutor_id,
        "fecha_ingreso": fecha_ingreso,
        "observaciones": "Paciente con necesidades de terapia ocupacional. Muy colaborativo y con gran potencial de mejora.",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers,
            json=new_paciente_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_paciente_id = response_data["data"]["id"]
            print_test_info("Crear paciente", "SUCCESS", response_data)
        else:
            raise Exception(f"Error creando paciente: {response_data}")

    except Exception as e:
        if "Error creando paciente:" in str(e):
            raise e
        raise Exception(f"Error en crear paciente: {str(e)}")

    # 3. Obtener paciente por ID
    if created_paciente_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error obteniendo paciente: {response.json()}")

            print_test_info("Obtener paciente por ID", "SUCCESS", response.json())

        except Exception as e:
            if "Error obteniendo paciente:" in str(e):
                raise e
            raise Exception(f"Error en obtener paciente: {str(e)}")

    # 4. Actualizar paciente
    if created_paciente_id:
        update_data = {
            "observaciones": "Paciente con excelente progreso en terapia ocupacional. Muy colaborativo y motivado."
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}",
                headers=auth_headers,
                json=update_data,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error actualizando paciente: {response.json()}")

            print_test_info("Actualizar paciente", "SUCCESS", response.json())

        except Exception as e:
            if "Error actualizando paciente:" in str(e):
                raise e
            raise Exception(f"Error en actualizar paciente: {str(e)}")

    return True


def test_pacientes_estados():
    """Probar cambios de estado específicos"""
    global token, created_paciente_id

    if not token or not created_paciente_id:
        raise Exception("Faltan datos para cambios de estado")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Probar diferentes estados
    estados_a_probar = ["inactivo", "activo", "alta"]

    for estado in estados_a_probar:
        estado_data = {"estado": estado}

        try:
            response = requests.put(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}/estado",
                headers=auth_headers,
                json=estado_data,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                # Algunos cambios de estado pueden fallar si son inválidos
                response_data = response.json()
                if response.status_code == 400:
                    print_test_info(f"Cambiar estado a {estado}", "INFO", {
                        "message": f"Cambio inválido (esperado): {response_data.get('message')}"
                    })
                else:
                    raise Exception(f"Error cambiando estado a {estado}: {response_data}")
            else:
                print_test_info(f"Cambiar estado a {estado}", "SUCCESS", response.json())

        except Exception as e:
            if f"Error cambiando estado a {estado}:" in str(e):
                raise e
            raise Exception(f"Error en cambio estado {estado}: {str(e)}")

    return True


def test_pacientes_endpoints_adicionales():
    """Probar endpoints adicionales de pacientes"""
    global token, created_tutor_id

    if not token:
        raise Exception("No hay token para endpoints adicionales")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener pacientes por tutor
    if created_tutor_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/pacientes/tutor/{created_tutor_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()
            if not success:
                raise Exception(f"Error obteniendo pacientes por tutor: {response_data}")

            print_test_info("Pacientes por tutor", "SUCCESS", {
                "total_pacientes": len(response_data.get("data", [])),
                "status": response_data.get("status")
            })

        except Exception as e:
            if "Error obteniendo pacientes por tutor:" in str(e):
                raise e
            raise Exception(f"Error en pacientes por tutor: {str(e)}")

    # 2. Obtener estadísticas
    try:
        response = requests.get(
            f"{BASE_URL}/api/pacientes/estadisticas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error obteniendo estadísticas: {response.json()}")

        print_test_info("Estadísticas de pacientes", "SUCCESS", response.json())

    except Exception as e:
        if "Error obteniendo estadísticas:" in str(e):
            raise e
        raise Exception(f"Error en estadísticas: {str(e)}")

    # 3. Obtener personas disponibles para paciente
    try:
        response = requests.get(
            f"{BASE_URL}/api/pacientes/personas-disponibles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error obteniendo personas disponibles: {response_data}")

        print_test_info("Personas disponibles para paciente", "SUCCESS", {
            "total_disponibles": len(response_data.get("data", [])),
            "status": response_data.get("status")
        })

    except Exception as e:
        if "Error obteniendo personas disponibles:" in str(e):
            raise e
        raise Exception(f"Error en personas disponibles: {str(e)}")

    return True


def test_pacientes_validations():
    """Probar validaciones de pacientes"""
    global token

    if not token:
        raise Exception("No hay token para validaciones")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Lista de validaciones a probar
    validations = [
        {
            "name": "campos faltantes",
            "data": {"tutor_id": 1, "fecha_ingreso": "2024-01-15"},  # persona_id faltante
            "expected_status": 400
        },
        {
            "name": "IDs invalidos",
            "data": {"persona_id": "no_es_numero", "tutor_id": "tampoco_es_numero", "fecha_ingreso": "2024-01-15"},
            "expected_status": 400
        },
        {
            "name": "fecha futura",
            "data": {"persona_id": 1, "tutor_id": 1, "fecha_ingreso": (date.today() + timedelta(days=30)).isoformat()},
            "expected_status": 400
        },
        {
            "name": "observaciones muy largas",
            "data": {"persona_id": 1, "tutor_id": 1, "fecha_ingreso": "2024-01-15", "observaciones": "A" * 1001},
            "expected_status": 400
        }
    ]

    for validation in validations:
        try:
            response = requests.post(
                f"{BASE_URL}/api/pacientes",
                headers=auth_headers,
                json=validation["data"],
                timeout=10
            )

            success = response.status_code == validation["expected_status"]
            if not success:
                raise Exception(
                    f"Validación {validation['name']} falló: esperado {validation['expected_status']}, obtenido {response.status_code}")

            print_test_info(f"Validacion {validation['name']}", "SUCCESS", {
                "expected": validation["expected_status"],
                "received": response.status_code
            })

        except Exception as e:
            if f"Validación {validation['name']} falló:" in str(e):
                raise e
            raise Exception(f"Error en validación {validation['name']}: {str(e)}")

    # Validación de estado inválido
    try:
        response = requests.put(
            f"{BASE_URL}/api/pacientes/1/estado",
            headers=auth_headers,
            json={"estado": "estado_inexistente"},
            timeout=10
        )

        success = response.status_code == 400
        if not success:
            raise Exception(f"Validación estado inválido falló: esperado 400, obtenido {response.status_code}")

        print_test_info("Validacion estado invalido", "SUCCESS", {
            "expected": 400,
            "received": response.status_code
        })

    except Exception as e:
        if "Validación estado inválido falló:" in str(e):
            raise e
        raise Exception(f"Error en validación estado: {str(e)}")

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
    config.export_path = "results_pacientes.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("PACIENTES", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (setup_test_data, "Configuracion de datos"),
        (test_pacientes_crud, "CRUD de pacientes"),
        (test_pacientes_estados, "Cambios de estado"),
        (test_pacientes_endpoints_adicionales, "Endpoints adicionales"),
        (test_pacientes_validations, "Validaciones")
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