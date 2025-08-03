"""
Test para API de Documentos de Pacientes - Centro Tía Glenda
Pruebas de subida, gestión y descarga de documentos PDF para pacientes
"""

import requests
import json
import os
import tempfile
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


class TestDocumentosPacientesAPI:
    """Pruebas para el API de documentos de pacientes"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.test_results = []
        self.paciente_id = None
        self.documento_id = None
        self.temp_pdf_path = None

    def crear_pdf_prueba(self, nombre_archivo="test_documento.pdf", contenido="Test Document"):
        """Crear un archivo PDF temporal para pruebas"""
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, nombre_archivo)
        
        # Crear PDF con reportlab
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, contenido)
        c.drawString(100, 730, "Este es un documento de prueba")
        c.drawString(100, 710, f"Archivo: {nombre_archivo}")
        c.save()
        
        return pdf_path

    def crear_archivo_no_pdf(self, nombre_archivo="test_archivo.txt"):
        """Crear un archivo que no es PDF para pruebas de validación"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, nombre_archivo)
        
        with open(file_path, 'w') as f:
            f.write("Este no es un archivo PDF")
        
        return file_path

    def limpiar_archivos_temporales(self):
        """Limpiar archivos temporales creados durante las pruebas"""
        if self.temp_pdf_path and os.path.exists(self.temp_pdf_path):
            try:
                os.remove(self.temp_pdf_path)
            except:
                pass

    def log_result(self, test_name, success, message, details=None):
        """Registrar resultado de prueba"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"    Detalles: {details}")

    def authenticate(self, usuario="admin", password="admin123"):
        """Autenticarse y obtener token"""
        try:
            print("🔐 Iniciando autenticación...")
            
            response = requests.post(f"{self.base_url}/api/login", json={
                "usuario": usuario,
                "contrasenia": password
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.token = data['data']['token']
                    self.log_result("Autenticación", True, "Login exitoso")
                    return True
                else:
                    self.log_result("Autenticación", False, f"Error en respuesta: {data.get('message')}")
                    return False
            else:
                self.log_result("Autenticación", False, f"Error HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Autenticación", False, f"Error de conexión: {str(e)}")
            return False

    def get_headers(self):
        """Obtener headers con token de autenticación"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def preparar_paciente_prueba(self):
        """Crear o obtener un paciente para las pruebas"""
        try:
            # Primero intentar obtener lista de pacientes
            response = requests.get(
                f"{self.base_url}/api/pacientes",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('data'):
                    # Usar el primer paciente disponible
                    self.paciente_id = data['data'][0]['id']
                    self.log_result("Preparar Paciente", True, f"Usando paciente ID: {self.paciente_id}")
                    return True
                else:
                    self.log_result("Preparar Paciente", False, "No hay pacientes disponibles para pruebas")
                    return False
            else:
                self.log_result("Preparar Paciente", False, f"Error obteniendo pacientes: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Preparar Paciente", False, f"Error: {str(e)}")
            return False

    def test_subir_documento_exitoso(self):
        """Probar subida exitosa de documento PDF"""
        try:
            # Crear PDF de prueba
            self.temp_pdf_path = self.crear_pdf_prueba("historia_clinica_test.pdf", "Historia Clínica de Prueba")
            
            with open(self.temp_pdf_path, 'rb') as pdf_file:
                files = {'archivo': ('historia_clinica_test.pdf', pdf_file, 'application/pdf')}
                data = {
                    'tipo_documento': 'historia_clinica',
                    'descripcion': 'Historia clínica de prueba para testing',
                    'es_confidencial': 'true'
                }
                
                response = requests.post(
                    f"{self.base_url}/api/pacientes/{self.paciente_id}/documentos",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    data=data
                )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('status') == 'success':
                    self.documento_id = data['data']['id']
                    self.log_result("Subir Documento", True, f"Documento subido con ID: {self.documento_id}")
                    return True
                else:
                    self.log_result("Subir Documento", False, f"Error en respuesta: {data.get('message')}")
                    return False
            else:
                self.log_result("Subir Documento", False, f"Error HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Subir Documento", False, f"Error: {str(e)}")
            return False

    def test_validacion_archivo_no_pdf(self):
        """Probar que se rechacen archivos que no son PDF"""
        try:
            # Crear archivo que no es PDF
            temp_txt = self.crear_archivo_no_pdf("test_file.txt")
            
            with open(temp_txt, 'rb') as txt_file:
                files = {'archivo': ('test_file.txt', txt_file, 'text/plain')}
                data = {'tipo_documento': 'general'}
                
                response = requests.post(
                    f"{self.base_url}/api/pacientes/{self.paciente_id}/documentos",
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    data=data
                )
            
            # Limpiar archivo temporal
            os.remove(temp_txt)
            
            if response.status_code == 400:
                data = response.json()
                if "PDF" in data.get('message', ''):
                    self.log_result("Validación No-PDF", True, "Archivo no-PDF rechazado correctamente")
                    return True
                else:
                    self.log_result("Validación No-PDF", False, f"Mensaje de error inesperado: {data.get('message')}")
                    return False
            else:
                self.log_result("Validación No-PDF", False, f"Debería retornar 400, pero retornó: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Validación No-PDF", False, f"Error: {str(e)}")
            return False

    def test_listar_documentos_paciente(self):
        """Probar obtener lista de documentos de un paciente"""
        try:
            response = requests.get(
                f"{self.base_url}/api/pacientes/{self.paciente_id}/documentos",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    documentos = data.get('data', [])
                    # Verificar que nuestro documento está en la lista
                    documento_encontrado = any(doc['id'] == self.documento_id for doc in documentos)
                    if documento_encontrado:
                        self.log_result("Listar Documentos", True, f"Lista obtenida con {len(documentos)} documentos")
                        return True
                    else:
                        self.log_result("Listar Documentos", False, "Documento subido no aparece en la lista")
                        return False
                else:
                    self.log_result("Listar Documentos", False, f"Error en respuesta: {data.get('message')}")
                    return False
            else:
                self.log_result("Listar Documentos", False, f"Error HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Listar Documentos", False, f"Error: {str(e)}")
            return False

    def test_descargar_documento(self):
        """Probar descarga de documento"""
        try:
            response = requests.get(
                f"{self.base_url}/api/pacientes/{self.paciente_id}/documentos/{self.documento_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                # Verificar que es un PDF
                if response.headers.get('content-type') == 'application/pdf':
                    self.log_result("Descargar Documento", True, f"Documento descargado ({len(response.content)} bytes)")
                    return True
                else:
                    self.log_result("Descargar Documento", False, f"Tipo de contenido incorrecto: {response.headers.get('content-type')}")
                    return False
            else:
                self.log_result("Descargar Documento", False, f"Error HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Descargar Documento", False, f"Error: {str(e)}")
            return False

    def test_actualizar_documento(self):
        """Probar actualización de metadatos del documento"""
        try:
            update_data = {
                'descripcion': 'Historia clínica actualizada para testing',
                'es_confidencial': False,
                'tipo_documento': 'examenes_medicos'
            }
            
            response = requests.put(
                f"{self.base_url}/api/pacientes/{self.paciente_id}/documentos/{self.documento_id}",
                headers=self.get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Actualizar Documento", True, "Metadatos actualizados correctamente")
                    return True
                else:
                    self.log_result("Actualizar Documento", False, f"Error en respuesta: {data.get('message')}")
                    return False
            else:
                self.log_result("Actualizar Documento", False, f"Error HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Actualizar Documento", False, f"Error: {str(e)}")
            return False

    def test_estadisticas_documentos(self):
        """Probar endpoint de estadísticas de documentos"""
        try:
            response = requests.get(
                f"{self.base_url}/api/documentos/estadisticas",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    estadisticas = data.get('data', [])
                    self.log_result("Estadísticas", True, f"Estadísticas obtenidas: {len(estadisticas)} tipos de documento")
                    return True
                else:
                    self.log_result("Estadísticas", False, f"Error en respuesta: {data.get('message')}")
                    return False
            else:
                self.log_result("Estadísticas", False, f"Error HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Estadísticas", False, f"Error: {str(e)}")
            return False

    def test_eliminar_documento(self):
        """Probar eliminación de documento"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/pacientes/{self.paciente_id}/documentos/{self.documento_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Eliminar Documento", True, "Documento eliminado correctamente")
                    return True
                else:
                    self.log_result("Eliminar Documento", False, f"Error en respuesta: {data.get('message')}")
                    return False
            else:
                self.log_result("Eliminar Documento", False, f"Error HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Eliminar Documento", False, f"Error: {str(e)}")
            return False

    def test_paciente_inexistente(self):
        """Probar manejo de paciente inexistente"""
        try:
            # Crear PDF de prueba
            temp_pdf = self.crear_pdf_prueba("test_paciente_inexistente.pdf")
            
            with open(temp_pdf, 'rb') as pdf_file:
                files = {'archivo': ('test.pdf', pdf_file, 'application/pdf')}
                data = {'tipo_documento': 'general'}
                
                response = requests.post(
                    f"{self.base_url}/api/pacientes/99999/documentos",  # ID inexistente
                    headers={"Authorization": f"Bearer {self.token}"},
                    files=files,
                    data=data
                )
            
            # Limpiar archivo temporal
            os.remove(temp_pdf)
            
            if response.status_code == 404:
                self.log_result("Paciente Inexistente", True, "Error 404 para paciente inexistente")
                return True
            else:
                self.log_result("Paciente Inexistente", False, f"Debería retornar 404, pero retornó: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Paciente Inexistente", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas de API de Documentos de Pacientes")
        print("=" * 60)
        
        # Limpiar resultados anteriores
        self.test_results = []
        
        # Autenticación
        if not self.authenticate():
            print("❌ No se pudo autenticar. Abortando pruebas.")
            return False
        
        # Preparar paciente de prueba
        if not self.preparar_paciente_prueba():
            print("❌ No se pudo preparar paciente de prueba. Abortando pruebas.")
            return False
        
        # Ejecutar pruebas en orden
        tests = [
            self.test_subir_documento_exitoso,
            self.test_validacion_archivo_no_pdf,
            self.test_listar_documentos_paciente,
            self.test_descargar_documento,
            self.test_actualizar_documento,
            self.test_estadisticas_documentos,
            self.test_paciente_inexistente,
            self.test_eliminar_documento,  # Al final para limpiar
        ]
        
        for test in tests:
            test()
        
        # Limpiar archivos temporales
        self.limpiar_archivos_temporales()
        
        # Resumen
        self.print_summary()
        
        return all(result['success'] for result in self.test_results)

    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS - DOCUMENTOS DE PACIENTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print(f"✅ Pasaron: {passed_tests}")
        print(f"❌ Fallaron: {failed_tests}")
        print(f"Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ PRUEBAS FALLIDAS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("=" * 60)


def main():
    """Función principal para ejecutar las pruebas"""
    tester = TestDocumentosPacientesAPI()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("🎉 ¡Todas las pruebas pasaron exitosamente!")
            return 0
        else:
            print("⚠️  Algunas pruebas fallaron. Revisar logs arriba.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())