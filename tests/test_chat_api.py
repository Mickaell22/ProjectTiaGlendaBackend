"""
test_chat_api.py
Tests para el sistema de chat interno
Centro Tía Glenda - Testing de Mensajería
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# Configuración base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

class ChatAPITest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.user_token = None
        self.test_users = {}
        self.test_messages = []
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
        print("\n[AUTH] Autenticando usuarios para tests de chat...")
        
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

        # Intentar autenticar usuario regular (si existe)
        try:
            login_data = {
                "usuario": "terapeuta.ana",
                "contrasenia": "admin123"
            }
            response = requests.post(f"{self.base_url}/api/login", 
                                   json=login_data, headers=self.headers)
            
            if response.status_code == 200:
                response_data = response.json()
                self.user_token = response_data['data']['token']
                self.test_users['terapeuta'] = {
                    'token': self.user_token,
                    'id': response_data['data']['user']['id'],
                    'nombre': response_data['data']['user']['nombre_completo']
                }
                self.print_test_result("Autenticación Usuario Regular", True, "Token obtenido exitosamente")
            else:
                self.print_test_result("Autenticación Usuario Regular", False, 
                                     f"Usuario terapeuta.ana no encontrado. Solo se usará admin.")
                # Continuamos con solo admin para tests básicos
        except Exception as e:
            self.print_test_result("Autenticación Usuario Regular", False, f"Excepción: {str(e)}")

        return len(self.test_users) > 0

    def test_obtener_usuarios_disponibles(self):
        """Test: Obtener usuarios disponibles para chat"""
        print("\n[USERS] Testeando obtención de usuarios disponibles...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/chat/usuarios-disponibles", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                users = response.json()['data']
                self.print_test_result("Obtener usuarios disponibles", True, 
                                     f"Encontrados {len(users)} usuarios", users[:2])
                return users
            else:
                self.print_test_result("Obtener usuarios disponibles", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener usuarios disponibles", False, f"Excepción: {str(e)}")
            return []

    def test_enviar_mensaje(self, id_destinatario=None):
        """Test: Enviar mensaje"""
        print("\n[MSG] Testeando envío de mensajes...")
        
        if not id_destinatario and len(self.test_users) > 1:
            # Si tenemos múltiples usuarios, enviar entre ellos
            users_list = list(self.test_users.values())
            id_destinatario = users_list[1]['id'] if users_list[0]['token'] == self.admin_token else users_list[0]['id']
        elif not id_destinatario:
            # Si solo tenemos un usuario, simular envío a ID ficticio (debería fallar elegantemente)
            id_destinatario = 999
        
        try:
            message_data = {
                "id_destinatario": id_destinatario,
                "mensaje": f"Test message from automated test - {datetime.now().isoformat()}",
                "tipo_mensaje": "texto",
                "prioridad": "normal"
            }
            
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{self.base_url}/api/chat/enviar", 
                                   json=message_data, headers=headers_with_token)
            
            if response.status_code == 200:
                message_info = response.json()['data']
                self.test_messages.append(message_info['id_mensaje'])
                self.print_test_result("Enviar mensaje", True, 
                                     f"Mensaje ID: {message_info['id_mensaje']}", message_data)
                return message_info['id_mensaje']
            else:
                self.print_test_result("Enviar mensaje", False, 
                                     f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.print_test_result("Enviar mensaje", False, f"Excepción: {str(e)}")
            return None

    def test_obtener_conversaciones(self):
        """Test: Obtener conversaciones del usuario"""
        print("\n[CONV] Testeando obtención de conversaciones...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/chat/conversaciones", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                conversations = response.json()['data']
                self.print_test_result("Obtener conversaciones", True, 
                                     f"Encontradas {len(conversations)} conversaciones", 
                                     conversations[:1])
                return conversations
            else:
                self.print_test_result("Obtener conversaciones", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener conversaciones", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_mensajes_conversacion(self, id_contacto):
        """Test: Obtener mensajes de conversación específica"""
        print("\n[MSGS] Testeando obtención de mensajes de conversación...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/chat/mensajes/{id_contacto}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                messages = response.json()['data']
                self.print_test_result("Obtener mensajes conversación", True, 
                                     f"Encontrados {len(messages)} mensajes", messages[:1])
                return messages
            else:
                self.print_test_result("Obtener mensajes conversación", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Obtener mensajes conversación", False, f"Excepción: {str(e)}")
            return []

    def test_marcar_mensaje_leido(self, id_mensaje):
        """Test: Marcar mensaje como leído"""
        print("\n[OK] Testeando marcar mensaje como leído...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.put(f"{self.base_url}/api/chat/marcar-leido/{id_mensaje}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Marcar mensaje leído", True, 
                                     f"Mensaje {id_mensaje} marcado como leído")
                return True
            else:
                self.print_test_result("Marcar mensaje leído", False, 
                                     f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Marcar mensaje leído", False, f"Excepción: {str(e)}")
            return False

    def test_buscar_mensajes(self):
        """Test: Buscar mensajes"""
        print("\n[SEARCH] Testeando búsqueda de mensajes...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            params = {"q": "test", "tipo_observacion": "texto"}
            response = requests.get(f"{self.base_url}/api/chat/buscar", 
                                  headers=headers_with_token, params=params)
            
            if response.status_code == 200:
                results = response.json()['data']
                self.print_test_result("Buscar mensajes", True, 
                                     f"Encontrados {len(results)} resultados", results[:1])
                return results
            else:
                self.print_test_result("Buscar mensajes", False, 
                                     f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.print_test_result("Buscar mensajes", False, f"Excepción: {str(e)}")
            return []

    def test_obtener_estadisticas(self):
        """Test: Obtener estadísticas de chat"""
        print("\n[SUMMARY] Testeando obtención de estadísticas...")
        
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/api/chat/estadisticas", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                stats = response.json()['data']
                self.print_test_result("Obtener estadísticas", True, 
                                     "Estadísticas obtenidas", stats)
                return stats
            else:
                self.print_test_result("Obtener estadísticas", False, 
                                     f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("Obtener estadísticas", False, f"Excepción: {str(e)}")
            return None

    def test_casos_error(self):
        """Test: Casos de error y validaciones"""
        print("\n[FAIL] Testeando casos de error...")
        
        # Test sin autenticación
        try:
            response = requests.get(f"{self.base_url}/api/chat/conversaciones", headers=self.headers)
            success = response.status_code == 401
            self.print_test_result("Error sin autenticación", success, 
                                 f"Status esperado 401, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error sin autenticación", False, f"Excepción: {str(e)}")

        # Test envío de mensaje vacío
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            message_data = {
                "id_destinatario": 1,
                "mensaje": "",
                "tipo_mensaje": "texto"
            }
            response = requests.post(f"{self.base_url}/api/chat/enviar", 
                                   json=message_data, headers=headers_with_token)
            success = response.status_code == 400
            self.print_test_result("Error mensaje vacío", success, 
                                 f"Status esperado 400, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error mensaje vacío", False, f"Excepción: {str(e)}")

        # Test destinatario inválido
        try:
            headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
            message_data = {
                "id_destinatario": -1,
                "mensaje": "Test",
                "tipo_mensaje": "texto"
            }
            response = requests.post(f"{self.base_url}/api/chat/enviar", 
                                   json=message_data, headers=headers_with_token)
            success = response.status_code == 400
            self.print_test_result("Error destinatario inválido", success, 
                                 f"Status esperado 400, obtenido: {response.status_code}")
        except Exception as e:
            self.print_test_result("Error destinatario inválido", False, f"Excepción: {str(e)}")

    def run_all_tests(self):
        """Ejecutar todos los tests de chat"""
        print("[START] INICIANDO TESTS DEL SISTEMA DE CHAT")
        print("=" * 60)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_users():
            print("[FAIL] No se pudo autenticar usuarios. Tests cancelados.")
            return False
        
        # Tests principales
        available_users = self.test_obtener_usuarios_disponibles()
        
        # Determinar destinatario para mensajes
        destinatario_id = None
        if available_users and len(available_users) > 0:
            destinatario_id = available_users[0]['id']
        
        # Enviar mensaje de prueba
        message_id = self.test_enviar_mensaje(destinatario_id)
        
        # Tests de conversaciones
        conversations = self.test_obtener_conversaciones()
        
        # Test mensajes de conversación (si hay conversaciones)
        if conversations and len(conversations) > 0:
            self.test_obtener_mensajes_conversacion(conversations[0]['id_conversacion'])
        
        # Marcar mensaje como leído (si se envió exitosamente)
        if message_id:
            self.test_marcar_mensaje_leido(message_id)
        
        # Tests adicionales
        self.test_buscar_mensajes()
        self.test_obtener_estadisticas()
        
        # Tests de casos de error
        self.test_casos_error()
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("[SUMMARY] RESUMEN DE TESTS DE CHAT")
        print("=" * 60)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"[OK] Exitosos: {self.results['passed']}")
        print(f"[FAIL] Fallidos: {self.results['failed']}")
        print(f"[TIME]  Duración: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\n[FAIL] ERRORES ENCONTRADOS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\n[RATE] Tasa de éxito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    tester = ChatAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n[SUCCESS] ¡Todos los tests de chat pasaron exitosamente!")
        return 0
    else:
        print("\n[FAILED] Algunos tests fallaron. Revisar logs arriba.")
        return 1

if __name__ == "__main__":
    exit(main())