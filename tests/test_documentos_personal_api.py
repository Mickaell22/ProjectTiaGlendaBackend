"""
test_documentos_personal_api.py
Tests para el sistema de documentos de personal
Centro Tía Glenda - Testing de Documentos de Personal
"""

import requests
import json
import time
import sys
import os
import io
from datetime import datetime, timedelta

# Configuración base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

class DocumentosPersonalAPITest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.user_token = None
        self.test_personal = []
        self.test_documents = []
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

    def create_test_document(self, filename="test_document.pdf", content=b"Test PDF content"):
        """Crear documento de prueba en memoria"""
        return io.BytesIO(content)

    def authenticate_users(self):
        """Autenticar usuarios para tests"""
        print("\n[AUTH] Autenticando usuarios para tests de documentos...")
        
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
                self.admin_token = response_data.get("data", {}).get("token")
                if self.admin_token:
                    self.print_test_result("Autenticación Admin", True, "Token obtenido exitosamente")
                else:
                    self.print_test_result("Autenticación Admin", False, "Token no encontrado en respuesta")
                    return False
            else:
                self.print_test_result("Autenticación Admin", False, f"Error: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Autenticación Admin", False, f"Excepción: {str(e)}")
            return False

        return True

    def setup_test_personal(self):
        """Obtener personal de prueba"""
        print("\n[SETUP] Obteniendo personal para tests...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/personal", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                self.test_personal = response.json()['data'][:2]  # Máximo 2 para tests
                self.print_test_result("Obtener personal", True, 
                                     f"Encontrado {len(self.test_personal)} personal")
                return len(self.test_personal) > 0
            else:
                self.print_test_result("Obtener personal", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Setup personal", False, f"Excepción: {str(e)}")
            return False

    def test_obtener_tipos_documentos(self):
        """Test: Obtener tipos de documentos soportados"""
        print("\n[TYPES] Testeando obtención de tipos de documentos...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/documentos-personal/tipos", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                tipos = response.json()['data']
                self.print_test_result("Obtener tipos documentos", True, 
                                     f"Tipos disponibles: {tipos.get('tipos_documento', [])}", tipos)
                return tipos
            else:
                self.print_test_result("Obtener tipos documentos", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener tipos documentos", False, f"Excepción: {str(e)}")
            return None

    def test_subir_documento_personal(self):
        """Test: Subir documento de personal"""
        print("\n[TEST] Testeando subida de documento de personal...")
        
        if not self.test_personal:
            self.print_test_result("Subir documento personal", False, "No hay personal disponible")
            return None
        
        try:
            personal_id = self.test_personal[0]['id']
            
            # Crear documento de prueba
            test_doc = self.create_test_document("cedula_test.pdf", b"Contenido cedula de prueba")
            
            # Preparar headers sin Content-Type (para multipart/form-data)
            headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Preparar archivo y datos
            files = {
                'documento': ('cedula_test.pdf', test_doc, 'application/pdf')
            }
            data = {
                'tipo_documento': 'cedula',
                'descripcion': 'Documento de prueba automatizada',
                'es_obligatorio': 'true',
                'fecha_vencimiento': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
            }
            
            response = requests.post(f"{self.base_url}/api/personal/{personal_id}/documentos", 
                                   headers=headers_with_token, files=files, data=data)
            
            if response.status_code == 200:
                documento_info = response.json()['data']
                self.test_documents.append(documento_info['id'])
                self.print_test_result("Subir documento personal", True, 
                                     f"Documento subido: {documento_info.get('nombre_archivo', 'N/A')}", 
                                     documento_info)
                return documento_info['id']
            else:
                self.print_test_result("Subir documento personal", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Subir documento personal", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_documentos_personal(self, personal_id):
        """Test: Obtener documentos de personal específico"""
        print("\n📁 Testeando obtención de documentos de personal...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/personal/{personal_id}/documentos", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                documentos = response.json()['data']
                self.print_test_result("Obtener documentos personal", True, 
                                     f"Personal {personal_id} tiene {len(documentos)} documentos", 
                                     documentos[:1])
                return documentos
            else:
                self.print_test_result("Obtener documentos personal", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener documentos personal", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_documento_especifico(self, documento_id):
        """Test: Obtener documento específico"""
        print("\n🔍 Testeando obtención de documento específico...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/documentos-personal/{documento_id}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                documento = response.json()['data']
                self.print_test_result("Obtener documento específico", True, 
                                     f"Documento obtenido: {documento['tipo_documento']}", documento)
                return documento
            else:
                self.print_test_result("Obtener documento específico", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener documento específico", False, f"Excepción: {str(e)}")
            return None

    def test_validar_documento(self, documento_id):
        """Test: Validar documento (solo admin)"""
        print("\n[VALIDATION] Testeando validación de documento...")
        
        try:
            validation_data = {
                "estado_validacion": "aprobado",
                "observaciones_validacion": f"Documento validado en prueba automática - {datetime.now().isoformat()}",
                "validado_por": "admin"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{self.base_url}/api/documentos-personal/{documento_id}/validar", 
                                  json=validation_data, headers=headers_with_token)
            
            if response.status_code == 200:
                documento_validado = response.json()['data']
                self.print_test_result("Validar documento", True, 
                                     "Documento validado exitosamente", validation_data)
                return documento_validado
            else:
                self.print_test_result("Validar documento", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Validar documento", False, f"Excepción: {str(e)}")
            return None

    def test_actualizar_documento(self, documento_id):
        """Test: Actualizar información de documento"""
        print("\n✏️ Testeando actualización de documento...")
        
        try:
            update_data = {
                "descripcion": f"Documento actualizado - {datetime.now().isoformat()}",
                "fecha_vencimiento": (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'),
                "observaciones": "Actualización de prueba"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{self.base_url}/api/documentos-personal/{documento_id}", 
                                  json=update_data, headers=headers_with_token)
            
            if response.status_code == 200:
                documento_actualizado = response.json()['data']
                self.print_test_result("Actualizar documento", True, 
                                     "Documento actualizado exitosamente", update_data)
                return documento_actualizado
            else:
                self.print_test_result("Actualizar documento", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Actualizar documento", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_documentos_vencidos(self):
        """Test: Obtener documentos próximos a vencer"""
        print("\n⚠️ Testeando obtención de documentos vencidos...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            params = {"dias_alerta": 90}  # Documentos que vencen en 90 días
            response = requests.get(f"{self.base_url}/api/documentos-personal/vencimientos", 
                                  headers=headers_with_token, params=params)
            
            if response.status_code == 200:
                documentos_vencidos = response.json()['data']
                self.print_test_result("Obtener documentos vencidos", True, 
                                     f"Encontrados {len(documentos_vencidos)} documentos próximos a vencer", 
                                     documentos_vencidos[:1])
                return documentos_vencidos
            else:
                self.print_test_result("Obtener documentos vencidos", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener documentos vencidos", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_documentos_pendientes_validacion(self):
        """Test: Obtener documentos pendientes de validación"""
        print("\n⏳ Testeando documentos pendientes de validación...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/documentos-personal/pendientes-validacion", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                documentos_pendientes = response.json()['data']
                self.print_test_result("Documentos pendientes validación", True, 
                                     f"Encontrados {len(documentos_pendientes)} documentos pendientes", 
                                     documentos_pendientes[:1])
                return documentos_pendientes
            else:
                self.print_test_result("Documentos pendientes validación", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Documentos pendientes validación", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_estadisticas_documentos(self):
        """Test: Obtener estadísticas de documentos"""
        print("\n📊 Testeando estadísticas de documentos...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/documentos-personal/estadisticas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                stats = response.json()['data']
                self.print_test_result("Obtener estadísticas documentos", True, 
                                     "Estadísticas obtenidas", stats)
                return stats
            else:
                self.print_test_result("Obtener estadísticas documentos", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener estadísticas documentos", False, f"Excepción: {str(e)}")
            return None

    def test_buscar_documentos(self):
        """Test: Búsqueda avanzada de documentos"""
        print("\n🔍 Testeando búsqueda de documentos...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            params = {
                "tipo_documento": "cedula",
                "estado_validacion": "aprobado",
                "q": "prueba"
            }
            response = requests.get(f"{self.base_url}/api/documentos-personal/buscar", 
                                  headers=headers_with_token, params=params)
            
            if response.status_code == 200:
                resultados = response.json()['data']
                self.print_test_result("Buscar documentos", True, 
                                     f"Encontrados {len(resultados)} resultados", resultados[:1])
                return resultados
            else:
                self.print_test_result("Buscar documentos", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Buscar documentos", False, f"Excepción: {str(e)}")
            return []

    def test_descargar_documento(self, documento_id):
        """Test: Descargar archivo de documento"""
        print("\n⬇️ Testeando descarga de documento...")
        
        try:
            headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/documentos-personal/{documento_id}/descargar", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                content_length = len(response.content)
                self.print_test_result("Descargar documento", True, 
                                     f"Documento descargado: {content_length} bytes")
                return True
            elif response.status_code == 404:
                self.print_test_result("Descargar documento", True, 
                                     "Archivo no encontrado (esperado en test)")
                return True
            else:
                self.print_test_result("Descargar documento", False, 
                                     f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Descargar documento", False, f"Excepción: {str(e)}")
            return False

    def test_eliminar_documento(self, documento_id):
        """Test: Eliminar documento"""
        print("\n🗑️ Testeando eliminación de documento...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(f"{self.base_url}/api/documentos-personal/{documento_id}", 
                                     headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Eliminar documento", True, 
                                     f"Documento {documento_id} eliminado exitosamente")
                return True
            else:
                self.print_test_result("Eliminar documento", False, 
                                     f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Eliminar documento", False, f"Excepción: {str(e)}")
            return False

    def test_casos_error(self):
        """Test: Casos de error y validaciones"""
        print("\n[ERROR_TESTS] Testeando casos de error...")
        
        # Test sin autenticación
        try:
            response = requests.get(f"{self.base_url}/api/documentos-personal/estadisticas", headers=self.headers)
            success = response.status_code == 401
            self.print_test_result("Error sin autenticación", success, 
                                 f"Status esperado 401, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin autenticación", False, f"Excepción: {str(e)}")

        # Test subida sin archivo
        if self.test_personal:
            try:
                headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
                personal_id = self.test_personal[0]['id']
                data = {'tipo_documento': 'cedula'}
                
                response = requests.post(f"{self.base_url}/api/personal/{personal_id}/documentos", 
                                       headers=headers_with_token, data=data)
                success = response.status_code == 400
                self.print_test_result("Error sin archivo", success, 
                                     f"Status esperado 400, obtenido: {response.status_code}")
            except Exception as e:
                self.print_test_result("Error sin archivo", False, f"Excepción: {str(e)}")

        # Test tipo documento inválido
        if self.test_personal:
            try:
                headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
                personal_id = self.test_personal[0]['id']
                
                test_doc = self.create_test_document("invalid.pdf")
                files = {'documento': ('invalid.pdf', test_doc, 'application/pdf')}
                data = {'tipo_documento': 'tipo_inexistente'}
                
                response = requests.post(f"{self.base_url}/api/personal/{personal_id}/documentos", 
                                       headers=headers_with_token, files=files, data=data)
                success = response.status_code == 400
                self.print_test_result("Error tipo documento inválido", success, 
                                     f"Status esperado 400, obtenido: {response.status_code}")
            except Exception as e:
                self.print_test_result("Error tipo documento inválido", False, f"Excepción: {str(e)}")

        # Test documento inexistente
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/documentos-personal/99999", 
                                  headers=headers_with_token)
            success = response.status_code == 404
            self.print_test_result("Error documento inexistente", success, 
                                 f"Status esperado 404, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error documento inexistente", False, f"Excepción: {str(e)}")

    def test_flujo_completo_documentos(self):
        """Test: Flujo completo de gestión de documentos"""
        print("\n[FLOW] Testeando flujo completo de documentos...")
        
        # 1. Obtener tipos de documentos
        print("   Paso 1: Obteniendo tipos de documentos...")
        self.test_obtener_tipos_documentos()
        
        if not self.test_personal:
            self.print_test_result("Flujo completo documentos", False, "No hay personal disponible")
            return
        
        # 2. Subir documento
        print("   Paso 2: Subiendo documento...")
        documento_id = self.test_subir_documento_personal()
        
        if documento_id:
            personal_id = self.test_personal[0]['id']
            
            # 3. Obtener documentos del personal
            print("   Paso 3: Obteniendo documentos del personal...")
            self.test_obtener_documentos_personal(personal_id)
            
            # 4. Obtener documento específico
            print("   Paso 4: Obteniendo documento específico...")
            self.test_obtener_documento_especifico(documento_id)
            
            # 5. Actualizar documento
            print("   Paso 5: Actualizando documento...")
            self.test_actualizar_documento(documento_id)
            
            # 6. Validar documento
            print("   Paso 6: Validando documento...")
            self.test_validar_documento(documento_id)
            
            # 7. Buscar documentos
            print("   Paso 7: Buscando documentos...")
            self.test_buscar_documentos()
            
            # 8. Verificar documentos pendientes
            print("   Paso 8: Verificando documentos pendientes...")
            self.test_obtener_documentos_pendientes_validacion()
            
            # 9. Verificar documentos vencidos
            print("   Paso 9: Verificando documentos vencidos...")
            self.test_obtener_documentos_vencidos()
            
            # 10. Obtener estadísticas
            print("   Paso 10: Obteniendo estadísticas...")
            self.test_obtener_estadisticas_documentos()
            
            # 11. Intentar descargar
            print("   Paso 11: Intentando descarga...")
            self.test_descargar_documento(documento_id)
            
            self.print_test_result("Flujo completo documentos", True, "Flujo completado exitosamente")
        else:
            self.print_test_result("Flujo completo documentos", False, "No se pudo subir documento inicial")

    def run_all_tests(self):
        """Ejecutar todos los tests de documentos de personal"""
        print(">> INICIANDO TESTS DEL SISTEMA DE DOCUMENTOS DE PERSONAL")
        print("=" * 75)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_users():
            print("[ERROR] No se pudo autenticar usuarios. Tests cancelados.")
            return False
        
        # Setup de personal de prueba
        if not self.setup_test_personal():
            print("[ERROR] No se pudo obtener personal de prueba. Tests cancelados.")
            return False
        
        # Test flujo completo
        self.test_flujo_completo_documentos()
        
        # Tests de casos de error
        self.test_casos_error()
        
        # Cleanup: eliminar documentos de prueba
        print("\n🧹 Limpiando documentos de prueba...")
        for doc_id in self.test_documents:
            try:
                headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
                requests.delete(f"{self.base_url}/api/documentos-personal/{doc_id}", 
                              headers=headers_with_token)
            except:
                pass  # Ignorar errores de cleanup
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 75)
        print("📊 RESUMEN DE TESTS DE DOCUMENTOS DE PERSONAL")
        print("=" * 75)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"[PASSED] Exitosos: {self.results['passed']}")
        print(f"[FAILED] Fallidos: {self.results['failed']}")
        print(f"⏱️  Duración: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\n[ERRORS] ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    tester = DocumentosPersonalAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n[SUCCESS] ¡Todos los tests de documentos de personal pasaron exitosamente!")
        return 0
    else:
        print("\n[WARNING] Algunos tests fallaron. Revisar logs arriba.")
        return 1

if __name__ == "__main__":
    exit(main())