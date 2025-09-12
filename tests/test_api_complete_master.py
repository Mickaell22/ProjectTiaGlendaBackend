import requests
import json
import time
import sys
import os
import subprocess
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# from utils.advanced_test_runner import AdvancedTestRunner, TestConfig

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales
token = None
test_results = {}
start_time = None


def print_header():
    """Imprimir header del test maestro"""
    print("\n" + "=" * 80)
    print("TEST API COMPLETE MAESTRO - SISTEMA TIA GLENDA")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Servidor: {BASE_URL}")
    print(f"Modulos a probar: 18 modulos completos (8 base + 10 nuevos)")
    print("=" * 80)


def print_test_info(test_name, status, data=None, error=None):
    """Función helper para logging de tests individuales"""
    if data and isinstance(data, dict):
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:150]}...")
    if error:
        print(f"   Error: {error}")


def check_server_health():
    """Verificar que el servidor esté funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)

        if response.status_code == 200:
            health_data = response.json()
            print_test_info("Health Check", "SUCCESS", {
                "status": health_data.get("status"),
                "service": health_data.get("service"),
                "version": health_data.get("version")
            })
            return True
        else:
            raise Exception(f"Servidor respondió con status {response.status_code}")

    except Exception as e:
        print_test_info("Health Check", "FAILED", error=str(e))
        return False


def test_login_master():
    """Login maestro para todos los tests"""
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
            user_data = response_data["data"]["user"]

            print_test_info("Login Maestro", "SUCCESS", {
                "usuario": user_data.get("usuario"),
                "rol": user_data.get("rol"),
                "token_length": len(token),
                "expires": "24 horas"
            })
            return True
        else:
            raise Exception(f"Login maestro falló: {response_data}")

    except Exception as e:
        if "Login maestro falló:" in str(e):
            raise e
        raise Exception(f"Error en login maestro: {str(e)}")


def run_module_tests(module_name, test_file):
    """Ejecutar tests de un módulo específico"""
    global test_results

    module_start = time.time()

    try:
        print(f"\nEjecutando {module_name}...")

        # Obtener la ruta absoluta del directorio de tests
        tests_dir = os.path.dirname(os.path.abspath(__file__))
        test_file_path = os.path.join(tests_dir, test_file)

        # Verificar que el archivo existe
        if not os.path.exists(test_file_path):
            raise Exception(f"Archivo no encontrado: {test_file_path}")

        print(f"   Archivo encontrado: {test_file_path}")

        # Ejecutar el test del módulo con ruta absoluta
        result = subprocess.run(
            [sys.executable, test_file_path],
            cwd=tests_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo por módulo
        )

        module_end = time.time()
        execution_time = module_end - module_start

        success = result.returncode == 0

        # Debug: mostrar información adicional si hay error
        if not success:
            print(f"   Debug - Return code: {result.returncode}")
            print(f"   Debug - Working directory: {tests_dir}")
            print(f"   Debug - Command: {sys.executable} {test_file_path}")
            if result.stderr:
                print(f"   Debug - Stderr: {result.stderr[:300]}...")

        # Intentar cargar resultados del archivo JSON si existe
        json_file = test_file.replace('.py', '').replace('test_', 'results_') + '.json'
        detailed_results = None

        try:
            json_path = os.path.join(tests_dir, json_file)
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    detailed_results = json.load(f)
        except Exception:
            pass  # No importa si no se puede cargar

        test_results[module_name] = {
            "success": success,
            "execution_time": round(execution_time, 2),
            "returncode": result.returncode,
            "stdout_lines": len(result.stdout.split('\n')) if result.stdout else 0,
            "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0,
            "detailed_results": detailed_results
        }

        if success:
            print_test_info(f"{module_name}", "SUCCESS", {
                "tiempo_ejecucion": f"{execution_time:.2f}s",
                "tests_internos": detailed_results.get("total_tests") if detailed_results else "N/A",
                "tests_exitosos": detailed_results.get("passed_tests") if detailed_results else "N/A"
            })
        else:
            print_test_info(f"{module_name}", "FAILED", {
                "codigo_error": result.returncode,
                "tiempo_ejecucion": f"{execution_time:.2f}s",
                "stderr_preview": result.stderr[:200] if result.stderr else "N/A"
            })

            # En caso de fallo, mostrar más detalles del error
            if result.stderr:
                print(f"   Error detallado: {result.stderr[:500]}...")

        return success

    except subprocess.TimeoutExpired:
        test_results[module_name] = {
            "success": False,
            "execution_time": 300,
            "error": "Timeout - Test tardó más de 5 minutos"
        }
        print_test_info(f"{module_name}", "TIMEOUT", error="Test tardó más de 5 minutos")
        return False

    except Exception as e:
        test_results[module_name] = {
            "success": False,
            "execution_time": 0,
            "error": str(e)
        }
        print_test_info(f"{module_name}", "ERROR", error=str(e))
        return False


def test_integration_endpoints():
    """Probar algunos endpoints clave para validar integración"""
    global token

    if not token:
        raise Exception("No hay token para tests de integración")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Endpoints clave a probar
    integration_tests = [
        ("GET", "/api/personas", "Listar personas"),
        ("GET", "/api/especialidades", "Listar especialidades"),
        ("GET", "/api/personal", "Listar personal"),
        ("GET", "/api/usuarios", "Listar usuarios"),
        ("GET", "/api/roles", "Listar roles"),
        ("GET", "/api/tutores", "Listar tutores"),
        ("GET", "/api/pacientes", "Listar pacientes"),
        ("GET", "/api/sesiones-terapia", "Listar sesiones terapéuticas"),
        ("GET", "/api/sesiones-pedagogicas", "Listar sesiones pedagógicas"),
        ("GET", "/api/chat/usuarios-disponibles", "Usuarios disponibles chat"),
        ("GET", "/api/fotos-perfil/formatos", "Formatos fotos perfil"),
        ("GET", "/api/documentos-personal/tipos", "Tipos documentos personal"),
        ("GET", "/api/control-pausas/estadisticas", "Estadísticas pausas"),
    ]

    integration_results = {}

    for method, endpoint, description in integration_tests:
        try:
            start_time = time.time()

            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=auth_headers, timeout=10)

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # milisegundos

            success = response.status_code == 200
            data_count = 0

            if success:
                response_data = response.json()
                if isinstance(response_data.get("data"), list):
                    data_count = len(response_data["data"])

            integration_results[endpoint] = {
                "success": success,
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "data_count": data_count
            }

            if success:
                print_test_info(description, "SUCCESS", {
                    "endpoint": endpoint,
                    "response_time": f"{response_time:.0f}ms",
                    "records": data_count
                })
            else:
                print_test_info(description, "FAILED", {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": f"{response_time:.0f}ms"
                })

        except Exception as e:
            integration_results[endpoint] = {
                "success": False,
                "error": str(e)
            }
            print_test_info(description, "ERROR", error=str(e))

    # Resumen de integración
    successful_endpoints = sum(1 for result in integration_results.values() if result.get("success", False))
    total_endpoints = len(integration_tests)

    print_test_info("Resumen de Integración", "SUCCESS", {
        "endpoints_exitosos": f"{successful_endpoints}/{total_endpoints}",
        "porcentaje_exito": f"{(successful_endpoints / total_endpoints) * 100:.1f}%",
        "tiempo_promedio": f"{sum(r.get('response_time_ms', 0) for r in integration_results.values()) / len(integration_results):.1f}ms"
    })

    return successful_endpoints == total_endpoints


def generate_final_report():
    """Generar reporte final completo"""
    global test_results, start_time

    end_time = time.time()
    total_execution_time = end_time - start_time

    # Calcular estadísticas
    total_modules = len(test_results)
    successful_modules = sum(1 for result in test_results.values() if result.get("success", False))
    total_time_modules = sum(result.get("execution_time", 0) for result in test_results.values())

    # Crear reporte
    report = {
        "test_execution": {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": round(total_execution_time, 2),
            "server": BASE_URL
        },
        "summary": {
            "total_modules": total_modules,
            "successful_modules": successful_modules,
            "failed_modules": total_modules - successful_modules,
            "success_rate": round((successful_modules / total_modules) * 100, 1) if total_modules > 0 else 0,
            "total_module_time": round(total_time_modules, 2)
        },
        "modules": test_results,
        "status": "PASSED" if successful_modules == total_modules else "FAILED"
    }

    # Guardar reporte en archivo
    try:
        with open("results_api_complete_master.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"No se pudo guardar el reporte: {e}")

    # Mostrar reporte en consola
    print("\n" + "=" * 80)
    print("REPORTE FINAL - TEST API COMPLETE MAESTRO")
    print("=" * 80)
    print(f"Tiempo total de ejecucion: {total_execution_time:.1f} segundos")
    print(f"Modulos exitosos: {successful_modules}/{total_modules} ({report['summary']['success_rate']}%)")
    print(f"Tiempo promedio por modulo: {total_time_modules / total_modules:.1f}s")

    print("\nDETALLE POR MODULO:")
    for module, result in test_results.items():
        status_icon = "[OK]" if result.get("success") else "[FAIL]"
        time_str = f"{result.get('execution_time', 0):.1f}s"
        print(f"  {status_icon} {module:<20} - {time_str}")

    print("\nESTADO GENERAL:")
    if successful_modules == total_modules:
        print("TODOS LOS TESTS PASARON! El sistema esta funcionando correctamente.")
    else:
        failed_modules = [name for name, result in test_results.items() if not result.get("success")]
        print(f"{len(failed_modules)} modulo(s) fallaron: {', '.join(failed_modules)}")

    print("=" * 80)

    return report


def main():
    """Función principal del test maestro"""
    global start_time
    start_time = time.time()

    print_header()

    # Tests básicos del maestro sin AdvancedTestRunner
    print("\nEjecutando tests basicos...")
    
    # Test 1: Health Check
    try:
        if not check_server_health():
            print("Health Check fallo. Servidor no responde.")
            return 1
        print("Health Check: SUCCESS")
    except Exception as e:
        print(f"Health Check: ERROR - {e}")
        return 1
    
    # Test 2: Login Maestro
    try:
        if not test_login_master():
            print("Login maestro fallo.")
            return 1
        print("Login Maestro: SUCCESS")
    except Exception as e:
        print(f"Login Maestro: ERROR - {e}")
        return 1

    print("\nEJECUTANDO MODULOS INDIVIDUALES:")
    print("-" * 60)

    # Lista de módulos a ejecutar en orden
    modules_to_test = [
        # Módulos base existentes
        ("AUTENTICACIÓN", "test_autenticacion_api.py"),
        ("ROLES", "test_roles_api.py"),
        ("PERSONAS", "test_personas_api.py"),
        ("ESPECIALIDADES", "test_especialidades_api.py"),
        ("PERSONAL", "test_personal_api.py"),
        ("TUTORES", "test_tutores_api.py"),
        ("PACIENTES", "test_pacientes_api.py"),
        ("USUARIOS", "test_usuarios_api.py"),
        ("SESIONES TERAPIA", "test_sesiones_terapia_api.py"),
        ("SESIONES PEDAGÓGICAS", "test_sesiones_pedagogicas_api.py"),
        ("DOCUMENTOS PACIENTES", "test_documentos_pacientes_api.py"),
        
        # Nuevos módulos (Fases 2-3)
        ("REPORTES", "test_reportes_api.py"),
        ("CHAT INTERNO", "test_chat_api.py"),
        ("FOTOS DE PERFIL", "test_fotos_perfil_api.py"),
        ("OBSERVACIONES", "test_observaciones_api.py"),
        ("ESPECIALIDADES MÚLTIPLES", "test_especialidades_multiples_api.py"),
        ("DOCUMENTOS PERSONAL", "test_documentos_personal_api.py"),
        ("CONTROL DE PAUSAS", "test_control_pausas_api.py")
    ]

    # Ejecutar cada módulo
    all_modules_passed = True
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    for module_name, test_file in modules_to_test:
        test_file_path = os.path.join(tests_dir, test_file)
        if os.path.exists(test_file_path):
            success = run_module_tests(module_name, test_file)
            if not success:
                all_modules_passed = False
        else:
            print_test_info(f"{module_name}", "SKIPPED", error=f"Archivo {test_file} no encontrado")
            test_results[module_name] = {"success": False, "error": "Archivo no encontrado"}
            all_modules_passed = False

    print("\nTESTS DE INTEGRACION:")
    print("-" * 40)

    # Tests de integración
    try:
        integration_success = test_integration_endpoints()
        if not integration_success:
            all_modules_passed = False
    except Exception as e:
        print_test_info("Tests de Integración", "FAILED", error=str(e))
        all_modules_passed = False

    # Generar reporte final
    final_report = generate_final_report()

    # Código de salida
    return 0 if all_modules_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario")
        print("Resultados parciales disponibles en results_api_complete_master.json")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError critico en test maestro: {e}")
        sys.exit(1)