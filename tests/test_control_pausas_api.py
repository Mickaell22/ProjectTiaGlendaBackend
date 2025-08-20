"""
test_control_pausas_api.py
Tests para el sistema de control de pausas de pacientes
Centro Tía Glenda - Testing de Control de Pausas
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

class ControlPausasAPITest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.user_token = None
        self.test_pacientes = []
        self.test_especialidades = []
        self.test_pausas = []
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
        print("\n🔐 Autenticando usuarios para tests de control de pausas...")
        
        # Autenticar admin
        try:
            login_data = {
                "usuario": "admin",
                "contrasenia": "admin123"
            }
            response = requests.post(f"{self.base_url}/api/login", 
                                   json=login_data, headers=self.headers)
            
            if response.status_code == 200:
                self.admin_token = response.json()['token']
                self.print_test_result("Autenticación Admin", True, "Token obtenido exitosamente")
            else:
                self.print_test_result("Autenticación Admin", False, f"Error: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Autenticación Admin", False, f"Excepción: {str(e)}")
            return False

        return True

    def setup_test_data(self):
        """Obtener datos de prueba"""
        print("\n📚 Obteniendo datos de prueba...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            
            # Obtener pacientes
            response = requests.get(f"{self.base_url}/api/pacientes", 
                                  headers=headers_with_token)
            if response.status_code == 200:
                self.test_pacientes = response.json()['data'][:2]  # Máximo 2 para tests
                self.print_test_result("Obtener pacientes", True, 
                                     f"Encontrados {len(self.test_pacientes)} pacientes")
            
            # Obtener especialidades
            response = requests.get(f"{self.base_url}/api/especialidades", 
                                  headers=headers_with_token)
            if response.status_code == 200:
                self.test_especialidades = response.json()['data'][:2]  # Máximo 2 para tests
                self.print_test_result("Obtener especialidades", True, 
                                     f"Encontradas {len(self.test_especialidades)} especialidades")
            
            return len(self.test_pacientes) > 0 and len(self.test_especialidades) > 0
            
        except Exception as e:
            self.print_test_result("Setup datos de prueba", False, f"Excepción: {str(e)}")
            return False

    def test_pausar_tratamiento_general(self):
        """Test: Pausar tratamiento general de paciente"""
        print("\n⏸️ Testeando pausa general de tratamiento...")
        
        if not self.test_pacientes:
            self.print_test_result("Pausar tratamiento general", False, "No hay pacientes disponibles")
            return None
        
        try:
            paciente_id = self.test_pacientes[0]['id']
            
            pausa_data = {
                "tipo_pausa": "general",
                "fecha_inicio": datetime.now().strftime('%Y-%m-%d'),
                "fecha_fin": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                "motivo": f"Pausa de prueba automática - {datetime.now().isoformat()}",
                "observaciones": "Pausa creada para testing del sistema"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/pausar", 
                                   json=pausa_data, headers=headers_with_token)
            
            if response.status_code == 200:
                pausa_info = response.json()['data']
                self.test_pausas.append(('general', paciente_id, None))
                self.print_test_result("Pausar tratamiento general", True, 
                                     f"Tratamiento pausado para paciente {paciente_id}", pausa_data)
                return pausa_info
            else:
                self.print_test_result("Pausar tratamiento general", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Pausar tratamiento general", False, f"Excepción: {str(e)}")
            return None

    def test_pausar_especialidad_especifica(self):
        """Test: Pausar especialidad específica de paciente"""
        print("\n⏸️ Testeando pausa de especialidad específica...")
        
        if not self.test_pacientes or not self.test_especialidades:
            self.print_test_result("Pausar especialidad específica", False, "Datos de prueba insuficientes")
            return None
        
        try:
            paciente_id = self.test_pacientes[0]['id']
            especialidad_id = self.test_especialidades[0]['id']
            
            pausa_data = {
                "tipo_pausa": "especialidad",
                "id_especialidad": especialidad_id,
                "fecha_inicio": datetime.now().strftime('%Y-%m-%d'),
                "fecha_fin": (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                "motivo": f"Pausa especialidad de prueba - {datetime.now().isoformat()}",
                "observaciones": "Pausa de especialidad para testing"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/pausar-especialidad", 
                                   json=pausa_data, headers=headers_with_token)
            
            if response.status_code == 200:
                pausa_info = response.json()['data']
                self.test_pausas.append(('especialidad', paciente_id, especialidad_id))
                self.print_test_result("Pausar especialidad específica", True, 
                                     f"Especialidad {especialidad_id} pausada para paciente {paciente_id}", 
                                     pausa_data)
                return pausa_info
            else:
                self.print_test_result("Pausar especialidad específica", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Pausar especialidad específica", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_estado_pausas_paciente(self, paciente_id):
        """Test: Obtener estado de pausas de paciente"""
        print("\n📋 Testeando obtención de estado de pausas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}/pausas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                pausas = response.json()['data']
                self.print_test_result("Obtener estado pausas", True, 
                                     f"Paciente {paciente_id} tiene {len(pausas)} pausas activas", 
                                     pausas[:1])
                return pausas
            else:
                self.print_test_result("Obtener estado pausas", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener estado pausas", False, f"Excepción: {str(e)}")
            return []

    def test_verificar_pausa_activa(self, paciente_id):
        """Test: Verificar si paciente tiene pausas activas"""
        print("\n🔍 Testeando verificación de pausas activas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}/pausa-activa", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                pausa_activa = response.json()['data']
                self.print_test_result("Verificar pausa activa", True, 
                                     f"Estado de pausa verificado", pausa_activa)
                return pausa_activa
            else:
                self.print_test_result("Verificar pausa activa", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Verificar pausa activa", False, f"Excepción: {str(e)}")
            return None

    def test_reanudar_tratamiento_general(self):
        """Test: Reanudar tratamiento general"""
        print("\n▶️ Testeando reanudación de tratamiento general...")
        
        if not self.test_pacientes:
            self.print_test_result("Reanudar tratamiento general", False, "No hay pacientes disponibles")
            return None
        
        try:
            paciente_id = self.test_pacientes[0]['id']
            
            reanudacion_data = {
                "motivo_reanudacion": f"Reanudación de prueba automática - {datetime.now().isoformat()}",
                "observaciones": "Reanudación por testing del sistema"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/reanudar", 
                                   json=reanudacion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                reanudacion_info = response.json()['data']
                self.print_test_result("Reanudar tratamiento general", True, 
                                     f"Tratamiento reanudado para paciente {paciente_id}", 
                                     reanudacion_data)
                return reanudacion_info
            else:
                self.print_test_result("Reanudar tratamiento general", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Reanudar tratamiento general", False, f"Excepción: {str(e)}")
            return None

    def test_reanudar_especialidad_especifica(self):
        """Test: Reanudar especialidad específica"""
        print("\n▶️ Testeando reanudación de especialidad específica...")
        
        if not self.test_pacientes or not self.test_especialidades:
            self.print_test_result("Reanudar especialidad específica", False, "Datos de prueba insuficientes")
            return None
        
        try:
            paciente_id = self.test_pacientes[0]['id']
            especialidad_id = self.test_especialidades[0]['id']
            
            reanudacion_data = {
                "id_especialidad": especialidad_id,
                "motivo_reanudacion": f"Reanudación especialidad de prueba - {datetime.now().isoformat()}",
                "observaciones": "Reanudación de especialidad por testing"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/reanudar-especialidad", 
                                   json=reanudacion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                reanudacion_info = response.json()['data']
                self.print_test_result("Reanudar especialidad específica", True, 
                                     f"Especialidad {especialidad_id} reanudada para paciente {paciente_id}", 
                                     reanudacion_data)
                return reanudacion_info
            else:
                self.print_test_result("Reanudar especialidad específica", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Reanudar especialidad específica", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_historial_pausas(self, paciente_id):
        """Test: Obtener historial completo de pausas"""
        print("\n📚 Testeando obtención de historial de pausas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}/historial-pausas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                historial = response.json()['data']
                self.print_test_result("Obtener historial pausas", True, 
                                     f"Historial contiene {len(historial)} registros", historial[:1])
                return historial
            else:
                self.print_test_result("Obtener historial pausas", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener historial pausas", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_pausas_vencidas(self):
        """Test: Obtener pausas que han vencido"""
        print("\n⏰ Testeando obtención de pausas vencidas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/control-pausas/vencidas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                pausas_vencidas = response.json()['data']
                self.print_test_result("Obtener pausas vencidas", True, 
                                     f"Encontradas {len(pausas_vencidas)} pausas vencidas", 
                                     pausas_vencidas[:1])
                return pausas_vencidas
            else:
                self.print_test_result("Obtener pausas vencidas", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener pausas vencidas", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_proximas_vencer(self):
        """Test: Obtener pausas próximas a vencer"""
        print("\n📅 Testeando pausas próximas a vencer...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            params = {"dias_alerta": 7}  # Pausas que vencen en 7 días
            response = requests.get(f"{self.base_url}/api/control-pausas/proximas-vencer", 
                                  headers=headers_with_token, params=params)
            
            if response.status_code == 200:
                pausas_proximas = response.json()['data']
                self.print_test_result("Obtener pausas próximas a vencer", True, 
                                     f"Encontradas {len(pausas_proximas)} pausas próximas a vencer", 
                                     pausas_proximas[:1])
                return pausas_proximas
            else:
                self.print_test_result("Obtener pausas próximas a vencer", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener pausas próximas a vencer", False, f"Excepción: {str(e)}")
            return []

    def test_procesar_pausas_automaticas(self):
        """Test: Procesar reanudaciones automáticas"""
        print("\n🤖 Testeando procesamiento automático de pausas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/control-pausas/procesar-automaticas", 
                                   headers=headers_with_token)
            
            if response.status_code == 200:
                resultado = response.json()['data']
                self.print_test_result("Procesar pausas automáticas", True, 
                                     f"Procesamiento automático ejecutado", resultado)
                return resultado
            else:
                self.print_test_result("Procesar pausas automáticas", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Procesar pausas automáticas", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_estadisticas_pausas(self):
        """Test: Obtener estadísticas de pausas"""
        print("\n📊 Testeando estadísticas de pausas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/control-pausas/estadisticas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                stats = response.json()['data']
                self.print_test_result("Obtener estadísticas pausas", True, 
                                     "Estadísticas obtenidas", stats)
                return stats
            else:
                self.print_test_result("Obtener estadísticas pausas", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener estadísticas pausas", False, f"Excepción: {str(e)}")
            return None

    def test_casos_error(self):
        """Test: Casos de error y validaciones"""
        print("\n❌ Testeando casos de error...")
        
        # Test sin autenticación
        try:
            response = requests.get(f"{self.base_url}/api/control-pausas/estadisticas", headers=self.headers)
            success = response.status_code == 401
            self.print_test_result("Error sin autenticación", success, 
                                 f"Status esperado 401, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin autenticación", False, f"Excepción: {str(e)}")

        # Test pausar paciente ya pausado
        if self.test_pacientes:
            try:
                headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
                paciente_id = self.test_pacientes[0]['id']
                
                pausa_data = {
                    "tipo_pausa": "general",
                    "fecha_inicio": datetime.now().strftime('%Y-%m-%d'),
                    "fecha_fin": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    "motivo": "Pausa duplicada de prueba"
                }
                
                # Intentar pausar dos veces
                response1 = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/pausar", 
                                        json=pausa_data, headers=headers_with_token)
                response2 = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/pausar", 
                                        json=pausa_data, headers=headers_with_token)
                
                success = response2.status_code == 400  # Segunda pausa debe fallar
                self.print_test_result("Error pausa duplicada", success, 
                                     f"Status esperado 400, obtenido: {response2.status_code}")
            except Exception as e:
                self.print_test_result("Error pausa duplicada", False, f"Excepción: {str(e)}")

        # Test fechas inválidas
        if self.test_pacientes:
            try:
                headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
                paciente_id = self.test_pacientes[0]['id']
                
                pausa_data = {
                    "tipo_pausa": "general",
                    "fecha_inicio": (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),  # Fecha futura
                    "fecha_fin": datetime.now().strftime('%Y-%m-%d'),  # Fecha anterior al inicio
                    "motivo": "Fechas inválidas"
                }
                
                response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/pausar", 
                                       json=pausa_data, headers=headers_with_token)
                success = response.status_code == 400
                self.print_test_result("Error fechas inválidas", success, 
                                     f"Status esperado 400, obtenido: {response.status_code}")
            except Exception as e:
                self.print_test_result("Error fechas inválidas", False, f"Excepción: {str(e)}")

        # Test paciente inexistente
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/pacientes/99999/pausas", 
                                  headers=headers_with_token)
            success = response.status_code == 404
            self.print_test_result("Error paciente inexistente", success, 
                                 f"Status esperado 404, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error paciente inexistente", False, f"Excepción: {str(e)}")

    def test_flujo_completo_control_pausas(self):
        """Test: Flujo completo de control de pausas"""
        print("\n🔄 Testeando flujo completo de control de pausas...")
        
        if not self.test_pacientes:
            self.print_test_result("Flujo completo control pausas", False, "No hay pacientes disponibles")
            return
        
        paciente_id = self.test_pacientes[0]['id']
        
        # 1. Verificar estado inicial
        print("   Paso 1: Verificando estado inicial...")
        self.test_verificar_pausa_activa(paciente_id)
        
        # 2. Pausar tratamiento general
        print("   Paso 2: Pausando tratamiento general...")
        self.test_pausar_tratamiento_general()
        
        # 3. Verificar pausa activa
        print("   Paso 3: Verificando pausa activa...")
        self.test_verificar_pausa_activa(paciente_id)
        
        # 4. Pausar especialidad específica
        print("   Paso 4: Pausando especialidad específica...")
        self.test_pausar_especialidad_especifica()
        
        # 5. Obtener estado de pausas
        print("   Paso 5: Obteniendo estado de pausas...")
        self.test_obtener_estado_pausas_paciente(paciente_id)
        
        # 6. Obtener historial
        print("   Paso 6: Obteniendo historial de pausas...")
        self.test_obtener_historial_pausas(paciente_id)
        
        # 7. Reanudar especialidad
        print("   Paso 7: Reanudando especialidad...")
        self.test_reanudar_especialidad_especifica()
        
        # 8. Reanudar tratamiento general
        print("   Paso 8: Reanudando tratamiento general...")
        self.test_reanudar_tratamiento_general()
        
        # 9. Verificar pausas vencidas
        print("   Paso 9: Verificando pausas vencidas...")
        self.test_obtener_pausas_vencidas()
        
        # 10. Verificar pausas próximas a vencer
        print("   Paso 10: Verificando pausas próximas a vencer...")
        self.test_obtener_proximas_vencer()
        
        # 11. Procesar automáticas
        print("   Paso 11: Procesando pausas automáticas...")
        self.test_procesar_pausas_automaticas()
        
        # 12. Obtener estadísticas
        print("   Paso 12: Obteniendo estadísticas...")
        self.test_obtener_estadisticas_pausas()
        
        self.print_test_result("Flujo completo control pausas", True, "Flujo completado exitosamente")

    def run_all_tests(self):
        """Ejecutar todos los tests de control de pausas"""
        print("🚀 INICIANDO TESTS DEL SISTEMA DE CONTROL DE PAUSAS")
        print("=" * 70)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_users():
            print("❌ No se pudo autenticar usuarios. Tests cancelados.")
            return False
        
        # Setup de datos de prueba
        if not self.setup_test_data():
            print("❌ No se pudieron obtener datos de prueba. Tests cancelados.")
            return False
        
        # Test flujo completo
        self.test_flujo_completo_control_pausas()
        
        # Tests de casos de error
        self.test_casos_error()
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE TESTS DE CONTROL DE PAUSAS")
        print("=" * 70)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"✅ Exitosos: {self.results['passed']}")
        print(f"❌ Fallidos: {self.results['failed']}")
        print(f"⏱️  Duración: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    tester = ControlPausasAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ¡Todos los tests de control de pausas pasaron exitosamente!")
        return 0
    else:
        print("\n💥 Algunos tests fallaron. Revisar logs arriba.")
        return 1

if __name__ == "__main__":
    exit(main())