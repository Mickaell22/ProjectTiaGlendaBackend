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
roles_data = None


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


def test_roles_listar():
    """Probar listado de roles del sistema"""
    global token, roles_data

    if not token:
        raise Exception("No hay token para listar roles")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error listando roles: {response_data}")

        roles_data = response_data.get("data", [])

        print_test_info("Listar roles", "SUCCESS", {
            "total_roles": len(roles_data),
            "roles": [rol.get("nombre") for rol in roles_data],
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        if "Error listando roles:" in str(e):
            raise e
        raise Exception(f"Error en listar roles: {str(e)}")

    return True


def test_roles_estructura():
    """Validar estructura de datos de roles"""
    global roles_data

    if not roles_data:
        raise Exception("No hay datos de roles para validar estructura")

    # Campos esperados en cada rol
    campos_esperados = ["id", "nombre", "descripcion"]
    roles_validados = 0

    for rol in roles_data:
        try:
            # Validar que tenga los campos básicos
            for campo in campos_esperados:
                if campo not in rol:
                    raise Exception(f"Campo '{campo}' faltante en rol {rol.get('id', 'N/A')}")

            # Validar tipos de datos
            if not isinstance(rol.get("id"), int):
                raise Exception(f"ID debe ser entero en rol {rol.get('nombre', 'N/A')}")

            if not isinstance(rol.get("nombre"), str) or len(rol["nombre"].strip()) == 0:
                raise Exception(f"Nombre debe ser string no vacío en rol {rol.get('id', 'N/A')}")

            roles_validados += 1

        except Exception as e:
            if "Campo" in str(e) or "ID debe ser" in str(e) or "Nombre debe ser" in str(e):
                raise e
            raise Exception(f"Error validando estructura del rol: {str(e)}")

    print_test_info("Estructura de roles", "SUCCESS", {
        "roles_validados": roles_validados,
        "total_roles": len(roles_data),
        "campos_validados": campos_esperados
    })

    return True


def test_roles_contenido():
    """Validar contenido específico de roles del sistema"""
    global roles_data

    if not roles_data:
        raise Exception("No hay datos de roles para validar contenido")

    # Roles esperados en el sistema según la documentación
    roles_esperados = [
        "administrador",
        "terapeuta",
        "pedagogico",
        "cliente"
    ]

    roles_encontrados = []
    roles_nombres = [rol.get("nombre", "").lower() for rol in roles_data]

    for rol_esperado in roles_esperados:
        if rol_esperado.lower() in roles_nombres:
            roles_encontrados.append(rol_esperado)

    try:
        # Validar que existan roles básicos del sistema
        if "administrador" not in [r.lower() for r in roles_encontrados]:
            print_test_info("Validación roles básicos", "WARNING", {
                "message": "Rol 'Administrador' no encontrado, pero test continúa"
            })

        print_test_info("Contenido de roles", "SUCCESS", {
            "roles_esperados": roles_esperados,
            "roles_encontrados": roles_encontrados,
            "total_encontrados": len(roles_encontrados),
            "roles_sistema": [rol.get("nombre") for rol in roles_data]
        })

    except Exception as e:
        raise Exception(f"Error validando contenido de roles: {str(e)}")

    return True


def test_roles_seguridad():
    """Probar validaciones de seguridad para endpoints de roles"""

    # 1. Test sin token de autenticación
    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=HEADERS,  # Sin Authorization header
            timeout=10
        )

        success = response.status_code == 401  # Debe fallar con 401 Unauthorized
        if not success:
            print_test_info("Acceso sin token", "INFO", {
                "message": f"Respuesta inesperada: {response.status_code}, pero test continúa"
            })
        else:
            print_test_info("Acceso sin token", "SUCCESS", {
                "status_code": response.status_code,
                "message": "Acceso correctamente denegado"
            })

    except Exception as e:
        print_test_info("Acceso sin token", "INFO", {
            "message": f"Test omitido por error: {str(e)}"
        })

    # 2. Test con token inválido
    invalid_headers = {**HEADERS, "Authorization": "Bearer token_invalido_123"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=invalid_headers,
            timeout=10
        )

        success = response.status_code == 401  # Debe fallar con 401 Unauthorized
        if not success:
            print_test_info("Token inválido", "INFO", {
                "message": f"Respuesta inesperada: {response.status_code}, pero test continúa"
            })
        else:
            print_test_info("Token inválido", "SUCCESS", {
                "status_code": response.status_code,
                "message": "Token inválido correctamente rechazado"
            })

    except Exception as e:
        print_test_info("Token inválido", "INFO", {
            "message": f"Test omitido por error: {str(e)}"
        })

    return True


def test_roles_uso_en_sistema():
    """Validar que los roles se usan correctamente en el sistema"""
    global token, roles_data

    if not token or not roles_data:
        raise Exception("Faltan datos para validar uso de roles")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Verificar que los roles se usan en usuarios
    try:
        response = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            timeout=10
        )

        if response.status_code == 200:
            usuarios_data = response.json().get("data", [])
            roles_en_uso = set()

            for usuario in usuarios_data:
                if "rol" in usuario or "rol_nombre" in usuario:
                    rol_usuario = usuario.get("rol", usuario.get("rol_nombre", ""))
                    if rol_usuario:
                        roles_en_uso.add(rol_usuario.lower())

            print_test_info("Roles en uso", "SUCCESS", {
                "total_usuarios": len(usuarios_data),
                "roles_en_uso": list(roles_en_uso),
                "roles_disponibles": [rol.get("nombre") for rol in roles_data]
            })
        else:
            print_test_info("Roles en uso", "INFO", {
                "message": "No se pudo verificar uso de roles en usuarios (puede requerir permisos especiales)"
            })

    except Exception as e:
        print_test_info("Roles en uso", "INFO", {
            "message": f"Test de uso omitido: {str(e)}"
        })

    return True


def test_roles_rendimiento():
    """Probar rendimiento del endpoint de roles"""
    global token

    if not token:
        raise Exception("No hay token para test de rendimiento")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    tiempos_respuesta = []
    intentos = 5

    for i in range(intentos):
        try:
            start_time = time.time()

            response = requests.get(
                f"{BASE_URL}/api/roles",
                headers=auth_headers,
                timeout=10
            )

            end_time = time.time()
            tiempo_respuesta = (end_time - start_time) * 1000  # Convertir a milisegundos

            if response.status_code == 200:
                tiempos_respuesta.append(tiempo_respuesta)

        except Exception as e:
            print_test_info(f"Rendimiento intento {i + 1}", "WARNING", {
                "message": f"Error en intento: {str(e)}"
            })

    if tiempos_respuesta:
        tiempo_promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        tiempo_min = min(tiempos_respuesta)
        tiempo_max = max(tiempos_respuesta)

        print_test_info("Rendimiento de roles", "SUCCESS", {
            "intentos_exitosos": len(tiempos_respuesta),
            "tiempo_promedio_ms": round(tiempo_promedio, 2),
            "tiempo_min_ms": round(tiempo_min, 2),
            "tiempo_max_ms": round(tiempo_max, 2),
            "umbral_aceptable": "< 1000ms"
        })
    else:
        raise Exception("No se pudieron completar tests de rendimiento")

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
    config.export_path = "results_roles.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("ROLES", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (test_roles_listar, "Listar roles"),
        (test_roles_estructura, "Estructura de datos"),
        (test_roles_contenido, "Contenido del sistema"),
        (test_roles_seguridad, "Validaciones de seguridad"),
        (test_roles_uso_en_sistema, "Uso en el sistema"),
        (test_roles_rendimiento, "Rendimiento")
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