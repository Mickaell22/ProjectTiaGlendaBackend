import requests
import json
import time
import sys
import os
import tempfile
from datetime import datetime, timedelta

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.advanced_test_runner import AdvancedTestRunner, TestConfig

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
admin_token = None
personal_token = None
admin_user_info = None
personal_user_info = None

def print_test_info(test_name, status, data=None, error=None):
    """Función helper para logging de tests individuales"""
    if data and isinstance(data, dict):
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
    if error:
        print(f"   Error: {error}")

# ============================================
# TESTS DE AUTENTICACIÓN PARA REPORTES
# ============================================

def test_login_admin():
    """Obtener token de administrador para tests"""
    global admin_token, admin_user_info

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
            admin_token = response_data["data"]["token"]
            admin_user_info = response_data["data"]
            print_test_info("Login Admin", "PASS", {"token": "obtenido"})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Login Admin", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Login Admin", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_login_personal():
    """Obtener token de personal para tests"""
    global personal_token, personal_user_info
    
    # Intentar con usuario de personal (si existe)
    login_data = {
        "usuario": "terapeuta.test",
        "contrasenia": "test123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json=login_data,
            timeout=10
        )

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("data", {}).get("token"):
                personal_token = response_data["data"]["token"]
                personal_user_info = response_data["data"]
                print_test_info("Login Personal", "PASS", {"token": "obtenido"})
                return {"status": "PASS", "response": response_data}
        
        # Si no existe usuario de personal, usar admin token para tests de personal
        personal_token = admin_token
        personal_user_info = admin_user_info
        print_test_info("Login Personal", "SKIP", {"message": "Usando admin token para simular personal"})
        return {"status": "SKIP", "response": {"message": "Using admin token"}}

    except Exception as e:
        personal_token = admin_token
        personal_user_info = admin_user_info
        print_test_info("Login Personal", "SKIP", error=str(e))
        return {"status": "SKIP", "error": str(e)}

# ============================================
# TESTS DE ENDPOINTS DE REPORTES
# ============================================

