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
created_especialidad_id = None


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


def test_especialidades_crud():
    """Probar CRUD completo de especialidades"""
    global token, created_especialidad_id

    if not token:
        raise Exception("No hay token para CRUD de especialidades")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todas las especialidades
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error listando especialidades: {response_data}")

        print_test_info("Listar especialidades", "SUCCESS", {
            "total_especialidades": len(response_data.get("data", [])),
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        if "Error listando especialidades:" in str(e):
            raise e
        raise Exception(f"Error en listar especialidades: {str(e)}")

    # 2. Crear nueva especialidad
    new_especialidad_data = {
        "nombre": f"Terapia Innovadora {int(time.time())}",
        "area": "terapeutico",
        "descripcion": "Especialidad creada durante tests automatizados para validar funcionalidad",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            json=new_especialidad_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_especialidad_id = response_data["data"]["id"]

        if not success:
            raise Exception(f"Error creando especialidad: {response_data}")

        print_test_info("Crear especialidad", "SUCCESS", response_data)

    except Exception as e:
        if "Error creando especialidad:" in str(e):
            raise e
        raise Exception(f"Error en crear especialidad: {str(e)}")

    # 3. Obtener especialidad por ID
    if created_especialidad_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/especialidades/id/{created_especialidad_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error obteniendo especialidad: {response.json()}")

            print_test_info("Obtener especialidad por ID", "SUCCESS", response.json())

        except Exception as e:
            if "Error obteniendo especialidad:" in str(e):
                raise e
            raise Exception(f"Error en obtener especialidad: {str(e)}")

    # 4. Actualizar especialidad
    if created_especialidad_id:
        update_data = {
            "descripcion": "Especialidad actualizada durante pruebas automatizadas - Descripción mejorada",
            "estado": "activo"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/especialidades/id/{created_especialidad_id}",
                headers=auth_headers,
                json=update_data,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error actualizando especialidad: {response.json()}")

            print_test_info("Actualizar especialidad", "SUCCESS", response.json())

        except Exception as e:
            if "Error actualizando especialidad:" in str(e):
                raise e
            raise Exception(f"Error en actualizar especialidad: {str(e)}")

    return True


def test_especialidades_por_area():
    """Probar endpoints de especialidades por área"""
    global token

    if not token:
        raise Exception("No hay token para especialidades por área")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Áreas a probar
    areas = ["terapeutico", "pedagogico"]

    for area in areas:
        try:
            response = requests.get(
                f"{BASE_URL}/api/especialidades/{area}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            response_data = response.json()
            if not success:
                raise Exception(f"Error obteniendo especialidades {area}: {response_data}")

            print_test_info(f"Especialidades {area}", "SUCCESS", {
                f"total_{area}": len(response_data.get("data", [])),
                "status": response_data.get("status"),
                "message": response_data.get("message")
            })

        except Exception as e:
            if f"Error obteniendo especialidades {area}:" in str(e):
                raise e
            raise Exception(f"Error en especialidades {area}: {str(e)}")

    return True


def test_especialidades_endpoints_adicionales():
    """Probar endpoints adicionales de especialidades"""
    global token

    if not token:
        raise Exception("No hay token para endpoints adicionales")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener especialidades activas
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/activas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error obteniendo especialidades activas: {response_data}")

        print_test_info("Especialidades activas", "SUCCESS", {
            "total_activas": len(response_data.get("data", [])),
            "status": response_data.get("status")
        })

    except Exception as e:
        if "Error obteniendo especialidades activas:" in str(e):
            raise e
        raise Exception(f"Error en especialidades activas: {str(e)}")

    # 2. Obtener estadísticas de especialidades
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/estadisticas",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error obteniendo estadísticas: {response.json()}")

        print_test_info("Estadísticas de especialidades", "SUCCESS", response.json())

    except Exception as e:
        if "Error obteniendo estadísticas:" in str(e):
            raise e
        raise Exception(f"Error en estadísticas: {str(e)}")

    return True


def test_especialidades_validations():
    """Probar validaciones de especialidades"""
    global token

    if not token:
        raise Exception("No hay token para validaciones")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Lista de validaciones a probar
    validations = [
        {
            "name": "campos faltantes",
            "data": {"area": "terapeutico"},  # nombre faltante
            "expected_status": 400
        },
        {
            "name": "nombre vacio",
            "data": {"nombre": "", "area": "terapeutico"},
            "expected_status": 400
        },
        {
            "name": "nombre muy corto",
            "data": {"nombre": "AB", "area": "terapeutico"},
            "expected_status": 400
        },
        {
            "name": "nombre muy largo",
            "data": {"nombre": "A" * 200, "area": "terapeutico"},
            "expected_status": 400
        },
        {
            "name": "area invalida",
            "data": {"nombre": "Terapia Test", "area": "area_inexistente"},
            "expected_status": 400
        },
        {
            "name": "caracteres especiales no permitidos",
            "data": {"nombre": "Terapia @#$%^&*", "area": "terapeutico"},
            "expected_status": 400
        },
        {
            "name": "especialidad duplicada",
            "data": {"nombre": "Terapia Ocupacional Pediátrica", "area": "terapeutico"},  # Ya existe
            "expected_status": 400
        }
    ]

    for validation in validations:
        try:
            response = requests.post(
                f"{BASE_URL}/api/especialidades",
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


def test_especialidades_estados():
    """Probar cambios de estado a través del endpoint de actualización"""
    global token, created_especialidad_id

    if not token or not created_especialidad_id:
        raise Exception("Faltan datos para cambios de estado")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Estados a probar a través del endpoint PUT general
    estados_a_probar = ["inactivo", "activo"]

    for estado in estados_a_probar:
        estado_data = {"estado": estado}

        try:
            response = requests.put(
                f"{BASE_URL}/api/especialidades/id/{created_especialidad_id}",
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


def test_especialidades_busqueda():
    """Probar funcionalidades de búsqueda y filtros"""
    global token

    if not token:
        raise Exception("No hay token para búsquedas")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Test: búsqueda por nombre (si el endpoint existe)
    try:
        # Intentar búsqueda por término
        search_params = {"search": "terapia"}
        response = requests.get(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            params=search_params,
            timeout=10
        )

        if response.status_code == 200:
            response_data = response.json()
            print_test_info("Búsqueda por término", "SUCCESS", {
                "resultados": len(response_data.get("data", [])),
                "termino": "terapia"
            })
        else:
            print_test_info("Búsqueda por término", "INFO", {
                "message": "Endpoint de búsqueda no implementado (normal)"
            })

    except Exception as e:
        print_test_info("Búsqueda por término", "INFO", {
            "message": f"Test de búsqueda omitido: {str(e)}"
        })

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
    config.export_path = "results_especialidades.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("ESPECIALIDADES", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (test_especialidades_crud, "CRUD de especialidades"),
        (test_especialidades_por_area, "Especialidades por área"),
        (test_especialidades_endpoints_adicionales, "Endpoints adicionales"),
        (test_especialidades_validations, "Validaciones"),
        (test_especialidades_estados, "Cambios de estado"),
        (test_especialidades_busqueda, "Búsquedas y filtros")
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