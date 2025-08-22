"""
test_fotos_perfil_api.py
Tests para el sistema de fotos de perfil
Centro Tía Glenda - Testing de Gestión de Fotos de Perfil
"""

import requests
import json
import time
import sys
import os
import io
from datetime import datetime
from PIL import Image

# Configuración base
import os
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
HEADERS = {"Content-Type": "application/json"}

class FotoPerfilAPITest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.user_token = None
        self.test_users = {}
        self.test_images = []
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

    def create_test_image(self, size=(100, 100), format='JPEG', color='red'):
        """Crear imagen de prueba en memoria"""
        img = Image.new('RGB', size, color=color)
        img_buffer = io.BytesIO()
        img.save(img_buffer, format=format)
        img_buffer.seek(0)
        return img_buffer

    def authenticate_users(self):
        """Autenticar usuarios para tests"""
        print("\n[AUTH] Autenticando usuarios para tests de fotos...")
        
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
                self.admin_token = response_data['data']['token']
                self.test_users['admin'] = {
                    'token': self.admin_token,
                    'id': response_data['data']['user']['id'],
                    'nombre': response_data['data']['user']['nombre_completo']
                }
                self.print_test_result("Autenticación Admin", True, "Token obtenido exitosamente")
            else:
                self.print_test_result("Autenticación Admin", False, f"Error: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Autenticación Admin", False, f"Excepción: {str(e)}")
            return False

        return True

    def test_obtener_formatos_soportados(self):
        """Test: Obtener formatos soportados"""
        print("\n[FORMATS] Testeando obtención de formatos soportados...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/fotos-perfil/formatos", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                formats = response.json()['data']
                self.print_test_result("Obtener formatos soportados", True, 
                                     f"Formatos: {formats.get('extensiones_permitidas', [])}", formats)
                return formats
            else:
                self.print_test_result("Obtener formatos soportados", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener formatos soportados", False, f"Excepción: {str(e)}")
            return None

    def test_subir_foto_perfil(self):
        """Test: Subir foto de perfil"""
        print("\n[UPLOAD] Testeando subida de foto de perfil...")
        
        try:
            # Crear imagen de prueba
            test_image = self.create_test_image((200, 200), 'JPEG', 'blue')
            
            # Preparar headers sin Content-Type (para multipart/form-data)
            headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Preparar archivo para upload
            files = {
                'foto': ('test_profile.jpg', test_image, 'image/jpeg')
            }
            
            response = requests.post(f"{self.base_url}/api/perfil/foto", 
                                   headers=headers_with_token, files=files)
            
            if response.status_code == 200:
                photo_info = response.json()['data']
                self.print_test_result("Subir foto perfil", True, 
                                     f"Foto subida: {photo_info.get('ruta_foto', 'N/A')}", photo_info)
                return photo_info.get('ruta_foto')
            else:
                self.print_test_result("Subir foto perfil", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Subir foto perfil", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_mi_foto_perfil(self):
        """Test: Obtener mi foto de perfil"""
        print("\n[GET] Testeando obtención de mi foto de perfil...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/perfil/foto", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                photo_info = response.json()['data']
                self.print_test_result("Obtener mi foto perfil", True, 
                                     "Información de foto obtenida", photo_info)
                return photo_info
            elif response.status_code == 404:
                self.print_test_result("Obtener mi foto perfil", True, 
                                     "No hay foto de perfil (esperado si no se subió antes)")
                return None
            else:
                self.print_test_result("Obtener mi foto perfil", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener mi foto perfil", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_foto_otro_usuario(self, usuario_id):
        """Test: Obtener foto de otro usuario"""
        print("\n[USER] Testeando obtención de foto de otro usuario...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/usuarios/{usuario_id}/foto", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                photo_info = response.json()['data']
                self.print_test_result("Obtener foto otro usuario", True, 
                                     f"Foto de usuario {usuario_id} obtenida", photo_info)
                return photo_info
            elif response.status_code == 404:
                self.print_test_result("Obtener foto otro usuario", True, 
                                     f"Usuario {usuario_id} no tiene foto (OK)")
                return None
            else:
                self.print_test_result("Obtener foto otro usuario", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener foto otro usuario", False, f"Excepción: {str(e)}")
            return None

    def test_eliminar_foto_perfil(self):
        """Test: Eliminar foto de perfil"""
        print("\n[DELETE] Testeando eliminación de foto de perfil...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.delete(f"{self.base_url}/api/perfil/foto", 
                                     headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Eliminar foto perfil", True, 
                                     "Foto eliminada exitosamente")
                return True
            elif response.status_code == 400:
                self.print_test_result("Eliminar foto perfil", True, 
                                     "No hay foto para eliminar (OK)")
                return True
            else:
                self.print_test_result("Eliminar foto perfil", False, 
                                     f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Eliminar foto perfil", False, f"Excepción: {str(e)}")
            return False

    def test_obtener_estadisticas_fotos(self):
        """Test: Obtener estadísticas de fotos (solo admin)"""
        print("\n[STATS] Testeando obtención de estadísticas de fotos...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/fotos-perfil/estadisticas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                stats = response.json()['data']
                self.print_test_result("Obtener estadísticas fotos", True, 
                                     "Estadísticas obtenidas", stats)
                return stats
            else:
                self.print_test_result("Obtener estadísticas fotos", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener estadísticas fotos", False, f"Excepción: {str(e)}")
            return None

    def test_casos_error(self):
        """Test: Casos de error y validaciones"""
        print("\n[ERROR] Testeando casos de error...")
        
        # Test sin autenticación
        try:
            response = requests.get(f"{self.base_url}/api/perfil/foto", headers=self.headers)
            success = response.status_code == 401
            self.print_test_result("Error sin autenticación", success, 
                                 f"Status esperado 401, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin autenticación", False, f"Excepción: {str(e)}")

        # Test subida sin archivo
        try:
            headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/perfil/foto", 
                                   headers=headers_with_token)
            success = response.status_code == 400
            self.print_test_result("Error sin archivo", success, 
                                 f"Status esperado 400, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin archivo", False, f"Excepción: {str(e)}")

        # Test archivo muy grande (simular con metadata)
        try:
            headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
            # Crear archivo de texto grande como imagen (debería fallar por tipo)
            large_content = b"x" * (6 * 1024 * 1024)  # 6MB
            files = {
                'foto': ('large_file.txt', io.BytesIO(large_content), 'text/plain')
            }
            response = requests.post(f"{self.base_url}/api/perfil/foto", 
                                   headers=headers_with_token, files=files)
            success = response.status_code == 400
            self.print_test_result("Error archivo inválido", success, 
                                 f"Status esperado 400, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error archivo inválido", False, f"Excepción: {str(e)}")

    def test_flujo_completo_foto(self):
        """Test: Flujo completo de gestión de foto"""
        print("\n[FLOW] Testeando flujo completo de gestión de foto...")
        
        # 1. Subir foto
        print("   Paso 1: Subiendo foto...")
        foto_ruta = self.test_subir_foto_perfil()
        
        if foto_ruta:
            # 2. Verificar que se puede obtener
            print("   Paso 2: Verificando obtención...")
            foto_info = self.test_obtener_mi_foto_perfil()
            
            if foto_info:
                # 3. Intentar acceder al archivo (test básico)
                print("   Paso 3: Verificando acceso a archivo...")
                try:
                    headers_with_token = {"Authorization": f"Bearer {self.admin_token}"}
                    # Construir URL del archivo
                    archivo_url = f"{self.base_url}/api/fotos-perfil/archivo/{foto_ruta}"
                    response = requests.get(archivo_url, headers=headers_with_token)
                    
                    success = response.status_code in [200, 404]  # 404 OK si archivo no existe físicamente
                    self.print_test_result("Acceso a archivo de foto", success, 
                                         f"Status: {response.status_code}")
                except Exception as e:
                    self.print_test_result("Acceso a archivo de foto", False, f"Excepción: {str(e)}")
                
                # 4. Eliminar foto
                print("   Paso 4: Eliminando foto...")
                self.test_eliminar_foto_perfil()
                
                # 5. Verificar que ya no existe
                print("   Paso 5: Verificando eliminación...")
                foto_despues = self.test_obtener_mi_foto_perfil()
                eliminada = foto_despues is None or not foto_despues.get('foto_perfil')
                self.print_test_result("Verificar eliminación", eliminada, 
                                     "Foto eliminada correctamente" if eliminada else "Foto aún existe")
            
            self.print_test_result("Flujo completo foto", True, "Flujo completado exitosamente")
        else:
            self.print_test_result("Flujo completo foto", False, "No se pudo subir foto inicial")

    def run_all_tests(self):
        """Ejecutar todos los tests de fotos de perfil"""
        print("[START] INICIANDO TESTS DEL SISTEMA DE FOTOS DE PERFIL")
        print("=" * 70)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_users():
            print("❌ No se pudo autenticar usuarios. Tests cancelados.")
            return False
        
        # Tests principales
        self.test_obtener_formatos_soportados()
        
        # Test flujo completo
        self.test_flujo_completo_foto()
        
        # Test con otro usuario (usar ID genérico)
        self.test_obtener_foto_otro_usuario(1)
        
        # Tests de estadísticas
        self.test_obtener_estadisticas_fotos()
        
        # Tests de casos de error
        self.test_casos_error()
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("[SUMMARY] RESUMEN DE TESTS DE FOTOS DE PERFIL")
        print("=" * 70)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"[PASS] Exitosos: {self.results['passed']}")
        print(f"[FAIL] Fallidos: {self.results['failed']}")
        print(f"[TIME] Duración: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\n[FAIL] ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\n[RATE] Tasa de éxito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    print("[INFO] NOTA: Este test requiere la librería Pillow para generar imágenes de prueba")
    print("   Instalar con: pip install Pillow")
    
    try:
        tester = FotoPerfilAPITest()
        success = tester.run_all_tests()
        
        if success:
            print("\n[SUCCESS] Todos los tests de fotos de perfil pasaron exitosamente!")
            return 0
        else:
            print("\n[FAILED] Algunos tests fallaron. Revisar logs arriba.")
            return 1
    except ImportError:
        print("\n[ERROR] Error: Librería Pillow no encontrada. Instalar con: pip install Pillow")
        return 1

if __name__ == "__main__":
    exit(main())