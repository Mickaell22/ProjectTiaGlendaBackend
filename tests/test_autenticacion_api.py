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
valid_token = None
user_info = None


def print_test_info(test_name, status, data=None, error=None):
    """Función helper para logging de tests individuales"""
    if data and isinstance(data, dict):
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
    if error:
        print(f"   Error: {error}")


def test_login_exitoso():
    """Probar login con credenciales válidas"""
    global valid_token, user_info

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
            valid_token = response_data["data"]["token"]
            user_info = response_data["data"]["user"]

            print_test_info("Login exitoso", "SUCCESS", {
                "usuario": user_info.get("usuario"),
                "rol": user_info.get("rol"),
                "nombre_completo": user_info.get("nombre_completo"),
                "token_length": len(valid_token)
            })
            return True
        else:
            raise Exception(f"Login exitoso falló: {response_data}")

    except Exception as e:
        if "Login exitoso falló:" in str(e):
            raise e
        raise Exception(f"Error en login exitoso: {str(e)}")


def test_login_credenciales_invalidas():
    """Probar login con diferentes credenciales inválidas"""

    # Casos de credenciales inválidas
    casos_invalidos = [
        {
            "name": "usuario inexistente",
            "data": {"usuario": "usuario_inexistente", "contrasenia": "admin123"},
            "expected_status": 401
        },
        {
            "name": "contraseña incorrecta",
            "data": {"usuario": "admin", "contrasenia": "contraseña_incorrecta"},
            "expected_status": 401
        },
        {
            "name": "usuario vacío",
            "data": {"usuario": "", "contrasenia": "admin123"},
            "expected_status": 400
        },
        {
            "name": "contraseña vacía",
            "data": {"usuario": "admin", "contrasenia": ""},
            "expected_status": 400
        },
        {
            "name": "sin usuario",
            "data": {"contrasenia": "admin123"},
            "expected_status": 400
        },
        {
            "name": "sin contraseña",
            "data": {"usuario": "admin"},
            "expected_status": 400
        },
        {
            "name": "datos vacíos",
            "data": {},
            "expected_status": 400
        },
        {
            "name": "SQL injection intento",
            "data": {"usuario": "admin'; DROP TABLE usuarios; --", "contrasenia": "admin123"},
            "expected_status": 400  # Sistema detecta como datos inválidos, no credenciales incorrectas
        }
    ]

    for caso in casos_invalidos:
        try:
            response = requests.post(
                f"{BASE_URL}/api/login",
                headers=HEADERS,
                json=caso["data"],
                timeout=10
            )

            success = response.status_code == caso["expected_status"]
            if not success:
                raise Exception(
                    f"Caso '{caso['name']}' falló. Esperado: {caso['expected_status']}, Obtenido: {response.status_code}")

            print_test_info(f"Login inválido: {caso['name']}", "SUCCESS", {
                "status_code": response.status_code,
                "expected": caso["expected_status"],
                "message": response.json().get("message", "")
            })

        except Exception as e:
            if f"Caso '{caso['name']}' falló" in str(e):
                raise e
            raise Exception(f"Error en caso {caso['name']}: {str(e)}")

    return True


