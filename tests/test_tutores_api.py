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
created_tutor_id = None
created_persona_id = None
created_tutor_cedula = None


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
            return False

    except Exception as e:
        print_test_info("Login", "ERROR", error=str(e))
        return False


def setup_test_data():
    """Crear datos de prueba necesarios"""
    global token, created_persona_id

    if not token:
        print_test_info("Setup", "FAILED", error="No hay token disponible")
        return False

    # Para el nuevo sistema, no necesitamos crear persona separada
    # Los datos se crean directamente en el tutor
    created_persona_id = int(time.time())  # Solo para compatibilidad con el test
    print_test_info("Setup", "SUCCESS", {"ready_for_tutor_creation": True})
    return True


def test_tutores_crud():
    """Probar CRUD completo de tutores"""
    global token, created_tutor_id, created_persona_id, created_tutor_cedula

    if not token or not created_persona_id:
        print_test_info("CRUD", "FAILED", error="Faltan datos de configuración")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todos los tutores
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test_info("Listar tutores", "SUCCESS" if success else "FAILED", {
            "total_tutores": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

        if not success:
            return False

    except Exception as e:
        print_test_info("Listar tutores", "ERROR", error=str(e))
        return False

    # 2. Crear nuevo tutor
    cedula_tutor = f"99{int(time.time())}"
    new_tutor_data = {
        "nombre": "Carmen Elena",
        "apellido": "Vargas Solís",
        "cedula": cedula_tutor,
        "telefono": "+50699887766",
        "email": f"carmen.vargas.{int(time.time())}@email.com",
        "direccion": "Cartago, Costa Rica",
        "parentesco": "madre",
        "ocupacion": "Profesora",
        "estado": "activo"
    }
    created_tutor_cedula = cedula_tutor

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=new_tutor_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_tutor_id = response_data["data"]["id"]

        print_test_info("Crear tutor", "SUCCESS" if success else "FAILED", response_data)

        if not success:
            return False

    except Exception as e:
        print_test_info("Crear tutor", "ERROR", error=str(e))
        return False

    # 3. Obtener tutor por ID
    if created_tutor_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/tutores/{created_tutor_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            print_test_info("Obtener tutor por ID", "SUCCESS" if success else "FAILED", response.json())

            if not success:
                return False

        except Exception as e:
            print_test_info("Obtener tutor por ID", "ERROR", error=str(e))
            return False

    # 4. Actualizar tutor
    if created_tutor_id:
        update_data = {
            "telefono": "+50699887799",
            "ocupacion": "Ingeniera",
            "direccion": "San José, Costa Rica"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/tutores/{created_tutor_id}",
                headers=auth_headers,
                json=update_data,
                timeout=10
            )

            success = response.status_code == 200
            print_test_info("Actualizar tutor", "SUCCESS" if success else "FAILED", response.json())

            if not success:
                return False

        except Exception as e:
            print_test_info("Actualizar tutor", "ERROR", error=str(e))
            return False

    return True


def test_tutores_endpoints_adicionales():
    """Probar endpoints adicionales de tutores"""
    global token

    if not token:
        print_test_info("Endpoints adicionales", "FAILED", error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener tutores activos
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores/activos",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test_info("Tutores activos", "SUCCESS" if success else "FAILED", {
            "total_activos": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

        if not success:
            return False

    except Exception as e:
        print_test_info("Tutores activos", "ERROR", error=str(e))
        return False

    # 2. Obtener estadísticas
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores/estadisticas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        print_test_info("Estadísticas de tutores", "SUCCESS" if success else "FAILED", response.json())

        if not success:
            return False

    except Exception as e:
        print_test_info("Estadísticas de tutores", "ERROR", error=str(e))
        return False

    # 3. Obtener personas disponibles para tutor
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores/personas-disponibles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test_info("Personas disponibles para tutor", "SUCCESS" if success else "FAILED", {
            "total_disponibles": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

        if not success:
            return False

    except Exception as e:
        print_test_info("Personas disponibles para tutor", "ERROR", error=str(e))
        return False

    return True


def test_tutores_validations():
    """Probar validaciones de tutores"""
    global token, created_tutor_cedula

    if not token:
        print_test_info("Validaciones", "FAILED", error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Tutor con campos faltantes
    invalid_tutor_data = {
        # nombre faltante
        "apellido": "Test",
        "parentesco": "madre"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=invalid_tutor_data,
            timeout=10
        )

        success = response.status_code == 400
        print_test_info("Validacion campos faltantes", "SUCCESS" if success else "FAILED", response.json())

        if not success:
            return False

    except Exception as e:
        print_test_info("Validacion campos faltantes", "ERROR", error=str(e))
        return False

    # 2. Tutor con cédula inválida
    invalid_cedula_data = {
        "nombre": "Test",
        "apellido": "User",
        "cedula": "123",  # Cédula muy corta
        "parentesco": "padre"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=invalid_cedula_data,
            timeout=10
        )

        success = response.status_code == 400
        print_test_info("Validacion cedula invalida", "SUCCESS" if success else "FAILED", response.json())

        if not success:
            return False

    except Exception as e:
        print_test_info("Validacion cedula invalida", "ERROR", error=str(e))
        return False

    # 3. Parentesco inválido
    invalid_parentesco_data = {
        "persona_id": 1,
        "parentesco": "parentesco_inexistente"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=invalid_parentesco_data,
            timeout=10
        )

        success = response.status_code == 400
        print_test_info("Validacion parentesco invalido", "SUCCESS" if success else "FAILED", response.json())

        if not success:
            return False

    except Exception as e:
        print_test_info("Validacion parentesco invalido", "ERROR", error=str(e))
        return False

    # 4. Tutor con cédula duplicada (usar la misma cédula del tutor creado)
    if created_tutor_cedula:
        duplicate_tutor_data = {
            "nombre": "Otro",
            "apellido": "Tutor",
            "cedula": created_tutor_cedula,  # Misma cédula
            "parentesco": "padre"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/tutores",
                headers=auth_headers,
                json=duplicate_tutor_data,
                timeout=10
            )

            success = response.status_code == 400
            print_test_info("Validacion cedula duplicada", "SUCCESS" if success else "FAILED", response.json())

            if not success:
                return False

        except Exception as e:
            print_test_info("Validacion cedula duplicada", "ERROR", error=str(e))
            return False

    # 5. Dirección muy larga
    long_address_data = {
        "nombre": "Test",
        "apellido": "User",
        "cedula": "9988776655",
        "parentesco": "madre",
        "direccion": "A" * 256  # Más de 255 caracteres
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=long_address_data,
            timeout=10
        )

        success = response.status_code == 400
        print_test_info("Validacion direccion muy larga", "SUCCESS" if success else "FAILED", response.json())

        if not success:
            return False

    except Exception as e:
        print_test_info("Validacion direccion muy larga", "ERROR", error=str(e))
        return False

    return True


def test_delete_tutor():
    """Probar eliminación de tutor"""
    global token, created_tutor_id

    if not token:
        print_test_info("Eliminacion", "FAILED", error="No hay token disponible")
        raise Exception("No hay token disponible para eliminacion")

    if not created_tutor_id:
        print_test_info("Eliminacion", "FAILED", error="No hay tutor creado")
        raise Exception("No hay tutor creado para eliminar")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Eliminar tutor creado en las pruebas
    try:
        print_test_info("Eliminacion", "INFO", {"attempting_delete": created_tutor_id})

        response = requests.delete(
            f"{BASE_URL}/api/tutores/{created_tutor_id}",
            headers=auth_headers,
            timeout=10
        )

        response_data = response.json() if response.headers.get('content-type', '').startswith(
            'application/json') else {"text": response.text}

        print_test_info("Eliminar tutor", "INFO", {
            "status_code": response.status_code,
            "response": response_data
        })

        # Casos válidos para eliminación:
        # 1. Eliminación exitosa (200)
        # 2. Tutor ya estaba inactivo (400 con mensaje específico)
        if response.status_code == 200:
            print_test_info("Eliminar tutor", "SUCCESS", {"message": "Tutor eliminado exitosamente"})
        elif (response.status_code == 400 and
              response_data.get("message", "").lower().find("ya está inactivo") != -1):
            print_test_info("Eliminar tutor", "SUCCESS", {"message": "Tutor ya estaba inactivo (válido)"})
        else:
            raise Exception(f"Delete failed: status={response.status_code}, response={response_data}")

    except Exception as e:
        if "Delete failed:" in str(e):
            raise e
        print_test_info("Eliminar tutor", "ERROR", error=str(e))
        raise Exception(f"Error eliminando tutor: {str(e)}")

    # Intentar eliminar tutor que no existe
    try:
        response = requests.delete(
            f"{BASE_URL}/api/tutores/99999",
            headers=auth_headers,
            timeout=10
        )

        response_data = response.json() if response.headers.get('content-type', '').startswith(
            'application/json') else {"text": response.text}

        print_test_info("Validacion eliminar inexistente", "INFO", {
            "status_code": response.status_code,
            "expected": 404,
            "response": response_data
        })

        # Casos válidos para tutor inexistente:
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
    config.bar_style = "modern"  # modern, classic, dots, blocks, arrows
    config.show_eta = True
    config.show_individual_times = True
    config.colored_output = True
    config.detailed_summary = True
    config.export_results = True
    config.export_path = "results_tutores.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("TUTORES", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (setup_test_data, "Configuracion de datos"),
        (test_tutores_crud, "CRUD de tutores"),
        (test_tutores_endpoints_adicionales, "Endpoints adicionales"),
        (test_tutores_validations, "Validaciones"),
        (test_delete_tutor, "Eliminacion")
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