def test_get_reportes_disponibles():
    """Test para obtener lista de reportes disponibles"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/api/reportes/disponibles",
            headers=headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data"):
            reportes = response_data["data"]
            print_test_info("Reportes Disponibles", "PASS", 
                          {"total_reportes": response_data.get("total_reportes", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reportes Disponibles", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reportes Disponibles", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_asistencia_paciente():
    """Test para generar reporte de asistencia por paciente"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        # Filtros de prueba
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/asistencia-paciente",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Reporte Asistencia Paciente", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reporte Asistencia Paciente", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Asistencia Paciente", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_progreso_terapeutico():
    """Test para generar reporte de progreso terapéutico"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/progreso-terapeutico",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Reporte Progreso Terapéutico", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reporte Progreso Terapéutico", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Progreso Terapéutico", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_carga_trabajo_personal():
    """Test para generar reporte de carga de trabajo del personal (solo admin)"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/carga-trabajo-personal",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Reporte Carga Trabajo Personal", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reporte Carga Trabajo Personal", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Carga Trabajo Personal", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_academico_estudiante():
    """Test para generar reporte académico por estudiante"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/academico-estudiante",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Reporte Académico Estudiante", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reporte Académico Estudiante", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Académico Estudiante", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_rendimiento_clase():
    """Test para generar reporte de rendimiento por clase"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/rendimiento-clase",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Reporte Rendimiento Clase", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reporte Rendimiento Clase", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Rendimiento Clase", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_utilizacion_recursos():
    """Test para generar reporte de utilización de recursos (solo admin)"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/utilizacion-recursos",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Reporte Utilización Recursos", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Reporte Utilización Recursos", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Utilización Recursos", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_estadisticas_generales():
    """Test para generar estadísticas generales (solo admin)"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/estadisticas-generales",
            headers=headers,
            json=filtros,
            timeout=15
        )

        success = response.status_code == 200
        response_data = response.json()

        if success:
            metadata = response_data.get("metadata", {})
            print_test_info("Estadísticas Generales", "PASS", 
                          {"total_registros": metadata.get("total_registros", 0)})
            return {"status": "PASS", "response": response_data}
        else:
            print_test_info("Estadísticas Generales", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Estadísticas Generales", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

# ============================================
# TESTS DE EXPORTACIÓN
# ============================================

def test_export_pdf():
    """Test para exportar reporte a PDF"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        # Datos de prueba para exportar
        export_data = {
            "data": [
                ["Paciente 1", "1234567890", "Sesión Terapia", "Psicología", "Terapeuta 1", 10, 8, 2, 80.0],
                ["Paciente 2", "0987654321", "Sesión Terapia", "Fonoaudiología", "Terapeuta 2", 12, 10, 2, 83.3]
            ],
            "metadata": {
                "tipo_reporte": "asistencia_paciente",
                "total_registros": 2,
                "fecha_generacion": datetime.now().isoformat(),
                "generado_por": "Test User",
                "filtros_aplicados": {
                    "fecha_inicio": "2024-01-01",
                    "fecha_fin": "2024-12-31"
                }
            },
            "formato": "portrait"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/export/pdf",
            headers=headers,
            json=export_data,
            timeout=20
        )

        success = response.status_code == 200

        if success:
            # Verificar que es un archivo PDF
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print_test_info("Export PDF", "PASS", {"content_type": content_type})
                return {"status": "PASS", "response": {"content_type": content_type}}
            else:
                print_test_info("Export PDF", "FAIL", {"content_type": content_type})
                return {"status": "FAIL", "response": {"content_type": content_type}}
        else:
            response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"status": response.status_code}
            print_test_info("Export PDF", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Export PDF", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_export_excel():
    """Test para exportar reporte a Excel"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        # Datos de prueba para exportar
        export_data = {
            "data": [
                ["Paciente 1", "1234567890", "Sesión Terapia", "Psicología", "Terapeuta 1", 10, 8, 2, 80.0],
                ["Paciente 2", "0987654321", "Sesión Terapia", "Fonoaudiología", "Terapeuta 2", 12, 10, 2, 83.3]
            ],
            "metadata": {
                "tipo_reporte": "asistencia_paciente",
                "total_registros": 2,
                "fecha_generacion": datetime.now().isoformat(),
                "generado_por": "Test User",
                "filtros_aplicados": {
                    "fecha_inicio": "2024-01-01",
                    "fecha_fin": "2024-12-31"
                }
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/export/excel",
            headers=headers,
            json=export_data,
            timeout=20
        )

        success = response.status_code == 200

        if success:
            # Verificar que es un archivo Excel
            content_type = response.headers.get('content-type', '')
            if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                print_test_info("Export Excel", "PASS", {"content_type": content_type})
                return {"status": "PASS", "response": {"content_type": content_type}}
            else:
                print_test_info("Export Excel", "FAIL", {"content_type": content_type})
                return {"status": "FAIL", "response": {"content_type": content_type}}
        else:
            response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"status": response.status_code}
            print_test_info("Export Excel", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Export Excel", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

# ============================================
# TESTS DE VALIDACIÓN Y PERMISOS
# ============================================

def test_validacion_filtros_fechas():
    """Test para validar filtros de fechas incorrectas"""
    if not admin_token:
        return {"status": "SKIP", "error": "No admin token available"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        
        # Filtros con fechas inválidas
        filtros_invalidos = {
            "fecha_inicio": "2024-12-31",
            "fecha_fin": "2024-01-01"  # Fecha fin menor que fecha inicio
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/asistencia-paciente",
            headers=headers,
            json=filtros_invalidos,
            timeout=10
        )

        # Debe fallar por fechas inválidas
        success = response.status_code == 400 or (response.status_code == 200 and not response.json().get("success", True))

        if success:
            print_test_info("Validación Filtros Fechas", "PASS", {"message": "Validación correcta de fechas"})
            return {"status": "PASS", "response": {"validated": True}}
        else:
            response_data = response.json()
            print_test_info("Validación Filtros Fechas", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Validación Filtros Fechas", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_acceso_sin_token():
    """Test para verificar que se requiere autenticación"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/reportes/disponibles",
            headers=HEADERS,
            timeout=10
        )

        # Debe fallar por falta de token
        success = response.status_code == 401

        if success:
            print_test_info("Acceso sin Token", "PASS", {"message": "Autenticación requerida"})
            return {"status": "PASS", "response": {"auth_required": True}}
        else:
            response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"status": response.status_code}
            print_test_info("Acceso sin Token", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Acceso sin Token", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

def test_reporte_admin_con_personal():
    """Test para verificar que personal no puede acceder a reportes de admin"""
    if not personal_token or personal_token == admin_token:
        return {"status": "SKIP", "error": "No personal token available or same as admin"}

    try:
        headers = {**HEADERS, "Authorization": f"Bearer {personal_token}"}
        
        filtros = {
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-12-31"
        }

        response = requests.post(
            f"{BASE_URL}/api/reportes/carga-trabajo-personal",
            headers=headers,
            json=filtros,
            timeout=10
        )

        # Debe fallar por falta de permisos
        success = response.status_code == 403 or (response.status_code == 200 and not response.json().get("success", True))

        if success:
            print_test_info("Reporte Admin con Personal", "PASS", {"message": "Permisos validados correctamente"})
            return {"status": "PASS", "response": {"permissions_validated": True}}
        else:
            response_data = response.json()
            print_test_info("Reporte Admin con Personal", "FAIL", response_data)
            return {"status": "FAIL", "response": response_data}

    except Exception as e:
        print_test_info("Reporte Admin con Personal", "ERROR", error=str(e))
        return {"status": "ERROR", "error": str(e)}

# ============================================
# CONFIGURACIÓN Y EJECUCIÓN DE TESTS
# ============================================

def main():
    """Función principal para ejecutar todos los tests de reportes"""
    print("\n" + "="*60)
    print("INICIANDO TESTS DE SISTEMA DE REPORTES")
    print("="*60)

    # Configuración del test runner
    config = TestConfig()
    config.export_results = True
    config.export_path = "results_reportes.json"
    config.detailed_summary = True
    config.show_progress_details = True

    runner = AdvancedTestRunner("REPORTES", config)

    # Lista de tests a ejecutar
    tests = [
        # Autenticación
        ("Autenticación Admin", test_login_admin),
        ("Autenticación Personal", test_login_personal),
        
        # Endpoints básicos
        ("Reportes Disponibles", test_get_reportes_disponibles),
        
        # Reportes terapéuticos
        ("Reporte Asistencia Paciente", test_reporte_asistencia_paciente),
        ("Reporte Progreso Terapéutico", test_reporte_progreso_terapeutico),
        
        # Reportes pedagógicos
        ("Reporte Académico Estudiante", test_reporte_academico_estudiante),
        ("Reporte Rendimiento Clase", test_reporte_rendimiento_clase),
        
        # Reportes administrativos
        ("Reporte Carga Trabajo Personal", test_reporte_carga_trabajo_personal),
        ("Reporte Utilización Recursos", test_reporte_utilizacion_recursos),
        ("Estadísticas Generales", test_estadisticas_generales),
        
        # Exportación
        ("Export PDF", test_export_pdf),
        ("Export Excel", test_export_excel),
        
        # Validación y permisos
        ("Validación Filtros Fechas", test_validacion_filtros_fechas),
        ("Acceso sin Token", test_acceso_sin_token),
        ("Reporte Admin con Personal", test_reporte_admin_con_personal),
    ]

    # Agregar tests al runner
    for test_name, test_func in tests:
        runner.add_test(test_func, test_name)
    
    # Ejecutar tests
    results = runner.run()
    
    # Mostrar resumen final
    print(f"\n{'='*60}")
    print("RESUMEN DE TESTS DE REPORTES")
    print(f"{'='*60}")
    
    # El runner ya muestra el resumen detallado, solo agregamos mensaje final
    total_tests = len(tests)
    successful_tests = len([r for r in runner.results if r.status == "PASS"])
    failed_tests = len([r for r in runner.results if r.status == "FAIL"]) 
    error_tests = len([r for r in runner.results if r.status == "ERROR"])
    
    print(f"Total de tests ejecutados: {total_tests}")
    print(f"Tests exitosos: {successful_tests}")
    print(f"Tests fallidos: {failed_tests}")
    print(f"Tests con error: {error_tests}")
    
    if failed_tests > 0 or error_tests > 0:
        print(f"\nALERTA: Algunos tests fallaron. Revisar logs para más detalles.")
        return False
    else:
        print(f"\nEXITO: Todos los tests del sistema de reportes pasaron exitosamente!")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nERROR: Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Error ejecutando tests: {e}")
        sys.exit(1)