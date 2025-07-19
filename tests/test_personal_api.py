import requests
import json
import time

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_personal_id = None
created_persona_id = None
test_especialidad_id = None


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
    global token, created_persona_id, test_especialidad_id
    print_section("CONFIGURACION DE DATOS DE PRUEBA")

    if not token:
        print_test("Sin token para setup", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Crear una persona para usar como personal
    persona_data = {
        "nombre": "Juan Carlos",
        "apellido": "Pérez",
        "cedula": f"77{int(time.time())}",
        "telefono": "+50677889900",
        "correo": f"juan.perez.{int(time.time())}@email.com",
        "direccion": "San José, Costa Rica",
        "fecha_nacimiento": "1985-03-15"
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
            print_test("Crear persona para personal", True, {"persona_id": created_persona_id})
        else:
            print_test("Crear persona para personal", False, response_data)
            return False

    except Exception as e:
        print_test("Crear persona para personal", False, error=str(e))
        return False

    # Obtener una especialidad existente para pruebas
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/activas",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data") and len(response_data["data"]) > 0:
            test_especialidad_id = response_data["data"][0]["id"]
            print_test("Obtener especialidad para pruebas", True, {"especialidad_id": test_especialidad_id})
            return True
        else:
            print_test("Obtener especialidad para pruebas", False, response_data)
            return False

    except Exception as e:
        print_test("Obtener especialidad para pruebas", False, error=str(e))
        return False


def test_personal_crud():
    """Probar CRUD completo de personal"""
    global token, created_personal_id, created_persona_id
    print_section("CRUD DE PERSONAL")

    if not token or not created_persona_id:
        print_test("Sin datos para pruebas", False, error="Faltan datos de configuración")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todo el personal
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar personal", success, {
            "total_personal": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar personal", False, error=str(e))

    # 2. Crear nuevo personal
    new_personal_data = {
        "persona_id": created_persona_id,
        "titulo_profesional": "Licenciatura en Terapia Ocupacional",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personal",
            headers=auth_headers,
            json=new_personal_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_personal_id = response_data["data"]["id"]

        print_test("Crear personal", success, response_data)

    except Exception as e:
        print_test("Crear personal", False, error=str(e))

    # 3. Obtener personal por ID
    if created_personal_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/personal/{created_personal_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Obtener personal por ID", success, response.json())

        except Exception as e:
            print_test("Obtener personal por ID", False, error=str(e))

    # 4. Actualizar personal
    if created_personal_id:
        update_data = {
            "titulo_profesional": "Maestría en Terapia Ocupacional Pediátrica"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/personal/{created_personal_id}",
                headers=auth_headers,
                json=update_data
            )

            success = response.status_code == 200
            print_test("Actualizar personal", success, response.json())

        except Exception as e:
            print_test("Actualizar personal", False, error=str(e))


def test_personal_especialidades():
    """Probar gestión de especialidades del personal"""
    global token, created_personal_id, test_especialidad_id
    print_section("ESPECIALIDADES DEL PERSONAL")

    if not token or not created_personal_id or not test_especialidad_id:
        print_test("Sin datos para pruebas", False, error="Faltan datos de configuración")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener especialidades del personal (debería estar vacío inicialmente)
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Obtener especialidades iniciales", success, {
            "total_especialidades": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Obtener especialidades iniciales", False, error=str(e))

    # 2. Asignar especialidad al personal
    assign_data = {
        "especialidad_id": test_especialidad_id
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers,
            json=assign_data
        )

        success = response.status_code == 200
        print_test("Asignar especialidad", success, response.json())

    except Exception as e:
        print_test("Asignar especialidad", False, error=str(e))

    # 3. Verificar que la especialidad fue asignada
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Verificar especialidad asignada", success, {
            "total_especialidades": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Verificar especialidad asignada", False, error=str(e))

    # 4. Intentar asignar la misma especialidad (debería fallar)
    try:
        response = requests.post(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades",
            headers=auth_headers,
            json=assign_data
        )

        success = response.status_code == 400
        print_test("Validacion especialidad duplicada", success, response.json())

    except Exception as e:
        print_test("Validacion especialidad duplicada", False, error=str(e))

    # 5. Quitar especialidad del personal
    try:
        response = requests.delete(
            f"{BASE_URL}/api/personal/{created_personal_id}/especialidades/{test_especialidad_id}",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Quitar especialidad", success, response.json())

    except Exception as e:
        print_test("Quitar especialidad", False, error=str(e))


def test_personal_endpoints_adicionales():
    """Probar endpoints adicionales de personal"""
    global token
    print_section("ENDPOINTS ADICIONALES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Personal por área - Terapéutico
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/area/terapeutico",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Personal terapéutico", success, {
            "total_terapeutico": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Personal terapéutico", False, error=str(e))

    # 2. Personal por área - Pedagógico
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/area/pedagogico",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Personal pedagógico", success, {
            "total_pedagogico": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Personal pedagógico", False, error=str(e))

    # 3. Estadísticas del personal
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/estadisticas",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Estadísticas del personal", success, response.json())

    except Exception as e:
        print_test("Estadísticas del personal", False, error=str(e))


def test_personal_validations():
    """Probar validaciones de personal"""
    global token
    print_section("VALIDACIONES DE PERSONAL")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Personal con campos faltantes
    invalid_personal_data = {
        # persona_id faltante
        "titulo_profesional": "Licenciatura Test"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personal",
            headers=auth_headers,
            json=invalid_personal_data
        )

        success = response.status_code == 400
        print_test("Validacion campos faltantes", success, response.json())

    except Exception as e:
        print_test("Validacion campos faltantes", False, error=str(e))

    # 2. Personal con persona_id inválido
    invalid_id_data = {
        "persona_id": "no_es_numero",
        "titulo_profesional": "Licenciatura Test"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personal",
            headers=auth_headers,
            json=invalid_id_data
        )

        success = response.status_code == 400
        print_test("Validacion persona_id invalido", success, response.json())

    except Exception as e:
        print_test("Validacion persona_id invalido", False, error=str(e))

    # 3. Personal con persona que ya es personal (usando persona existente)
    if created_persona_id:
        duplicate_personal_data = {
            "persona_id": created_persona_id,
            "titulo_profesional": "Otra Licenciatura"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/personal",
                headers=auth_headers,
                json=duplicate_personal_data
            )

            success = response.status_code == 400
            print_test("Validacion persona ya es personal", success, response.json())

        except Exception as e:
            print_test("Validacion persona ya es personal", False, error=str(e))

    # 4. Área inválida en endpoint
    try:
        response = requests.get(
            f"{BASE_URL}/api/personal/area/area_inexistente",
            headers=auth_headers
        )

        success = response.status_code == 400
        print_test("Validacion area invalida", success, response.json())

    except Exception as e:
        print_test("Validacion area invalida", False, error=str(e))


def test_delete_personal():
    """Probar eliminación de personal"""
    global token, created_personal_id
    print_section("ELIMINACION DE PERSONAL")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    if not created_personal_id:
        print_test("Sin personal para eliminar", False, error="No hay personal creado")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Eliminar personal creado en las pruebas
    try:
        response = requests.delete(
            f"{BASE_URL}/api/personal/{created_personal_id}",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Eliminar personal", success, response.json())

    except Exception as e:
        print_test("Eliminar personal", False, error=str(e))


def run_all_tests():
    """Ejecutar todas las pruebas de personal"""
    print("INICIO DE PRUEBAS DEL MODULO DE PERSONAL")
    print("=" * 60)

    # Ejecutar pruebas en orden
    tests = [
        test_login,
        setup_test_data,
        test_personal_crud,
        test_personal_especialidades,
        test_personal_endpoints_adicionales,
        test_personal_validations,
        test_delete_personal
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