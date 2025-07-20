import requests
import json
import time

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_tutor_id = None
created_persona_id = None


def print_section(title):
    """Imprimir seccion de pruebas"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_test(test_name, success, response_data=None, error=None):
    """Imprimir resultado de prueba"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} - {test_name}")

    if response_data:
        print(f"   Respuesta: {json.dumps(response_data, indent=4, ensure_ascii=False)}")

    if error:
        print(f"   Error: {error}")
    print()


def test_login():
    """Autenticarse para obtener token"""
    global token
    print_section("AUTENTICACION PARA PRUEBAS")

    login_data = {
        "usuario": "admin",
        "contrasenia": "admin123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json=login_data
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("token"):
            token = response_data["data"]["token"]
            print_test("Login para pruebas", True, {"message": "Token obtenido exitosamente"})
            return True
        else:
            print_test("Login para pruebas", False, response_data)
            return False

    except Exception as e:
        print_test("Login para pruebas", False, error=str(e))
        return False


def setup_test_data():
    """Crear datos de prueba necesarios"""
    global token, created_persona_id
    print_section("CONFIGURACION DE DATOS DE PRUEBA")

    if not token:
        print_test("Sin token para setup", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Crear una persona para usar como tutor
    persona_data = {
        "nombre": "Carmen Elena",
        "apellido": "Vargas Solís",
        "cedula": f"99{int(time.time())}",
        "telefono": "+50699887766",
        "correo": f"carmen.vargas.{int(time.time())}@email.com",
        "direccion": "Cartago, Costa Rica",
        "fecha_nacimiento": "1985-06-15"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=persona_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]
            print_test("Crear persona para tutor", True, {"persona_id": created_persona_id})
            return True
        else:
            print_test("Crear persona para tutor", False, response_data)
            return False

    except Exception as e:
        print_test("Crear persona para tutor", False, error=str(e))
        return False


def test_tutores_crud():
    """Probar CRUD completo de tutores"""
    global token, created_tutor_id, created_persona_id
    print_section("CRUD DE TUTORES")

    if not token or not created_persona_id:
        print_test("Sin datos para pruebas", False, error="Faltan datos de configuración")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todos los tutores
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar tutores", success, {
            "total_tutores": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar tutores", False, error=str(e))

    # 2. Crear nuevo tutor
    new_tutor_data = {
        "persona_id": created_persona_id,
        "parentesco": "madre",
        "es_contacto_emergencia": True,
        "observaciones_tutor": "Madre muy colaborativa, disponible en horarios matutinos",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=new_tutor_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_tutor_id = response_data["data"]["id"]

        print_test("Crear tutor", success, response_data)

    except Exception as e:
        print_test("Crear tutor", False, error=str(e))

    # 3. Obtener tutor por ID
    if created_tutor_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/tutores/{created_tutor_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Obtener tutor por ID", success, response.json())

        except Exception as e:
            print_test("Obtener tutor por ID", False, error=str(e))

    # 4. Actualizar tutor
    if created_tutor_id:
        update_data = {
            "es_contacto_emergencia": False,
            "observaciones_tutor": "Madre colaborativa, disponible tardes y fines de semana"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/tutores/{created_tutor_id}",
                headers=auth_headers,
                json=update_data
            )

            success = response.status_code == 200
            print_test("Actualizar tutor", success, response.json())

        except Exception as e:
            print_test("Actualizar tutor", False, error=str(e))


def test_tutores_endpoints_adicionales():
    """Probar endpoints adicionales de tutores"""
    global token
    print_section("ENDPOINTS ADICIONALES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener tutores activos
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores/activos",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Tutores activos", success, {
            "total_activos": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Tutores activos", False, error=str(e))

    # 2. Obtener estadísticas
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores/estadisticas",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Estadísticas de tutores", success, response.json())

    except Exception as e:
        print_test("Estadísticas de tutores", False, error=str(e))

    # 3. Obtener personas disponibles para tutor
    try:
        response = requests.get(
            f"{BASE_URL}/api/tutores/personas-disponibles",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Personas disponibles para tutor", success, {
            "total_disponibles": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Personas disponibles para tutor", False, error=str(e))


def test_tutores_validations():
    """Probar validaciones de tutores"""
    global token
    print_section("VALIDACIONES DE TUTORES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Tutor con campos faltantes
    invalid_tutor_data = {
        # persona_id faltante
        "parentesco": "madre"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=invalid_tutor_data
        )

        success = response.status_code == 400
        print_test("Validacion campos faltantes", success, response.json())

    except Exception as e:
        print_test("Validacion campos faltantes", False, error=str(e))

    # 2. Tutor con persona_id inválido
    invalid_id_data = {
        "persona_id": "no_es_numero",
        "parentesco": "padre"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=invalid_id_data
        )

        success = response.status_code == 400
        print_test("Validacion persona_id invalido", success, response.json())

    except Exception as e:
        print_test("Validacion persona_id invalido", False, error=str(e))

    # 3. Parentesco inválido
    invalid_parentesco_data = {
        "persona_id": 1,
        "parentesco": "parentesco_inexistente"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=invalid_parentesco_data
        )

        success = response.status_code == 400
        print_test("Validacion parentesco invalido", success, response.json())

    except Exception as e:
        print_test("Validacion parentesco invalido", False, error=str(e))

    # 4. Tutor con persona que ya es tutor (usando persona existente)
    if created_persona_id:
        duplicate_tutor_data = {
            "persona_id": created_persona_id,
            "parentesco": "padre"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/tutores",
                headers=auth_headers,
                json=duplicate_tutor_data
            )

            success = response.status_code == 400
            print_test("Validacion persona ya es tutor", success, response.json())

        except Exception as e:
            print_test("Validacion persona ya es tutor", False, error=str(e))

    # 5. Observaciones muy largas
    long_observations_data = {
        "persona_id": 1,
        "parentesco": "madre",
        "observaciones_tutor": "A" * 501  # Más de 500 caracteres
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/tutores",
            headers=auth_headers,
            json=long_observations_data
        )

        success = response.status_code == 400
        print_test("Validacion observaciones muy largas", success, response.json())

    except Exception as e:
        print_test("Validacion observaciones muy largas", False, error=str(e))


def test_delete_tutor():
    """Probar eliminación de tutor"""
    global token, created_tutor_id
    print_section("ELIMINACION DE TUTOR")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    if not created_tutor_id:
        print_test("Sin tutor para eliminar", False, error="No hay tutor creado")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Eliminar tutor creado en las pruebas
    try:
        response = requests.delete(
            f"{BASE_URL}/api/tutores/{created_tutor_id}",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Eliminar tutor", success, response.json())

    except Exception as e:
        print_test("Eliminar tutor", False, error=str(e))

    # Intentar eliminar tutor que no existe
    try:
        response = requests.delete(
            f"{BASE_URL}/api/tutores/99999",
            headers=auth_headers
        )

        success = response.status_code == 404
        print_test("Validacion eliminar tutor inexistente", success, response.json())

    except Exception as e:
        print_test("Validacion eliminar tutor inexistente", False, error=str(e))


def run_all_tests():
    """Ejecutar todas las pruebas de tutores"""
    print("INICIO DE PRUEBAS DEL MODULO DE TUTORES")
    print("=" * 60)

    # Ejecutar pruebas en orden
    tests = [
        test_login,
        setup_test_data,
        test_tutores_crud,
        test_tutores_endpoints_adicionales,
        test_tutores_validations,
        test_delete_tutor
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            result = test()
            if result is not False:
                passed += 1
        except Exception as e:
            print(f"Error ejecutando prueba: {e}")

    print_section("RESUMEN DE PRUEBAS")
    print(f"Pruebas ejecutadas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {total - passed}")
    print(f"Porcentaje de exito: {(passed / total) * 100:.1f}%")


if __name__ == "__main__":
    # Verificar que el servidor este corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            run_all_tests()
        else:
            print("Error: El servidor no responde correctamente")
    except Exception as e:
        print(f"Error: No se pudo conectar al servidor en {BASE_URL}")
        print(f"Asegurate de que el servidor este corriendo con: python app.py")
        print(f"Error detallado: {e}")