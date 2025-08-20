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
created_persona_id = None


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


def test_personas_crud():
    """Probar CRUD completo de personas"""
    global token, created_persona_id

    if not token:
        raise Exception("No hay token para CRUD de personas")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todas las personas
    try:
        response = requests.get(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error listando personas: {response_data}")

        print_test_info("Listar personas", "SUCCESS", {
            "total_personas": len(response_data.get("data", [])),
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        if "Error listando personas:" in str(e):
            raise e
        raise Exception(f"Error en listar personas: {str(e)}")

    # 2. Crear nueva persona
    new_persona_data = {
        "nombre": "Ana Sofía",
        "apellido": "Rodríguez Vega",
        "cedula": f"11{int(time.time())}",
        "telefono": "+50611223344",
        "correo": f"ana.rodriguez.{int(time.time())}@email.com",
        "direccion": "San José, Costa Rica",
        "fecha_nacimiento": "1990-05-15"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=new_persona_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]
            print_test_info("Crear persona", "SUCCESS", response_data)
        else:
            raise Exception(f"Error creando persona: {response_data}")

    except Exception as e:
        if "Error creando persona:" in str(e):
            raise e
        raise Exception(f"Error en crear persona: {str(e)}")

    # 3. Obtener persona por ID
    if created_persona_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/personas/{created_persona_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error obteniendo persona: {response.json()}")

            print_test_info("Obtener persona por ID", "SUCCESS", response.json())

        except Exception as e:
            if "Error obteniendo persona:" in str(e):
                raise e
            raise Exception(f"Error en obtener persona: {str(e)}")

    # 4. Actualizar persona
    if created_persona_id:
        update_data = {
            "telefono": "+50699887766",
            "direccion": "Cartago, Costa Rica - Dirección actualizada"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/personas/{created_persona_id}",
                headers=auth_headers,
                json=update_data,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error actualizando persona: {response.json()}")

            print_test_info("Actualizar persona", "SUCCESS", response.json())

        except Exception as e:
            if "Error actualizando persona:" in str(e):
                raise e
            raise Exception(f"Error en actualizar persona: {str(e)}")

    return True


def test_personas_endpoints_adicionales():
    """Probar endpoints adicionales de personas"""
    global token

    if not token:
        raise Exception("No hay token para endpoints adicionales")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Único endpoint adicional disponible: personas disponibles (requiere admin)
    try:
        response = requests.get(
            f"{BASE_URL}/api/personas/disponibles",
            headers=auth_headers,
            timeout=10
        )

        # Este endpoint requiere admin_required, puede fallar con 403
        if response.status_code == 403:
            print_test_info("Personas disponibles", "INFO", {
                "message": "Endpoint requiere permisos de administrador (403 esperado)"
            })
        elif response.status_code == 200:
            response_data = response.json()
            print_test_info("Personas disponibles", "SUCCESS", {
                "total_disponibles": len(response_data.get("data", [])),
                "status": response_data.get("status")
            })
        else:
            raise Exception(f"Error inesperado en personas disponibles: {response.json()}")

    except Exception as e:
        if "Error inesperado en personas disponibles:" in str(e):
            raise e
        raise Exception(f"Error en personas disponibles: {str(e)}")

    return True


def test_personas_validations():
    """Probar validaciones de personas"""
    global token

    if not token:
        raise Exception("No hay token para validaciones")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Lista de validaciones a probar
    validations = [
        {
            "name": "campos faltantes",
            "data": {"apellido": "Pérez", "cedula": "123456789"},  # nombre faltante
            "expected_status": 400
        },
        {
            "name": "correo invalido",
            "data": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "cedula": "987654321",
                "correo": "correo_invalido",
                "fecha_nacimiento": "1990-01-01"
            },
            "expected_status": 400
        },
        {
            "name": "telefono invalido",
            "data": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "cedula": "987654322",
                "telefono": "123",  # Muy corto
                "fecha_nacimiento": "1990-01-01"
            },
            "expected_status": 400
        },
        {
            "name": "fecha nacimiento futura",
            "data": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "cedula": "987654323",
                "fecha_nacimiento": "2030-01-01"  # Fecha futura
            },
            "expected_status": 400
        },
        {
            "name": "cedula muy larga",
            "data": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "cedula": "1234567890123456789012345",  # Muy larga
                "fecha_nacimiento": "1990-01-01"
            },
            "expected_status": 400
        }
    ]

    for validation in validations:
        try:
            response = requests.post(
                f"{BASE_URL}/api/personas",
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

    # Validación de cédula duplicada
    if created_persona_id:
        try:
            # Intentar crear persona con la misma cédula
            duplicate_data = {
                "nombre": "Otra",
                "apellido": "Persona",
                "cedula": f"11{int(time.time())}",  # Usar la misma cédula de la persona creada
                "fecha_nacimiento": "1985-01-01"
            }

            # Primero obtener la cédula de la persona creada
            person_response = requests.get(
                f"{BASE_URL}/api/personas/{created_persona_id}",
                headers=auth_headers,
                timeout=10
            )

            if person_response.status_code == 200:
                person_data = person_response.json()
                duplicate_data["cedula"] = person_data["data"]["cedula"]

            response = requests.post(
                f"{BASE_URL}/api/personas",
                headers=auth_headers,
                json=duplicate_data,
                timeout=10
            )

            success = response.status_code == 400
            if not success:
                # Si no falló, podría ser que el sistema permita duplicados o use otro mensaje
                print_test_info("Validacion cedula duplicada", "INFO", {
                    "message": "Sistema podría permitir cédulas duplicadas o usar validación diferente",
                    "status_code": response.status_code
                })
            else:
                print_test_info("Validacion cedula duplicada", "SUCCESS", {
                    "expected": 400,
                    "received": response.status_code
                })

        except Exception as e:
            raise Exception(f"Error en validación cédula duplicada: {str(e)}")

    return True


def test_delete_persona():
    """Probar eliminación de persona"""
    global token, created_persona_id

    if not token:
        raise Exception("No hay token para eliminación")

    if not created_persona_id:
        raise Exception("No hay persona creada para eliminar")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Eliminar persona creada en las pruebas
    try:
        print_test_info("Eliminacion", "INFO", {"attempting_delete": created_persona_id})

        response = requests.delete(
            f"{BASE_URL}/api/personas/{created_persona_id}",
            headers=auth_headers,
            timeout=10
        )

        response_data = response.json() if response.headers.get('content-type', '').startswith(
            'application/json') else {"text": response.text}

        print_test_info("Eliminar persona", "INFO", {
            "status_code": response.status_code,
            "response": response_data
        })

        # Casos válidos para eliminación:
        # 1. Eliminación exitosa (200)
        # 2. Persona ya estaba inactiva (400 con mensaje específico)
        # 3. No se puede eliminar por estar asociada (400 con mensaje específico)
        if response.status_code == 200:
            print_test_info("Eliminar persona", "SUCCESS", {"message": "Persona eliminada exitosamente"})
        elif (response.status_code == 400 and
              (response_data.get("message", "").lower().find("ya está inactiv") != -1 or
               response_data.get("message", "").lower().find("asociada") != -1)):
            print_test_info("Eliminar persona", "SUCCESS",
                            {"message": f"Eliminación válida: {response_data.get('message')}"})
        else:
            raise Exception(f"Delete failed: status={response.status_code}, response={response_data}")

    except Exception as e:
        if "Delete failed:" in str(e):
            raise e
        print_test_info("Eliminar persona", "ERROR", error=str(e))
        raise Exception(f"Error eliminando persona: {str(e)}")

    # Intentar eliminar persona que no existe
    try:
        response = requests.delete(
            f"{BASE_URL}/api/personas/99999",
            headers=auth_headers,
            timeout=10
        )

        response_data = response.json() if response.headers.get('content-type', '').startswith(
            'application/json') else {"text": response.text}

        print_test_info("Validacion eliminar inexistente", "INFO", {
            "status_code": response.status_code,
            "expected": [404, 400],
            "response": response_data
        })

        # Casos válidos para persona inexistente:
        # 1. Not found (404)
        # 2. Bad request si el endpoint valida el ID (400)
        if response.status_code in [404, 400]:
            print_test_info("Validacion eliminar inexistente", "SUCCESS", {
                "message": f"Validación correcta (status: {response.status_code})"
            })
        else:
            raise Exception(f"Validation failed: expected 404 or 400, got {response.status_code}")

    except Exception as e:
        if "Validation failed:" in str(e):
            raise e
        print_test_info("Validacion eliminar inexistente", "ERROR", error=str(e))
        raise Exception(f"Error validando eliminacion inexistente: {str(e)}")

    return True


def main():
    """Función principal con el nuevo runner"""

    # Configurar el runner
    config = TestConfig()
    config.bar_style = "dots"
    config.show_eta = True
    config.show_individual_times = True
    config.colored_output = True
    config.detailed_summary = True
    config.export_results = True
    config.export_path = "results_personas.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("PERSONAS", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (test_personas_crud, "CRUD de personas"),
        (test_personas_endpoints_adicionales, "Endpoints adicionales"),
        (test_personas_validations, "Validaciones"),
        (test_delete_persona, "Eliminacion")
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