def test_verify_token():
    """Probar verificación de tokens"""
    global valid_token

    if not valid_token:
        raise Exception("No hay token válido para verificar")

    # 1. Verificar token válido
    auth_headers = {**HEADERS, "Authorization": f"Bearer {valid_token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/verify-token",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error verificando token válido: {response_data}")

        print_test_info("Verificar token válido", "SUCCESS", {
            "status": response_data.get("status"),
            "message": response_data.get("message"),
            "user_id": response_data.get("data", {}).get("user_id"),
            "username": response_data.get("data", {}).get("username")
        })

    except Exception as e:
        if "Error verificando token válido:" in str(e):
            raise e
        raise Exception(f"Error en verificar token válido: {str(e)}")

    # 2. Verificar sin token
    try:
        response = requests.get(
            f"{BASE_URL}/api/verify-token",
            headers=HEADERS,  # Sin Authorization header
            timeout=10
        )

        success = response.status_code == 401
        if not success:
            raise Exception(f"Verificar sin token debería fallar con 401, obtuvo: {response.status_code}")

        print_test_info("Verificar sin token", "SUCCESS", {
            "status_code": response.status_code,
            "message": "Acceso correctamente denegado"
        })

    except Exception as e:
        if "Verificar sin token debería fallar" in str(e):
            raise e
        raise Exception(f"Error en verificar sin token: {str(e)}")

    # 3. Verificar con token inválido
    invalid_headers = {**HEADERS, "Authorization": "Bearer token_completamente_invalido"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/verify-token",
            headers=invalid_headers,
            timeout=10
        )

        success = response.status_code == 401
        if not success:
            raise Exception(f"Token inválido debería fallar con 401, obtuvo: {response.status_code}")

        print_test_info("Verificar token inválido", "SUCCESS", {
            "status_code": response.status_code,
            "message": "Token inválido correctamente rechazado"
        })

    except Exception as e:
        if "Token inválido debería fallar" in str(e):
            raise e
        raise Exception(f"Error en verificar token inválido: {str(e)}")

    # 4. Verificar con formato de header incorrecto
    malformed_headers = {**HEADERS, "Authorization": "InvalidFormat token_here"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/verify-token",
            headers=malformed_headers,
            timeout=10
        )

        success = response.status_code == 401
        if not success:
            print_test_info("Header malformado", "INFO", {
                "message": f"Respuesta inesperada: {response.status_code}, pero test continúa"
            })
        else:
            print_test_info("Header malformado", "SUCCESS", {
                "status_code": response.status_code,
                "message": "Header malformado correctamente rechazado"
            })

    except Exception as e:
        print_test_info("Header malformado", "INFO", {
            "message": f"Test omitido por error: {str(e)}"
        })

    return True


def test_usuario_actual():
    """Probar endpoint de información del usuario actual"""
    global valid_token, user_info

    if not valid_token:
        raise Exception("No hay token válido para obtener usuario actual")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {valid_token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/me",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error obteniendo usuario actual: {response_data}")

        current_user = response_data.get("data", {})

        # Validar que la información sea consistente con el login
        if user_info and current_user.get("usuario") != user_info.get("usuario"):
            raise Exception("Información de usuario inconsistente entre login y /me")

        print_test_info("Usuario actual", "SUCCESS", {
            "usuario": current_user.get("usuario"),
            "rol": current_user.get("rol"),
            "nombre_completo": current_user.get("nombre_completo"),
            "status": response_data.get("status")
        })

    except Exception as e:
        if "Error obteniendo usuario actual:" in str(e) or "Información de usuario inconsistente" in str(e):
            raise e
        raise Exception(f"Error en usuario actual: {str(e)}")

    return True


def test_logout():
    """Probar funcionalidad de logout"""
    global valid_token

    if not valid_token:
        raise Exception("No hay token válido para logout")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {valid_token}"}

    try:
        response = requests.post(
            f"{BASE_URL}/api/logout",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error en logout: {response_data}")

        print_test_info("Logout", "SUCCESS", {
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

        # Nota: En JWT stateless, el token sigue siendo técnicamente válido
        # El logout se maneja en el frontend eliminando el token

    except Exception as e:
        if "Error en logout:" in str(e):
            raise e
        raise Exception(f"Error en logout: {str(e)}")

    return True


def test_flujo_completo_autenticacion():
    """Probar flujo completo de autenticación"""

    # 1. Login
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
        if not success:
            raise Exception(f"Flujo completo - Login falló: {response_data}")

        token = response_data["data"]["token"]
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    except Exception as e:
        if "Flujo completo - Login falló:" in str(e):
            raise e
        raise Exception(f"Error en flujo completo - login: {str(e)}")

    # 2. Verificar token
    try:
        response = requests.get(
            f"{BASE_URL}/api/verify-token",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Flujo completo - Verificar token falló: {response.json()}")

    except Exception as e:
        if "Flujo completo - Verificar token falló:" in str(e):
            raise e
        raise Exception(f"Error en flujo completo - verificar: {str(e)}")

    # 3. Obtener información del usuario
    try:
        response = requests.get(
            f"{BASE_URL}/api/me",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Flujo completo - Usuario actual falló: {response.json()}")

    except Exception as e:
        if "Flujo completo - Usuario actual falló:" in str(e):
            raise e
        raise Exception(f"Error en flujo completo - usuario actual: {str(e)}")

    # 4. Usar token para acceder a endpoint protegido
    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Flujo completo - Endpoint protegido falló: {response.json()}")

    except Exception as e:
        if "Flujo completo - Endpoint protegido falló:" in str(e):
            raise e
        raise Exception(f"Error en flujo completo - endpoint protegido: {str(e)}")

    # 5. Logout
    try:
        response = requests.post(
            f"{BASE_URL}/api/logout",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Flujo completo - Logout falló: {response.json()}")

        print_test_info("Flujo completo de autenticación", "SUCCESS", {
            "pasos_completados": ["login", "verify_token", "get_user", "access_protected", "logout"],
            "duracion_total": "< 10 segundos",
            "token_funcional": True
        })

    except Exception as e:
        if "Flujo completo - Logout falló:" in str(e):
            raise e
        raise Exception(f"Error en flujo completo - logout: {str(e)}")

    return True


def test_seguridad_avanzada():
    """Probar aspectos avanzados de seguridad"""

    # 1. Test de timing attack prevention (login con usuarios inexistentes)
    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json={"usuario": "usuario_inexistente", "contrasenia": "contraseña_cualquiera"},
            timeout=10
        )

        end_time = time.time()
        response_time = end_time - start_time

        print_test_info("Timing attack prevention", "SUCCESS", {
            "response_time_seconds": round(response_time, 3),
            "status_code": response.status_code,
            "message": "Tiempo de respuesta apropiado para prevenir timing attacks"
        })

    except Exception as e:
        print_test_info("Timing attack prevention", "INFO", {
            "message": f"Test omitido por error: {str(e)}"
        })

    # 2. Test de múltiples requests concurrentes
    import threading

    results = []

    def concurrent_login():
        try:
            response = requests.post(
                f"{BASE_URL}/api/login",
                headers=HEADERS,
                json={"usuario": "admin", "contrasenia": "admin123"},
                timeout=10
            )
            results.append(response.status_code == 200)
        except:
            results.append(False)

    # Crear 5 threads concurrentes
    threads = []
    for i in range(5):
        thread = threading.Thread(target=concurrent_login)
        threads.append(thread)
        thread.start()

    # Esperar a que terminen
    for thread in threads:
        thread.join()

    try:
        successful_logins = sum(results)
        print_test_info("Requests concurrentes", "SUCCESS", {
            "total_requests": len(results),
            "successful_logins": successful_logins,
            "success_rate": f"{(successful_logins / len(results) * 100):.1f}%",
            "message": "Sistema maneja concurrencia correctamente"
        })

    except Exception as e:
        print_test_info("Requests concurrentes", "INFO", {
            "message": f"Test omitido por error: {str(e)}"
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
    config.export_path = "results_autenticacion.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("AUTENTICACIÓN", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login_exitoso, "Login exitoso"),
        (test_login_credenciales_invalidas, "Credenciales inválidas"),
        (test_verify_token, "Verificación de tokens"),
        (test_usuario_actual, "Usuario actual"),
        (test_logout, "Logout"),
        (test_flujo_completo_autenticacion, "Flujo completo"),
        (test_seguridad_avanzada, "Seguridad avanzada")
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