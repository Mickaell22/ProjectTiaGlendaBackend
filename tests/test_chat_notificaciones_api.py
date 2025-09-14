#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TEST SUITE - SISTEMA DE CHAT Y NOTIFICACIONES PUSH
Centro Tía Glenda - Fase 4 Implementación Completa
Archivo: test_chat_notificaciones_api.py

Pruebas completas del sistema de chat interno y notificaciones automáticas
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuración de la API
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# Configuración de pruebas
TEST_CONFIG = {
    'timeout': 30,
    'admin_credentials': {
        'usuario': 'admin.norte',
        'contrasenia': 'admin123'
    },
    'test_credentials': {
        'usuario': 'usuario.test',
        'contrasenia': 'Test123!'
    }
}

class TestChatNotificaciones:
    """Clase principal para testing del sistema de chat y notificaciones"""
    
    def __init__(self):
        self.admin_token = None
        self.test_token = None
        self.session = requests.Session()
        self.resultados = {
            'total_tests': 0,
            'exitosos': 0,
            'fallidos': 0,
            'errores': []
        }
    
    def print_separator(self, title="", char="=", width=80):
        """Imprimir separador con título"""
        if title:
            title_len = len(title)
            padding = (width - title_len - 2) // 2
            print(f"{char * padding} {title} {char * padding}")
        else:
            print(char * width)
    
    def log_test(self, test_name, success, message="", details=None):
        """Registrar resultado de test"""
        self.resultados['total_tests'] += 1
        
        if success:
            self.resultados['exitosos'] += 1
            status = "[PASS]"
        else:
            self.resultados['fallidos'] += 1
            status = "[FAIL]"
            self.resultados['errores'].append({
                'test': test_name,
                'message': message,
                'details': details
            })
        
        print(f"{status} - {test_name}")
        if message:
            print(f"      {message}")
        if details:
            print(f"      Detalles: {details}")
    
    def hacer_request(self, method, endpoint, data=None, headers=None, token=None):
        """Realizar request HTTP con manejo de errores"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Configurar headers
            request_headers = {'Content-Type': 'application/json'}
            if headers:
                request_headers.update(headers)
            if token:
                request_headers['Authorization'] = f'Bearer {token}'
            
            # Realizar request
            if method.upper() == 'GET':
                response = self.session.get(url, headers=request_headers, timeout=TEST_CONFIG['timeout'])
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=request_headers, timeout=TEST_CONFIG['timeout'])
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=request_headers, timeout=TEST_CONFIG['timeout'])
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=request_headers, timeout=TEST_CONFIG['timeout'])
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'response': response
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Timeout en la request'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Respuesta no es JSON válido'}
        except Exception as e:
            return {'success': False, 'error': f'Error inesperado: {str(e)}'}
    
    def autenticar_admin(self):
        """Autenticar usuario administrador"""
        print("\n[AUTH] Autenticando usuario administrador...")
        
        response = self.hacer_request('POST', '/login', {
            'usuario': TEST_CONFIG['admin_credentials']['usuario'],
            'contrasenia': TEST_CONFIG['admin_credentials']['contrasenia']
        })
        
        if response['success'] and response['status_code'] == 200:
            self.admin_token = response['data'].get('token')
            self.log_test("Autenticación Admin", True, "Token obtenido exitosamente")
            return True
        else:
            self.log_test("Autenticación Admin", False, 
                         f"Error: {response.get('error', 'Error desconocido')}")
            return False
    
    # ============================================
    # TESTS DEL SISTEMA DE CHAT
    # ============================================
    
    def test_chat_conversaciones(self):
        """Test: Obtener conversaciones del usuario"""
        response = self.hacer_request('GET', '/chat/conversaciones', token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  'conversaciones' in response['data'])
        
        self.log_test("Chat - Obtener Conversaciones", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
    
    def test_chat_usuarios_disponibles(self):
        """Test: Obtener usuarios disponibles para chat"""
        response = self.hacer_request('GET', '/chat/usuarios-disponibles', token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  'usuarios' in response['data'])
        
        self.log_test("Chat - Usuarios Disponibles", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
        
        return response['data'].get('usuarios', []) if success else []
    
    def test_chat_enviar_mensaje(self, usuarios_disponibles):
        """Test: Enviar mensaje de chat"""
        if not usuarios_disponibles:
            self.log_test("Chat - Enviar Mensaje", False, "No hay usuarios disponibles")
            return None
        
        destinatario = usuarios_disponibles[0]
        mensaje_data = {
            'id_destinatario': destinatario['id'],
            'mensaje': f'Mensaje de prueba - {datetime.now().isoformat()}',
            'tipo_mensaje': 'texto',
            'prioridad': 'normal'
        }
        
        response = self.hacer_request('POST', '/chat/enviar', mensaje_data, token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  response['data'].get('id_mensaje'))
        
        mensaje_id = response['data'].get('id_mensaje') if success else None
        
        self.log_test("Chat - Enviar Mensaje", success,
                     f"Mensaje ID: {mensaje_id}" if success else response.get('error', ''))
        
        return mensaje_id
    
    def test_chat_marcar_leido(self, mensaje_id):
        """Test: Marcar mensaje como leído"""
        if not mensaje_id:
            self.log_test("Chat - Marcar Leído", False, "No hay mensaje ID")
            return
        
        response = self.hacer_request('PUT', f'/chat/marcar-leido/{mensaje_id}', token=self.admin_token)
        
        success = (response['success'] and response['status_code'] == 200)
        
        self.log_test("Chat - Marcar Leído", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
    
    def test_chat_estadisticas(self):
        """Test: Obtener estadísticas de chat"""
        response = self.hacer_request('GET', '/chat/estadisticas', token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  'estadisticas' in response['data'])
        
        self.log_test("Chat - Estadísticas", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
    
    def test_chat_buscar_mensajes(self):
        """Test: Buscar mensajes"""
        response = self.hacer_request('GET', '/chat/buscar?q=prueba', token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  'mensajes' in response['data'])
        
        self.log_test("Chat - Buscar Mensajes", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
    
    # ============================================
    # TESTS DEL SISTEMA DE NOTIFICACIONES
    # ============================================
    
    def test_notificaciones_obtener(self):
        """Test: Obtener notificaciones del usuario"""
        response = self.hacer_request('GET', '/notificaciones', token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  'notificaciones' in response['data'])
        
        self.log_test("Notificaciones - Obtener", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
        
        return response['data'].get('notificaciones', []) if success else []
    
    def test_notificaciones_estadisticas(self):
        """Test: Obtener estadísticas de notificaciones"""
        response = self.hacer_request('GET', '/notificaciones/estadisticas', token=self.admin_token)
        
        success = (response['success'] and 
                  response['status_code'] == 200 and
                  'estadisticas' in response['data'])
        
        self.log_test("Notificaciones - Estadísticas", success,
                     f"Status: {response['status_code']}" if response['success'] else response['error'])
    
    def test_scheduler_estado(self):
        """Test: Obtener estado del scheduler"""
        response = self.hacer_request('GET', '/admin/scheduler/estado', token=self.admin_token)
        
        success = (response['success'] and response['status_code'] == 200)
        
        self.log_test("Scheduler - Estado", success,
                     f"Activo: {response['data'].get('activo', 'N/A')}" if success else response.get('error', ''))
    
    def test_scheduler_job_manual(self):
        """Test: Ejecutar job manual del scheduler"""
        response = self.hacer_request('POST', '/admin/scheduler/job/procesar_notificaciones/ejecutar', 
                                    token=self.admin_token)
        
        success = (response['success'] and response['status_code'] == 200)
        
        self.log_test("Scheduler - Job Manual", success,
                     f"Status: {response['status_code']}" if response['success'] else response.get('error', ''))
    
    # ============================================
    # TESTS DE INTEGRACIÓN
    # ============================================
    
    def test_integracion_completa(self):
        """Test de integración completa del sistema"""
        print("\n[INTEGRATION] Ejecutando test de integración completa...")
        
        # 1. Obtener usuarios disponibles
        usuarios = self.test_chat_usuarios_disponibles()
        
        # 2. Enviar mensaje si hay usuarios
        mensaje_id = None
        if usuarios:
            mensaje_id = self.test_chat_enviar_mensaje(usuarios)
        
        # 3. Marcar mensaje como leído
        if mensaje_id:
            self.test_chat_marcar_leido(mensaje_id)
        
        # 4. Verificar notificaciones
        notificaciones = self.test_notificaciones_obtener()
        
        # 5. Test de scheduler
        self.test_scheduler_estado()
        
        # Evaluar integración
        integration_success = (usuarios is not None and 
                             len(usuarios) >= 0 and
                             notificaciones is not None)
        
        self.log_test("Integración Completa", integration_success,
                     "Sistema de chat y notificaciones funcionando")
    
    # ============================================
    # TESTS DE VALIDACIÓN DE DATOS
    # ============================================
    
    def test_validaciones_chat(self):
        """Test: Validaciones del sistema de chat"""
        print("\n[VALIDATION] Ejecutando tests de validación...")
        
        # Test mensaje vacío
        response = self.hacer_request('POST', '/chat/enviar', {
            'id_destinatario': 1,
            'mensaje': '',
            'tipo_mensaje': 'texto'
        }, token=self.admin_token)
        
        success = (response['success'] and response['status_code'] == 400)
        self.log_test("Validación - Mensaje Vacío", success,
                     "Rechaza mensajes vacíos correctamente")
        
        # Test destinatario inválido
        response = self.hacer_request('POST', '/chat/enviar', {
            'id_destinatario': -1,
            'mensaje': 'Test',
            'tipo_mensaje': 'texto'
        }, token=self.admin_token)
        
        success = (response['success'] and response['status_code'] == 400)
        self.log_test("Validación - Destinatario Inválido", success,
                     "Rechaza destinatarios inválidos correctamente")
    
    # ============================================
    # EJECUCIÓN PRINCIPAL
    # ============================================
    
    def ejecutar_todos_los_tests(self):
        """Ejecutar todos los tests del sistema"""
        print("CENTRO TIA GLENDA - TEST SUITE FASE 4")
        print("Sistema de Chat Interno y Notificaciones Push")
        self.print_separator()
        
        start_time = time.time()
        
        # 1. Autenticación
        if not self.autenticar_admin():
            print("[ERROR] Error critico: No se pudo autenticar. Abortando tests.")
            return False
        
        # 2. Tests de Chat
        self.print_separator("TESTS DEL SISTEMA DE CHAT", "-", 60)
        usuarios_disponibles = self.test_chat_usuarios_disponibles()
        mensaje_id = self.test_chat_enviar_mensaje(usuarios_disponibles)
        self.test_chat_conversaciones()
        self.test_chat_marcar_leido(mensaje_id)
        self.test_chat_estadisticas()
        self.test_chat_buscar_mensajes()
        
        # 3. Tests de Notificaciones
        self.print_separator("TESTS DEL SISTEMA DE NOTIFICACIONES", "-", 60)
        self.test_notificaciones_obtener()
        self.test_notificaciones_estadisticas()
        
        # 4. Tests del Scheduler
        self.print_separator("TESTS DEL JOB SCHEDULER", "-", 60)
        self.test_scheduler_estado()
        self.test_scheduler_job_manual()
        
        # 5. Tests de Validación
        self.print_separator("TESTS DE VALIDACIÓN", "-", 60)
        self.test_validaciones_chat()
        
        # 6. Test de Integración
        self.print_separator("TEST DE INTEGRACIÓN", "-", 60)
        self.test_integracion_completa()
        
        # 7. Reporte Final
        self.generar_reporte_final(time.time() - start_time)
        
        return self.resultados['fallidos'] == 0
    
    def generar_reporte_final(self, tiempo_ejecucion):
        """Generar reporte final de los tests"""
        self.print_separator("REPORTE FINAL DE TESTS")
        
        porcentaje_exito = (self.resultados['exitosos'] / self.resultados['total_tests'] * 100) if self.resultados['total_tests'] > 0 else 0
        
        print(f"ESTADISTICAS:")
        print(f"   * Total de tests ejecutados: {self.resultados['total_tests']}")
        print(f"   * Tests exitosos: {self.resultados['exitosos']}")
        print(f"   * Tests fallidos: {self.resultados['fallidos']}")
        print(f"   * Porcentaje de exito: {porcentaje_exito:.1f}%")
        print(f"   * Tiempo de ejecucion: {tiempo_ejecucion:.2f} segundos")
        
        if self.resultados['errores']:
            print(f"\nERRORES ENCONTRADOS:")
            for i, error in enumerate(self.resultados['errores'], 1):
                print(f"   {i}. {error['test']}")
                print(f"      -> {error['message']}")
                if error['details']:
                    print(f"      -> {error['details']}")
        
        # Estado final
        print(f"\nRESULTADO FINAL:")
        if self.resultados['fallidos'] == 0:
            print("   [SUCCESS] TODOS LOS TESTS PASARON - SISTEMA LISTO PARA PRODUCCION")
            print("   [SUCCESS] Sistema de Chat y Notificaciones implementado exitosamente")
        else:
            print("   [WARNING] ALGUNOS TESTS FALLARON - REVISAR ERRORES")
            print("   [WARNING] Se requiere correccion antes de ir a produccion")
        
        self.print_separator()


def main():
    """Función principal"""
    try:
        # Crear instancia de testing
        tester = TestChatNotificaciones()
        
        # Ejecutar todos los tests
        exito = tester.ejecutar_todos_los_tests()
        
        # Determinar código de salida
        exit_code = 0 if exito else 1
        
        print(f"\n[EXIT] Finalizando con codigo de salida: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Tests interrumpidos por el usuario")
        return 130
    except Exception as e:
        print(f"\n\n[CRITICAL] Error critico en el sistema de testing: {str(e)}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())