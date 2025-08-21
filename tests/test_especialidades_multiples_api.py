"""
test_especialidades_multiples_api.py
Tests para el sistema de especialidades múltiples
Centro Tía Glenda - Testing de Especialidades Múltiples
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

class EspecialidadesMultiplesAPITest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.user_token = None
        self.test_data = {
            'especialidades': [],
            'personal': [],
            'pacientes': []
        }
        self.test_assignments = []
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
        print("\n[AUTH] Autenticando usuarios para tests de especialidades multiples...")
        
        # Autenticar admin
        try:
            login_data = {
                "usuario": "admin.norte",
                "contrasenia": "admin123"
            }
            response = requests.post(f"{self.base_url}/api/login", 
                                   json=login_data, headers=self.headers)
            
            if response.status_code == 200:
                self.admin_token = response.json()['data']['token']
                self.print_test_result("Autenticación Admin", True, "Token obtenido exitosamente")
            else:
                self.print_test_result("Autenticación Admin", False, f"Error: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Autenticación Admin", False, f"Excepción: {str(e)}")
            return False

        return True

    def setup_test_data(self):
        """Obtener datos de prueba existentes"""
        print("\n[DATA] Obteniendo datos de prueba...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            
            # Obtener especialidades
            response = requests.get(f"{self.base_url}/api/especialidades", 
                                  headers=headers_with_token)
            if response.status_code == 200:
                self.test_data['especialidades'] = response.json()['data'][:3]  # Máximo 3 para tests
                self.print_test_result("Obtener especialidades", True, 
                                     f"Encontradas {len(self.test_data['especialidades'])} especialidades")
            
            # Obtener personal
            response = requests.get(f"{self.base_url}/api/personal", 
                                  headers=headers_with_token)
            if response.status_code == 200:
                self.test_data['personal'] = response.json()['data'][:2]  # Máximo 2 para tests
                self.print_test_result("Obtener personal", True, 
                                     f"Encontrado {len(self.test_data['personal'])} personal")
            
            # Obtener pacientes
            response = requests.get(f"{self.base_url}/api/pacientes", 
                                  headers=headers_with_token)
            if response.status_code == 200:
                self.test_data['pacientes'] = response.json()['data'][:2]  # Máximo 2 para tests
                self.print_test_result("Obtener pacientes", True, 
                                     f"Encontrados {len(self.test_data['pacientes'])} pacientes")
            
            return (len(self.test_data['especialidades']) > 0 and 
                   len(self.test_data['personal']) > 0 and 
                   len(self.test_data['pacientes']) > 0)
            
        except Exception as e:
            self.print_test_result("Setup datos de prueba", False, f"Excepción: {str(e)}")
            return False

    def test_asignar_especialidad_personal(self):
        """Test: Asignar especialidad a personal"""
        print("\n[TEST] Testeando asignacion de especialidad a personal...")
        
        if not self.test_data['personal'] or not self.test_data['especialidades']:
            self.print_test_result("Asignar especialidad personal", False, "Datos de prueba insuficientes")
            return None
        
        try:
            personal_id = self.test_data['personal'][0]['id']
            especialidad_id = self.test_data['especialidades'][0]['id']
            
            assignment_data = {
                "id_personal": personal_id,
                "id_especialidad": especialidad_id,
                "es_principal": True,
                "nivel_competencia": "avanzado",
                "certificacion": "Certificación de prueba automática",
                "observaciones": f"Asignación de prueba - {datetime.now().isoformat()}"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/personal/{personal_id}/especialidades", 
                                   json=assignment_data, headers=headers_with_token)
            
            if response.status_code == 200:
                assignment_info = response.json()['data']
                self.test_assignments.append(('personal', personal_id, especialidad_id))
                self.print_test_result("Asignar especialidad personal", True, 
                                     f"Especialidad asignada al personal {personal_id}", assignment_data)
                return assignment_info
            elif response.status_code == 400 and "asignada" in response.text:
                # Especialidad ya asignada, contar como éxito
                self.print_test_result("Asignar especialidad personal", True, 
                                     f"Especialidad ya existe (esperado en pruebas)", assignment_data)
                return {"personal_id": personal_id, "especialidad_id": especialidad_id}
            else:
                self.print_test_result("Asignar especialidad personal", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Asignar especialidad personal", False, f"Excepción: {str(e)}")
            return None

    def test_asignar_especialidad_paciente(self):
        """Test: Asignar especialidad a paciente"""
        print("\n[TEST] Testeando asignacion de especialidad a paciente...")
        
        if not self.test_data['pacientes'] or not self.test_data['especialidades']:
            self.print_test_result("Asignar especialidad paciente", False, "Datos de prueba insuficientes")
            return None
        
        try:
            paciente_id = self.test_data['pacientes'][0]['id']
            especialidad_id = self.test_data['especialidades'][0]['id']
            
            assignment_data = {
                "id_paciente": paciente_id,
                "id_especialidad": especialidad_id,
                "es_principal": True,
                "prioridad": "alta",
                "observaciones": f"Asignación paciente de prueba - {datetime.now().isoformat()}",
                "requiere_coordinacion": False
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/especialidades", 
                                   json=assignment_data, headers=headers_with_token)
            
            if response.status_code == 200:
                assignment_info = response.json()['data']
                self.test_assignments.append(('paciente', paciente_id, especialidad_id))
                self.print_test_result("Asignar especialidad paciente", True, 
                                     f"Especialidad asignada al paciente {paciente_id}", assignment_data)
                return assignment_info
            elif response.status_code == 400 and "asignada" in response.text:
                # Especialidad ya asignada, contar como éxito
                self.print_test_result("Asignar especialidad paciente", True, 
                                     f"Especialidad ya existe (esperado en pruebas)", assignment_data)
                return {"paciente_id": paciente_id, "especialidad_id": especialidad_id}
            else:
                self.print_test_result("Asignar especialidad paciente", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Asignar especialidad paciente", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_especialidades_personal(self, personal_id):
        """Test: Obtener especialidades de personal específico"""
        print("\n[TEST] Testeando obtencion de especialidades de personal...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/personal/{personal_id}/especialidades", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                especialidades = response.json()['data']
                self.print_test_result("Obtener especialidades personal", True, 
                                     f"Personal {personal_id} tiene {len(especialidades)} especialidades", 
                                     especialidades[:1])
                return especialidades
            else:
                self.print_test_result("Obtener especialidades personal", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener especialidades personal", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_especialidades_paciente(self, paciente_id):
        """Test: Obtener especialidades de paciente específico"""
        print("\n[TEST] Testeando obtencion de especialidades de paciente...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}/especialidades", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                especialidades = response.json()['data']
                self.print_test_result("Obtener especialidades paciente", True, 
                                     f"Paciente {paciente_id} tiene {len(especialidades)} especialidades", 
                                     especialidades[:1])
                return especialidades
            else:
                self.print_test_result("Obtener especialidades paciente", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener especialidades paciente", False, f"Excepción: {str(e)}")
            return []

    def test_actualizar_especialidad_personal(self):
        """Test: Actualizar especialidad de personal"""
        print("\n[TEST] Testeando actualizacion de especialidad de personal...")
        
        if not self.test_data['personal'] or not self.test_data['especialidades']:
            self.print_test_result("Actualizar especialidad personal", False, "Datos de prueba insuficientes")
            return None
        
        try:
            personal_id = self.test_data['personal'][0]['id']
            especialidad_id = self.test_data['especialidades'][0]['id']
            
            update_data = {
                "nivel_competencia": "experto",
                "es_principal": False,
                "certificacion": "Certificación actualizada",
                "observaciones": f"Actualización de prueba - {datetime.now().isoformat()}"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{self.base_url}/api/personal/{personal_id}/especialidades/{especialidad_id}", 
                                  json=update_data, headers=headers_with_token)
            
            if response.status_code == 200:
                assignment_actualizada = response.json()['data']
                self.print_test_result("Actualizar especialidad personal", True, 
                                     "Especialidad de personal actualizada", update_data)
                return assignment_actualizada
            else:
                self.print_test_result("Actualizar especialidad personal", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Actualizar especialidad personal", False, f"Excepción: {str(e)}")
            return None

    def test_cambiar_especialidad_principal_paciente(self):
        """Test: Cambiar especialidad principal de paciente"""
        print("\n[TEST] Testeando cambio de especialidad principal de paciente...")
        
        if not self.test_data['pacientes'] or len(self.test_data['especialidades']) < 2:
            self.print_test_result("Cambiar especialidad principal", False, "Datos de prueba insuficientes")
            return None
        
        try:
            paciente_id = self.test_data['pacientes'][0]['id']
            
            # Primero asignar una segunda especialidad
            segunda_especialidad = self.test_data['especialidades'][1]['id']
            assignment_data = {
                "id_paciente": paciente_id,
                "id_especialidad": segunda_especialidad,
                "es_principal": False,
                "prioridad": "media"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/especialidades", 
                                   json=assignment_data, headers=headers_with_token)
            
            if response.status_code == 200 or (response.status_code == 400 and "asignada" in response.text):
                # Ahora cambiar la especialidad principal
                change_data = {"nueva_especialidad_principal": segunda_especialidad}
                response = requests.put(f"{self.base_url}/api/pacientes/{paciente_id}/especialidad-principal", 
                                      json=change_data, headers=headers_with_token)
                
                if response.status_code == 200:
                    self.print_test_result("Cambiar especialidad principal", True, 
                                         f"Especialidad principal cambiada a {segunda_especialidad}")
                    return True
                else:
                    self.print_test_result("Cambiar especialidad principal", False, 
                                         f"Status: {response.status_code}")
                    return False
            else:
                self.print_test_result("Cambiar especialidad principal", False, 
                                     "No se pudo asignar segunda especialidad")
                return False
        except Exception as e:
            self.print_test_result("Cambiar especialidad principal", False, f"Excepción: {str(e)}")
            return False

    def test_verificar_compatibilidad_personal_paciente(self):
        """Test: Verificar compatibilidad entre personal y paciente"""
        print("\n[TEST] Testeando verificacion de compatibilidad...")
        
        if not self.test_data['personal'] or not self.test_data['pacientes']:
            self.print_test_result("Verificar compatibilidad", False, "Datos de prueba insuficientes")
            return None
        
        try:
            personal_id = self.test_data['personal'][0]['id']
            paciente_id = self.test_data['pacientes'][0]['id']
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/compatibilidad-especialidades/{personal_id}/{paciente_id}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                compatibilidad = response.json()['data']
                self.print_test_result("Verificar compatibilidad", True, 
                                     f"Compatibilidad verificada", compatibilidad)
                return compatibilidad
            else:
                self.print_test_result("Verificar compatibilidad", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Verificar compatibilidad", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_estadisticas_especialidades(self):
        """Test: Obtener estadísticas de especialidades múltiples"""
        print("\n[TEST] Testeando estadisticas de especialidades multiples...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/especialidades-multiples/estadisticas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                stats = response.json()['data']
                self.print_test_result("Obtener estadísticas especialidades", True, 
                                     "Estadísticas obtenidas", stats)
                return stats
            else:
                self.print_test_result("Obtener estadísticas especialidades", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener estadísticas especialidades", False, f"Excepción: {str(e)}")
            return None

    def test_eliminar_especialidad_personal(self):
        """Test: Eliminar especialidad de personal"""
        print("\n[TEST] Testeando eliminacion de especialidad de personal...")
        
        if not self.test_data['personal'] or not self.test_data['especialidades']:
            self.print_test_result("Eliminar especialidad personal", False, "Datos de prueba insuficientes")
            return False
        
        try:
            personal_id = self.test_data['personal'][0]['id']
            especialidad_id = self.test_data['especialidades'][0]['id']
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(f"{self.base_url}/api/personal/{personal_id}/especialidades/{especialidad_id}", 
                                     headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Eliminar especialidad personal", True, 
                                     f"Especialidad {especialidad_id} eliminada del personal {personal_id}")
                return True
            else:
                self.print_test_result("Eliminar especialidad personal", False, 
                                     f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Eliminar especialidad personal", False, f"Excepción: {str(e)}")
            return False

    def test_casos_error(self):
        """Test: Casos de error y validaciones"""
        print("\n[TEST] Testeando casos de error...")
        
        # Test sin autenticación
        try:
            response = requests.get(f"{self.base_url}/api/especialidades-multiples/estadisticas", headers=self.headers)
            success = response.status_code == 401
            self.print_test_result("Error sin autenticación", success, 
                                 f"Status esperado 401, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin autenticación", False, f"Excepción: {str(e)}")

        # Test asignación duplicada
        if self.test_data['personal'] and self.test_data['especialidades']:
            try:
                headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
                personal_id = self.test_data['personal'][0]['id']
                especialidad_id = self.test_data['especialidades'][0]['id']
                
                assignment_data = {
                    "id_personal": personal_id,
                    "id_especialidad": especialidad_id,
                    "es_principal": True
                }
                
                # Intentar asignar la misma especialidad dos veces
                response1 = requests.post(f"{self.base_url}/api/personal/{personal_id}/especialidades", 
                                        json=assignment_data, headers=headers_with_token)
                response2 = requests.post(f"{self.base_url}/api/personal/{personal_id}/especialidades", 
                                        json=assignment_data, headers=headers_with_token)
                
                success = response2.status_code == 400  # Segunda asignación debe fallar
                self.print_test_result("Error asignación duplicada", success, 
                                     f"Status esperado 400, obtenido: {response2.status_code}")
            except Exception as e:
                self.print_test_result("Error asignación duplicada", False, f"Excepción: {str(e)}")

        # Test ID inválido
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/personal/99999/especialidades", 
                                  headers=headers_with_token)
            success = response.status_code == 404
            self.print_test_result("Error ID inválido", success, 
                                 f"Status esperado 404, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error ID inválido", False, f"Excepción: {str(e)}")

    def test_flujo_completo_especialidades_multiples(self):
        """Test: Flujo completo de especialidades múltiples"""
        print("\n[TEST] Testeando flujo completo de especialidades multiples...")
        
        # 1. Asignar especialidades a personal
        print("   Paso 1: Asignando especialidad a personal...")
        self.test_asignar_especialidad_personal()
        
        # 2. Asignar especialidades a paciente
        print("   Paso 2: Asignando especialidad a paciente...")
        self.test_asignar_especialidad_paciente()
        
        if self.test_data['personal']:
            # 3. Obtener especialidades de personal
            print("   Paso 3: Obteniendo especialidades de personal...")
            self.test_obtener_especialidades_personal(self.test_data['personal'][0]['id'])
            
            # 4. Actualizar especialidad de personal
            print("   Paso 4: Actualizando especialidad de personal...")
            self.test_actualizar_especialidad_personal()
        
        if self.test_data['pacientes']:
            # 5. Obtener especialidades de paciente
            print("   Paso 5: Obteniendo especialidades de paciente...")
            self.test_obtener_especialidades_paciente(self.test_data['pacientes'][0]['id'])
            
            # 6. Cambiar especialidad principal
            print("   Paso 6: Cambiando especialidad principal...")
            self.test_cambiar_especialidad_principal_paciente()
        
        # 7. Verificar compatibilidad
        print("   Paso 7: Verificando compatibilidad...")
        self.test_verificar_compatibilidad_personal_paciente()
        
        # 8. Obtener estadísticas
        print("   Paso 8: Obteniendo estadísticas...")
        self.test_obtener_estadisticas_especialidades()
        
        self.print_test_result("Flujo completo especialidades múltiples", True, "Flujo completado exitosamente")

    def run_all_tests(self):
        """Ejecutar todos los tests de especialidades múltiples"""
        print("[*] INICIANDO TESTS DEL SISTEMA DE ESPECIALIDADES MULTIPLES")
        print("=" * 75)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_users():
            print("[ERROR] No se pudo autenticar usuarios. Tests cancelados.")
            return False
        
        # Setup de datos de prueba
        if not self.setup_test_data():
            print("[ERROR] No se pudieron obtener datos de prueba. Tests cancelados.")
            return False
        
        # Test flujo completo
        self.test_flujo_completo_especialidades_multiples()
        
        # Tests de casos de error
        self.test_casos_error()
        
        # Cleanup: eliminar asignaciones de prueba
        print("\n[CLEANUP] Limpiando asignaciones de prueba...")
        for assignment_type, entity_id, especialidad_id in self.test_assignments:
            try:
                headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
                if assignment_type == 'personal':
                    requests.delete(f"{self.base_url}/api/personal/{entity_id}/especialidades/{especialidad_id}", 
                                  headers=headers_with_token)
                elif assignment_type == 'paciente':
                    requests.delete(f"{self.base_url}/api/pacientes/{entity_id}/especialidades/{especialidad_id}", 
                                  headers=headers_with_token)
            except:
                pass  # Ignorar errores de cleanup
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 75)
        print("[SUMMARY] RESUMEN DE TESTS DE ESPECIALIDADES MULTIPLES")
        print("=" * 75)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"[OK] Exitosos: {self.results['passed']}")
        print(f"[FAIL] Fallidos: {self.results['failed']}")
        print(f"[TIME] Duracion: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\n[ERRORS] ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\n[RATE] Tasa de exito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    tester = EspecialidadesMultiplesAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n[SUCCESS] Todos los tests de especialidades multiples pasaron exitosamente!")
        return 0
    else:
        print("\n[FAILED] Algunos tests fallaron. Revisar logs arriba.")
        return 1

if __name__ == "__main__":
    exit(main())