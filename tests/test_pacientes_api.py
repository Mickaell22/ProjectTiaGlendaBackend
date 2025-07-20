import requests
import json
import time
from datetime import date, timedelta

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_paciente_id = None
created_persona_id = None
created_tutor_id = None


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
    global token, created_persona_id, created_tutor_id
    print_section("CONFIGURACION DE DATOS DE PRUEBA")

    if not token:
        print_test("Sin token para setup", False, error="No hay token disponible")
        return False

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
            json=tutor_persona_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            tutor_persona_id = response_data["data"]["id"]
            print_test("Crear persona para tutor", True, {"persona_id": tutor_persona_id})
        else:
            print_test("Crear persona para tutor", False, response_data)
            return False

    except Exception as e:
        print_test("Crear persona para tutor", False, error=str(e))
        return False

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
            json=tutor_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_tutor_id = response_data["data"]["id"]
            print_test("Crear tutor", True, {"tutor_id": created_tutor_id})
        else:
            print_test("Crear tutor", False, response_data)
            return False

    except Exception as e:
        print_test("Crear tutor", False, error=str(e))
        return False

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
            json=paciente_persona_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]
            print_test("Crear persona para paciente", True, {"persona_id": created_persona_id})
            return True
        else:
            print_test("Crear persona para paciente", False, response_data)
            return False

    except Exception as e:
        print_test("Crear persona para paciente", False, error=str(e))
        return False


def test_pacientes_crud():
    """Probar CRUD completo de pacientes"""
    global token, created_paciente_id, created_persona_id, created_tutor_id
    print_section("CRUD DE PACIENTES")

    if not token or not created_persona_id or not created_tutor_id:
        print_test("Sin datos para pruebas", False, error="Faltan datos de configuración")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todos los pacientes
    try:
        response = requests.get(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar pacientes", success, {
            "total_pacientes": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar pacientes", False, error=str(e))

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
            json=new_paciente_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_paciente_id = response_data["data"]["id"]

        print_test("Crear paciente", success, response_data)

    except Exception as e:
        print_test("Crear paciente", False, error=str(e))

    # 3. Obtener paciente por ID
    if created_paciente_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Obtener paciente por ID", success, response.json())

        except Exception as e:
            print_test("Obtener paciente por ID", False, error=str(e))

    # 4. Actualizar paciente
    if created_paciente_id:
        update_data = {
            "observaciones": "Paciente con excelente progreso en terapia ocupacional. Muy colaborativo y motivado."
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}",
                headers=auth_headers,
                json=update_data
            )

            success = response.status_code == 200
            print_test("Actualizar paciente", success, response.json())

        except Exception as e:
            print_test("Actualizar paciente", False, error=str(e))

    # 5. Cambiar estado del paciente
    if created_paciente_id:
        estado_data = {
            "estado": "inactivo"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}/estado",
                headers=auth_headers,
                json=estado_data
            )

            success = response.status_code == 200
            print_test("Cambiar estado paciente", success, response.json())

        except Exception as e:
            print_test("Cambiar estado paciente", False, error=str(e))


