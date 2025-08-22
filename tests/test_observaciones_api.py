"""
test_observaciones_api.py
Tests para el sistema de observaciones de sesiones
Centro Tía Glenda - Testing de Observaciones
"""

import requests
import json
import time
import sys
import os
from datetime import datetime, timedelta

# Configuración base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

class ObservacionesAPITest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.user_token = None
        self.test_users = {}
        self.test_observations = []
        self.test_sessions = {}
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def print_test_result(self, test_name, success, message="", data=None):
        """Imprimir resultado de test individual"""
        self.results['total_tests'] += 1
        status = "PASS" if success else "FAIL"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}[{status}]{reset} {test_name}")
        if message:
            print(f"      {message}")
        if data:
            print(f"      Data: {json.dumps(data, indent=6, ensure_ascii=False)[:200]}...")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")

    def authenticate_users(self):
        """Autenticar usuarios para tests"""
        print("\n[AUTH] Autenticando usuarios para tests de observaciones...")
        
        # Autenticar admin
        try:
            login_data = {
                "usuario": "admin.norte",
                "contrasenia": "admin123"
            }
            response = requests.post(f"{self.base_url}/api/login", 
                                   json=login_data, headers=self.headers)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("data", {}).get("token"):
                    self.admin_token = response_data["data"]["token"]
                    self.test_users['admin'] = {
                        'token': self.admin_token,
                        'id': response_data["data"]["user"]["id"],
                        'nombre': response_data["data"]["user"]["nombre_completo"]
                    }
                else:
                    self.print_test_result("Autenticación Admin", False, f"Token no encontrado en respuesta: {response_data}")
                    return False
                self.print_test_result("Autenticación Admin", True, "Token obtenido exitosamente")
            else:
                self.print_test_result("Autenticación Admin", False, f"Error: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Autenticación Admin", False, f"Excepción: {str(e)}")
            return False

        return True

    def setup_test_sessions(self):
        """Obtener sesiones de prueba existentes"""
        print("\n[INFO] Obteniendo sesiones para tests...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            
            # Obtener sesiones terapéuticas
            response = requests.get(f"{self.base_url}/api/sesiones-terapia", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                terapia_sessions = response.json()['data']
                if terapia_sessions:
                    self.test_sessions['terapeutica'] = terapia_sessions[0]['id']
                    self.print_test_result("Obtener sesión terapéutica", True, 
                                         f"ID sesión: {self.test_sessions['terapeutica']}")
                else:
                    self.print_test_result("Obtener sesión terapéutica", False, "No hay sesiones disponibles")
            
            # Obtener sesiones pedagógicas
            response = requests.get(f"{self.base_url}/api/sesiones-pedagogicas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                pedagogica_sessions = response.json()['data']
                if pedagogica_sessions:
                    self.test_sessions['pedagogica'] = pedagogica_sessions[0]['id']
                    self.print_test_result("Obtener sesión pedagógica", True, 
                                         f"ID sesión: {self.test_sessions['pedagogica']}")
                else:
                    self.print_test_result("Obtener sesión pedagógica", False, "No hay sesiones disponibles")
            
            return len(self.test_sessions) > 0
            
        except Exception as e:
            self.print_test_result("Setup sesiones", False, f"Excepción: {str(e)}")
            return False

    def test_crear_observacion_terapeutica(self):
        """Test: Crear observación para sesión terapéutica"""
        print("\n[INFO] Testeando creación de observación terapéutica...")
        
        if 'terapeutica' not in self.test_sessions:
            self.print_test_result("Crear observación terapéutica", False, "No hay sesión terapéutica disponible")
            return None
        
        try:
            observacion_data = {
                "id_sesion": self.test_sessions['terapeutica'],
                "tipo_sesion": "terapeutica",
                "observacion": f"Observación de prueba automatizada - {datetime.now().isoformat()}",
                "tipo_observacion": "observacion",
                "es_seguimiento": False,
                "es_privada": False
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/observaciones", 
                                   json=observacion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                observacion_info = response.json()['data']
                self.test_observations.append(observacion_info['id'])
                self.print_test_result("Crear observación terapéutica", True, 
                                     f"Observación ID: {observacion_info['id']}", observacion_data)
                return observacion_info['id']
            else:
                self.print_test_result("Crear observación terapéutica", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Crear observación terapéutica", False, f"Excepción: {str(e)}")
            return None

    def test_crear_observacion_pedagogica(self):
        """Test: Crear observación para sesión pedagógica"""
        print("\n[INFO] Testeando creación de observación pedagógica...")
        
        if 'pedagogica' not in self.test_sessions:
            self.print_test_result("Crear observación pedagógica", False, "No hay sesión pedagógica disponible")
            return None
        
        try:
            observacion_data = {
                "id_sesion": self.test_sessions['pedagogica'],
                "tipo_sesion": "pedagogica",
                "observacion": f"Observación pedagógica de prueba - {datetime.now().isoformat()}",
                "tipo_observacion": "nota",
                "es_seguimiento": True,
                "es_privada": True
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/observaciones", 
                                   json=observacion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                observacion_info = response.json()['data']
                self.test_observations.append(observacion_info['id'])
                self.print_test_result("Crear observación pedagógica", True, 
                                     f"Observación ID: {observacion_info['id']}", observacion_data)
                return observacion_info['id']
            else:
                self.print_test_result("Crear observación pedagógica", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Crear observación pedagógica", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_observaciones_sesion(self, tipo_sesion):
        """Test: Obtener observaciones de una sesión específica"""
        print(f"\n[INFO] Testeando obtención de observaciones de sesión {tipo_sesion}...")
        
        if tipo_sesion not in self.test_sessions:
            self.print_test_result(f"Obtener observaciones {tipo_sesion}", False, 
                                 f"No hay sesión {tipo_sesion} disponible")
            return []
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            session_id = self.test_sessions[tipo_sesion]
            response = requests.get(f"{self.base_url}/api/observaciones/sesion/{session_id}/{tipo_sesion}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                observaciones = response.json()['data']
                self.print_test_result(f"Obtener observaciones {tipo_sesion}", True, 
                                     f"Encontradas {len(observaciones)} observaciones", observaciones[:1])
                return observaciones
            else:
                self.print_test_result(f"Obtener observaciones {tipo_sesion}", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result(f"Obtener observaciones {tipo_sesion}", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_observacion_especifica(self, observacion_id):
        """Test: Obtener observación específica por ID"""
        print("\n[INFO] Testeando obtención de observación específica...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/observaciones/{observacion_id}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                observacion = response.json()['data']
                self.print_test_result("Obtener observación específica", True, 
                                     f"Observación obtenida: {observacion['tipo_observacion']}", observacion)
                return observacion
            else:
                self.print_test_result("Obtener observación específica", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener observación específica", False, f"Excepción: {str(e)}")
            return None

    def test_actualizar_observacion(self, observacion_id):
        """Test: Actualizar observación existente"""
        print("\n✏️ Testeando actualización de observación...")
        
        try:
            update_data = {
                "observacion": f"Observación actualizada - {datetime.now().isoformat()}",
                "tipo_observacion": "falta",
                "es_seguimiento": True
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{self.base_url}/api/observaciones/{observacion_id}", 
                                  json=update_data, headers=headers_with_token)
            
            if response.status_code == 200:
                observacion_actualizada = response.json()['data']
                self.print_test_result("Actualizar observación", True, 
                                     "Observación actualizada exitosamente", update_data)
                return observacion_actualizada
            else:
                self.print_test_result("Actualizar observación", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Actualizar observación", False, f"Excepción: {str(e)}")
            return None

    def test_buscar_observaciones(self):
        """Test: Búsqueda avanzada de observaciones"""
        print("\n[INFO] Testeando búsqueda avanzada de observaciones...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            params = {
                "q": "prueba",
                "tipo_observacion": "observacion",
                "tipo_sesion": "terapeutica"
            }
            response = requests.get(f"{self.base_url}/api/observaciones/buscar", 
                                  headers=headers_with_token, params=params)
            
            if response.status_code == 200:
                resultados = response.json()['data']
                self.print_test_result("Buscar observaciones", True, 
                                     f"Encontrados {len(resultados)} resultados", resultados[:1])
                return resultados
            else:
                self.print_test_result("Buscar observaciones", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Buscar observaciones", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_seguimientos_pendientes(self):
        """Test: Obtener seguimientos pendientes"""
        print("\n📅 Testeando obtención de seguimientos pendientes...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/observaciones/seguimientos-pendientes", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                seguimientos = response.json()['data']
                self.print_test_result("Obtener seguimientos pendientes", True, 
                                     f"Encontrados {len(seguimientos)} seguimientos", seguimientos[:1])
                return seguimientos
            else:
                self.print_test_result("Obtener seguimientos pendientes", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener seguimientos pendientes", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_estadisticas_observaciones(self):
        """Test: Obtener estadísticas de observaciones"""
        print("\n[INFO] Testeando obtención de estadísticas de observaciones...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/observaciones/estadisticas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                stats = response.json()['data']
                self.print_test_result("Obtener estadísticas observaciones", True, 
                                     "Estadísticas obtenidas", stats)
                return stats
            else:
                self.print_test_result("Obtener estadísticas observaciones", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener estadísticas observaciones", False, f"Excepción: {str(e)}")
            return None

    def test_eliminar_observacion(self, observacion_id):
        """Test: Eliminar observación"""
        print("\n🗑️ Testeando eliminación de observación...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(f"{self.base_url}/api/observaciones/{observacion_id}", 
                                     headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Eliminar observación", True, 
                                     f"Observación {observacion_id} eliminada exitosamente")
                return True
            else:
                self.print_test_result("Eliminar observación", False, 
                                     f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Eliminar observación", False, f"Excepción: {str(e)}")
            return False

    def test_casos_error(self):
        """Test: Casos de error y validaciones"""
        print("\n[INFO] Testeando casos de error...")
        
        # Test sin autenticación
        try:
            response = requests.get(f"{self.base_url}/api/observaciones/estadisticas", headers=self.headers)
            success = response.status_code == 401
            self.print_test_result("Error sin autenticación", success, 
                                 f"Status esperado 401, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin autenticación", False, f"Excepción: {str(e)}")

        # Test creación con datos inválidos
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            observacion_data = {
                "id_sesion": -1,  # ID inválido
                "tipo_sesion": "invalido",  # Tipo inválido
                "observacion": "",  # Observación vacía
                "tipo_observacion": "inexistente"  # Tipo inexistente
            }
            response = requests.post(f"{self.base_url}/api/observaciones", 
                                   json=observacion_data, headers=headers_with_token)
            success = response.status_code == 400
            self.print_test_result("Error datos inválidos", success, 
                                 f"Status esperado 400, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error datos inválidos", False, f"Excepción: {str(e)}")

        # Test acceso a observación inexistente
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/observaciones/99999", 
                                  headers=headers_with_token)
            success = response.status_code == 404
            self.print_test_result("Error observación inexistente", success, 
                                 f"Status esperado 404, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error observación inexistente", False, f"Excepción: {str(e)}")

    def test_flujo_completo_observaciones(self):
        """Test: Flujo completo de gestión de observaciones"""
        print("\n[INFO] Testeando flujo completo de observaciones...")
        
        # 1. Crear observación terapéutica
        print("   Paso 1: Creando observación terapéutica...")
        obs_terapeutica_id = self.test_crear_observacion_terapeutica()
        
        # 2. Crear observación pedagógica
        print("   Paso 2: Creando observación pedagógica...")
        obs_pedagogica_id = self.test_crear_observacion_pedagogica()
        
        if obs_terapeutica_id:
            # 3. Obtener observaciones de la sesión
            print("   Paso 3: Obteniendo observaciones de sesión...")
            self.test_obtener_observaciones_sesion('terapeutica')
            
            # 4. Obtener observación específica
            print("   Paso 4: Obteniendo observación específica...")
            self.test_obtener_observacion_especifica(obs_terapeutica_id)
            
            # 5. Actualizar observación
            print("   Paso 5: Actualizando observación...")
            self.test_actualizar_observacion(obs_terapeutica_id)
            
            # 6. Búsqueda de observaciones
            print("   Paso 6: Buscando observaciones...")
            self.test_buscar_observaciones()
            
            # 7. Verificar seguimientos
            print("   Paso 7: Verificando seguimientos...")
            self.test_obtener_seguimientos_pendientes()
            
            # 8. Obtener estadísticas
            print("   Paso 8: Obteniendo estadísticas...")
            self.test_obtener_estadisticas_observaciones()
            
            self.print_test_result("Flujo completo observaciones", True, "Flujo completado exitosamente")
        else:
            self.print_test_result("Flujo completo observaciones", False, "No se pudo crear observación inicial")

    def run_all_tests(self):
        """Ejecutar todos los tests de observaciones"""
        print("INICIANDO TESTS DEL SISTEMA DE OBSERVACIONES")
        print("=" * 70)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_users():
            print("ERROR: No se pudo autenticar usuarios. Tests cancelados.")
            return False
        
        # Setup de sesiones de prueba
        if not self.setup_test_sessions():
            print("WARNING: No se pudieron obtener sesiones de prueba. Algunos tests se saltaran.")
        
        # Test flujo completo
        self.test_flujo_completo_observaciones()
        
        # Tests adicionales
        if self.test_sessions:
            # Tests específicos por tipo de sesión
            for tipo_sesion in self.test_sessions.keys():
                self.test_obtener_observaciones_sesion(tipo_sesion)
        
        # Tests de casos de error
        self.test_casos_error()
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("RESUMEN DE TESTS DE OBSERVACIONES")
        print("=" * 70)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"OK Exitosos: {self.results['passed']}")
        print(f"X Fallidos: {self.results['failed']}")
        print(f"TIME Duracion: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\nERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\nTasa de exito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    tester = ObservacionesAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\nTodos los tests de observaciones pasaron exitosamente!")
        return 0
    else:
        print("\nAlgunos tests fallaron. Revisar logs arriba.")
        return 1

if __name__ == "__main__":
    exit(main())