def test_pacientes_endpoints_adicionales():
    """Probar endpoints adicionales de pacientes"""
    global token, created_tutor_id
    print_section("ENDPOINTS ADICIONALES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener pacientes por tutor
    if created_tutor_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/pacientes/tutor/{created_tutor_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            response_data = response.json()
            print_test("Pacientes por tutor", success, {
                "total_pacientes": len(response_data.get("data", [])) if success else 0,
                "status": response_data.get("status")
            })

        except Exception as e:
            print_test("Pacientes por tutor", False, error=str(e))

    # 2. Obtener estadísticas
    try:
        response = requests.get(
            f"{BASE_URL}/api/pacientes/estadisticas",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Estadísticas de pacientes", success, response.json())

    except Exception as e:
        print_test("Estadísticas de pacientes", False, error=str(e))

    # 3. Obtener personas disponibles para paciente
    try:
        response = requests.get(
            f"{BASE_URL}/api/pacientes/personas-disponibles",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Personas disponibles para paciente", success, {
            "total_disponibles": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status")
        })

    except Exception as e:
        print_test("Personas disponibles para paciente", False, error=str(e))


def test_pacientes_validations():
    """Probar validaciones de pacientes"""
    global token
    print_section("VALIDACIONES DE PACIENTES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Paciente con campos faltantes
    invalid_paciente_data = {
        # persona_id faltante
        "tutor_id": 1,
        "fecha_ingreso": "2024-01-15"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers,
            json=invalid_paciente_data
        )

        success = response.status_code == 400
        print_test("Validacion campos faltantes", success, response.json())

    except Exception as e:
        print_test("Validacion campos faltantes", False, error=str(e))

    # 2. Paciente con IDs inválidos
    invalid_id_data = {
        "persona_id": "no_es_numero",
        "tutor_id": "tampoco_es_numero",
        "fecha_ingreso": "2024-01-15"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers,
            json=invalid_id_data
        )

        success = response.status_code == 400
        print_test("Validacion IDs invalidos", success, response.json())

    except Exception as e:
        print_test("Validacion IDs invalidos", False, error=str(e))

    # 3. Fecha de ingreso futura
    future_date = (date.today() + timedelta(days=30)).isoformat()
    future_date_data = {
        "persona_id": 1,
        "tutor_id": 1,
        "fecha_ingreso": future_date
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers,
            json=future_date_data
        )

        success = response.status_code == 400
        print_test("Validacion fecha futura", success, response.json())

    except Exception as e:
        print_test("Validacion fecha futura", False, error=str(e))

    # 4. Paciente con persona que ya es paciente (usando persona existente)
    if created_persona_id:
        duplicate_paciente_data = {
            "persona_id": created_persona_id,
            "tutor_id": 1,
            "fecha_ingreso": "2024-01-15"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/api/pacientes",
                headers=auth_headers,
                json=duplicate_paciente_data
            )

            success = response.status_code == 400
            print_test("Validacion persona ya es paciente", success, response.json())

        except Exception as e:
            print_test("Validacion persona ya es paciente", False, error=str(e))

    # 5. Observaciones muy largas
    long_observations_data = {
        "persona_id": 1,
        "tutor_id": 1,
        "fecha_ingreso": "2024-01-15",
        "observaciones": "A" * 1001  # Más de 1000 caracteres
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/pacientes",
            headers=auth_headers,
            json=long_observations_data
        )

        success = response.status_code == 400
        print_test("Validacion observaciones muy largas", success, response.json())

    except Exception as e:
        print_test("Validacion observaciones muy largas", False, error=str(e))

    # 6. Estado inválido
    invalid_state_data = {
        "estado": "estado_inexistente"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/api/pacientes/1/estado",
            headers=auth_headers,
            json=invalid_state_data
        )

        success = response.status_code == 400
        print_test("Validacion estado invalido", success, response.json())

    except Exception as e:
        print_test("Validacion estado invalido", False, error=str(e))


def test_pacientes_estados():
    """Probar cambios de estado específicos"""
    global token, created_paciente_id
    print_section("CAMBIOS DE ESTADO")

    if not token or not created_paciente_id:
        print_test("Sin datos para pruebas", False, error="Faltan datos de configuración")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Probar diferentes estados
    estados_a_probar = ["activo", "alta", "derivado"]

    for estado in estados_a_probar:
        estado_data = {"estado": estado}

        try:
            response = requests.put(
                f"{BASE_URL}/api/pacientes/{created_paciente_id}/estado",
                headers=auth_headers,
                json=estado_data
            )

            success = response.status_code == 200
            print_test(f"Cambiar estado a {estado}", success, response.json())

        except Exception as e:
            print_test(f"Cambiar estado a {estado}", False, error=str(e))


def run_all_tests():
    """Ejecutar todas las pruebas de pacientes"""
    print("INICIO DE PRUEBAS DEL MODULO DE PACIENTES")
    print("=" * 60)

    # Ejecutar pruebas en orden
    tests = [
        test_login,
        setup_test_data,
        test_pacientes_crud,
        test_pacientes_endpoints_adicionales,
        test_pacientes_validations,
        test_pacientes_estados
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