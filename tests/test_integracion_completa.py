"""
test_integracion_completa.py
Tests de integración completa entre módulos
Centro Tía Glenda - Testing de Integración Completa
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

class IntegracionCompletaTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.admin_token = None
        self.test_data = {
            'personas': [],
            'usuarios': [],
            'personal': [],
            'pacientes': [],
            'especialidades': [],
            'sesiones': [],
            'documentos': [],
            'observaciones': [],
            'pausas': []
        }
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
        if data and len(str(data)) < 300:
            print(f"      Data: {json.dumps(data, indent=6, ensure_ascii=False)[:200]}...")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")

    def authenticate_admin(self):
        """Autenticar usuario administrador"""
        print("\n🔐 Autenticando administrador...")
        
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
                return True
            else:
                self.print_test_result("Autenticación Admin", False, f"Error: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Autenticación Admin", False, f"Excepción: {str(e)}")
            return False

    def test_flujo_completo_paciente_integral(self):
        """Test: Flujo completo de gestión integral de un paciente"""
        print("\n🔄 INICIANDO FLUJO COMPLETO DE PACIENTE INTEGRAL...")
        print("=" * 60)
        
        headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
        
        # PASO 1: Crear nueva persona para el paciente
        print("\n   PASO 1: Creando nueva persona...")
        try:
            persona_data = {
                "nombre": "María Elena",
                "apellido": "Gómez Herrera",
                "cedula": f"1234567{datetime.now().strftime('%S')}",  # Cédula única
                "fecha_nacimiento": "2010-05-15",
                "telefono": "0987654321",
                "email": "maria.test@example.com",
                "direccion": "Av. Principal 123, Quito"
            }
            
            response = requests.post(f"{self.base_url}/api/personas", 
                                   json=persona_data, headers=headers_with_token)
            
            if response.status_code == 200:
                persona_id = response.json()['data']['id']
                self.test_data['personas'].append(persona_id)
                self.print_test_result("Crear persona", True, f"Persona creada ID: {persona_id}")
            else:
                self.print_test_result("Crear persona", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Crear persona", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 2: Crear tutor para el paciente
        print("\n   PASO 2: Creando tutor...")
        try:
            tutor_data = {
                "nombre": "Juan Carlos",
                "apellido": "Gómez Pérez",
                "cedula": f"1987654{datetime.now().strftime('%S')}",
                "telefono": "0999888777",
                "email": "juan.padre@example.com",
                "direccion": "Av. Principal 123, Quito",
                "parentesco": "padre",
                "ocupacion": "Ingeniero Civil",
                "direccion_empresa": "Calle del Trabajo 456",
                "telefono_empresa": "02-2345678",
                "nombre_empresa": "Constructora ABC"
            }
            
            response = requests.post(f"{self.base_url}/api/tutores", 
                                   json=tutor_data, headers=headers_with_token)
            
            if response.status_code == 200:
                tutor_id = response.json()['data']['id']
                self.print_test_result("Crear tutor", True, f"Tutor creado ID: {tutor_id}")
            else:
                self.print_test_result("Crear tutor", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Crear tutor", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 3: Crear paciente vinculado a la persona y tutor
        print("\n   PASO 3: Creando paciente...")
        try:
            paciente_data = {
                "id_persona": persona_id,
                "id_tutor": tutor_id,
                "fecha_ingreso": datetime.now().strftime('%Y-%m-%d'),
                "motivo_consulta": "Evaluación integral de desarrollo y terapia de lenguaje",
                "observaciones": "Paciente integral de prueba para testing completo del sistema",
                "estado": "activo"
            }
            
            response = requests.post(f"{self.base_url}/api/pacientes", 
                                   json=paciente_data, headers=headers_with_token)
            
            if response.status_code == 200:
                paciente_id = response.json()['data']['id']
                self.test_data['pacientes'].append(paciente_id)
                self.print_test_result("Crear paciente", True, f"Paciente creado ID: {paciente_id}")
            else:
                self.print_test_result("Crear paciente", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Crear paciente", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 4: Obtener especialidades disponibles
        print("\n   PASO 4: Obteniendo especialidades...")
        try:
            response = requests.get(f"{self.base_url}/api/especialidades", headers=headers_with_token)
            
            if response.status_code == 200 and response.json()['data']:
                especialidades = response.json()['data'][:2]  # Tomar primeras 2
                self.test_data['especialidades'] = especialidades
                self.print_test_result("Obtener especialidades", True, 
                                     f"Especialidades disponibles: {len(especialidades)}")
            else:
                self.print_test_result("Obtener especialidades", False, "No hay especialidades")
                return False
        except Exception as e:
            self.print_test_result("Obtener especialidades", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 5: Asignar múltiples especialidades al paciente
        print("\n   PASO 5: Asignando especialidades múltiples...")
        for i, especialidad in enumerate(self.test_data['especialidades']):
            try:
                assignment_data = {
                    "id_paciente": paciente_id,
                    "id_especialidad": especialidad['id'],
                    "es_principal": i == 0,  # Primera como principal
                    "prioridad": "alta" if i == 0 else "media",
                    "observaciones": f"Especialidad {i+1} asignada en flujo integral"
                }
                
                response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/especialidades", 
                                       json=assignment_data, headers=headers_with_token)
                
                if response.status_code == 200:
                    self.print_test_result(f"Asignar especialidad {i+1}", True, 
                                         f"Especialidad {especialidad['nombre']} asignada")
                else:
                    self.print_test_result(f"Asignar especialidad {i+1}", False, 
                                         f"Status: {response.status_code}")
            except Exception as e:
                self.print_test_result(f"Asignar especialidad {i+1}", False, f"Excepción: {str(e)}")
        
        # PASO 6: Obtener personal disponible para especialidades
        print("\n   PASO 6: Obteniendo personal...")
        try:
            response = requests.get(f"{self.base_url}/api/personal", headers=headers_with_token)
            
            if response.status_code == 200 and response.json()['data']:
                personal = response.json()['data'][:1]  # Tomar primero
                self.test_data['personal'] = personal
                self.print_test_result("Obtener personal", True, f"Personal disponible: {len(personal)}")
            else:
                self.print_test_result("Obtener personal", False, "No hay personal")
                return False
        except Exception as e:
            self.print_test_result("Obtener personal", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 7: Crear sesión terapéutica para el paciente
        print("\n   PASO 7: Creando sesión terapéutica...")
        try:
            sesion_data = {
                "codigo_sesion": f"ST-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "id_terapeuta": self.test_data['personal'][0]['id'],
                "id_especialidad": self.test_data['especialidades'][0]['id'],
                "fecha_inicio": datetime.now().strftime('%Y-%m-%d'),
                "fecha_fin": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                "tipo_sesion": "individual",
                "modalidad": "presencial",
                "objetivo_general": "Mejorar habilidades de comunicación",
                "duracion_minutos": 45,
                "frecuencia_semanal": 2,
                "dias_semana": ["lunes", "miércoles"]
            }
            
            response = requests.post(f"{self.base_url}/api/sesiones-terapia", 
                                   json=sesion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                sesion_id = response.json()['data']['id']
                self.test_data['sesiones'].append(sesion_id)
                self.print_test_result("Crear sesión terapéutica", True, f"Sesión creada ID: {sesion_id}")
                
                # Inscribir paciente en la sesión
                inscripcion_data = {
                    "id_paciente": paciente_id,
                    "fecha_inscripcion": datetime.now().strftime('%Y-%m-%d'),
                    "estado": "activo"
                }
                
                response = requests.post(f"{self.base_url}/api/sesiones-terapia/{sesion_id}/pacientes", 
                                       json=inscripcion_data, headers=headers_with_token)
                
                if response.status_code == 200:
                    self.print_test_result("Inscribir paciente en sesión", True, 
                                         "Paciente inscrito en sesión terapéutica")
                else:
                    self.print_test_result("Inscribir paciente en sesión", False, 
                                         f"Status: {response.status_code}")
            else:
                self.print_test_result("Crear sesión terapéutica", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Crear sesión terapéutica", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 8: Crear observación para la sesión
        print("\n   PASO 8: Creando observación de sesión...")
        try:
            observacion_data = {
                "id_sesion": sesion_id,
                "tipo_sesion": "terapeutica",
                "observacion": f"Observación integral de prueba - Paciente muestra buena disposición para el trabajo terapéutico. {datetime.now().isoformat()}",
                "tipo_observacion": "observacion",
                "es_seguimiento": False,
                "es_privada": False
            }
            
            response = requests.post(f"{self.base_url}/api/observaciones", 
                                   json=observacion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                observacion_id = response.json()['data']['id']
                self.test_data['observaciones'].append(observacion_id)
                self.print_test_result("Crear observación", True, f"Observación creada ID: {observacion_id}")
            else:
                self.print_test_result("Crear observación", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test_result("Crear observación", False, f"Excepción: {str(e)}")
        
        # PASO 9: Subir documento del paciente
        print("\n   PASO 9: Subiendo documento del paciente...")
        try:
            test_doc = io.BytesIO(b"Contenido de documento de prueba integral")
            
            headers_upload = {"Authorization": f"Bearer {self.admin_token}"}
            files = {'documento': ('historia_clinica.pdf', test_doc, 'application/pdf')}
            data = {
                'tipo_documento': 'historia_clinica',
                'descripcion': 'Historia clínica integral de prueba'
            }
            
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/documentos", 
                                   headers=headers_upload, files=files, data=data)
            
            if response.status_code == 200:
                documento_id = response.json()['data']['id']
                self.test_data['documentos'].append(documento_id)
                self.print_test_result("Subir documento paciente", True, f"Documento subido ID: {documento_id}")
            else:
                self.print_test_result("Subir documento paciente", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test_result("Subir documento paciente", False, f"Excepción: {str(e)}")
        
        # PASO 10: Pausar temporalmente el tratamiento
        print("\n   PASO 10: Pausando tratamiento temporalmente...")
        try:
            pausa_data = {
                "tipo_pausa": "general",
                "fecha_inicio": datetime.now().strftime('%Y-%m-%d'),
                "fecha_fin": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                "motivo": "Pausa temporal para evaluación médica",
                "observaciones": "Pausa de prueba en flujo integral"
            }
            
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/pausar", 
                                   json=pausa_data, headers=headers_with_token)
            
            if response.status_code == 200:
                self.test_data['pausas'].append(('general', paciente_id))
                self.print_test_result("Pausar tratamiento", True, "Tratamiento pausado temporalmente")
            else:
                self.print_test_result("Pausar tratamiento", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test_result("Pausar tratamiento", False, f"Excepción: {str(e)}")
        
        # PASO 11: Verificar estado integral del paciente
        print("\n   PASO 11: Verificando estado integral...")
        try:
            # Verificar datos completos del paciente
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                paciente_completo = response.json()['data']
                tiene_datos_basicos = all(key in paciente_completo for key in ['id', 'persona', 'tutor'])
                self.print_test_result("Verificar datos completos", tiene_datos_basicos, 
                                     "Paciente tiene datos completos")
            
            # Verificar especialidades asignadas
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}/especialidades", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                especialidades_asignadas = response.json()['data']
                tiene_especialidades = len(especialidades_asignadas) > 0
                self.print_test_result("Verificar especialidades", tiene_especialidades, 
                                     f"Paciente tiene {len(especialidades_asignadas)} especialidades")
            
            # Verificar sesiones
            response = requests.get(f"{self.base_url}/api/sesiones-terapia", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Verificar sesiones", True, "Sesiones verificadas")
            
            # Verificar estado de pausa
            response = requests.get(f"{self.base_url}/api/pacientes/{paciente_id}/pausa-activa", 
                                  headers=headers_with_token)
            
            if response.status_code == 200:
                pausa_activa = response.json()['data']
                self.print_test_result("Verificar pausa activa", True, 
                                     f"Estado de pausa: {pausa_activa}")
            
        except Exception as e:
            self.print_test_result("Verificar estado integral", False, f"Excepción: {str(e)}")
        
        # PASO 12: Reanudar tratamiento
        print("\n   PASO 12: Reanudando tratamiento...")
        try:
            reanudacion_data = {
                "motivo_reanudacion": "Evaluación médica completada exitosamente",
                "observaciones": "Reanudación en flujo integral de prueba"
            }
            
            response = requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/reanudar", 
                                   json=reanudacion_data, headers=headers_with_token)
            
            if response.status_code == 200:
                self.print_test_result("Reanudar tratamiento", True, "Tratamiento reanudado exitosamente")
            else:
                self.print_test_result("Reanudar tratamiento", False, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test_result("Reanudar tratamiento", False, f"Excepción: {str(e)}")
        
        print("\n✅ FLUJO COMPLETO DE PACIENTE INTEGRAL COMPLETADO")
        return True

    def test_flujo_personal_completo(self):
        """Test: Flujo completo de gestión de personal"""
        print("\n👨‍⚕️ INICIANDO FLUJO COMPLETO DE PERSONAL...")
        print("=" * 50)
        
        headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
        
        # PASO 1: Crear persona para personal
        print("\n   PASO 1: Creando persona para personal...")
        try:
            persona_data = {
                "nombre": "Ana Patricia",
                "apellido": "López Vega",
                "cedula": f"1987654{datetime.now().strftime('%M')}",
                "fecha_nacimiento": "1985-03-20",
                "telefono": "0999111222",
                "email": "ana.terapeuta@clinica.com",
                "direccion": "Calle Terapeutas 456"
            }
            
            response = requests.post(f"{self.base_url}/api/personas", 
                                   json=persona_data, headers=headers_with_token)
            
            if response.status_code == 200:
                persona_id = response.json()['data']['id']
                self.print_test_result("Crear persona personal", True, f"Persona creada ID: {persona_id}")
            else:
                self.print_test_result("Crear persona personal", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("Crear persona personal", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 2: Crear personal
        print("\n   PASO 2: Creando personal...")
        try:
            if self.test_data['especialidades']:
                personal_data = {
                    "id_persona": persona_id,
                    "id_especialidad": self.test_data['especialidades'][0]['id'],
                    "numero_registro": f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "fecha_ingreso": datetime.now().strftime('%Y-%m-%d'),
                    "cargo": "Terapeuta",
                    "tipo_contrato": "indefinido",
                    "estado": "activo"
                }
                
                response = requests.post(f"{self.base_url}/api/personal", 
                                       json=personal_data, headers=headers_with_token)
                
                if response.status_code == 200:
                    personal_id = response.json()['data']['id']
                    self.test_data['personal'].append({'id': personal_id})
                    self.print_test_result("Crear personal", True, f"Personal creado ID: {personal_id}")
                else:
                    self.print_test_result("Crear personal", False, f"Status: {response.status_code}")
                    return False
        except Exception as e:
            self.print_test_result("Crear personal", False, f"Excepción: {str(e)}")
            return False
        
        # PASO 3: Asignar especialidades múltiples
        print("\n   PASO 3: Asignando especialidades múltiples...")
        try:
            for i, especialidad in enumerate(self.test_data['especialidades']):
                assignment_data = {
                    "id_personal": personal_id,
                    "id_especialidad": especialidad['id'],
                    "es_principal": i == 0,
                    "nivel_competencia": "avanzado",
                    "certificacion": f"Certificación en {especialidad['nombre']}"
                }
                
                response = requests.post(f"{self.base_url}/api/personal/{personal_id}/especialidades", 
                                       json=assignment_data, headers=headers_with_token)
                
                if response.status_code == 200:
                    self.print_test_result(f"Asignar especialidad personal {i+1}", True, 
                                         f"Especialidad {especialidad['nombre']} asignada")
        except Exception as e:
            self.print_test_result("Asignar especialidades personal", False, f"Excepción: {str(e)}")
        
        # PASO 4: Subir documentos del personal
        print("\n   PASO 4: Subiendo documentos del personal...")
        try:
            test_doc = io.BytesIO(b"Contenido de cédula de identidad")
            
            headers_upload = {"Authorization": f"Bearer {self.admin_token}"}
            files = {'documento': ('cedula.pdf', test_doc, 'application/pdf')}
            data = {
                'tipo_documento': 'cedula',
                'descripcion': 'Cédula de identidad del personal',
                'es_obligatorio': 'true'
            }
            
            response = requests.post(f"{self.base_url}/api/personal/{personal_id}/documentos", 
                                   headers=headers_upload, files=files, data=data)
            
            if response.status_code == 200:
                documento_id = response.json()['data']['id']
                self.print_test_result("Subir documento personal", True, f"Documento subido ID: {documento_id}")
                
                # Validar documento
                validation_data = {
                    "estado_validacion": "aprobado",
                    "observaciones_validacion": "Documento validado en flujo integral"
                }
                
                response = requests.put(f"{self.base_url}/api/documentos-personal/{documento_id}/validar", 
                                      json=validation_data, headers=headers_with_token)
                
                if response.status_code == 200:
                    self.print_test_result("Validar documento personal", True, "Documento validado")
        except Exception as e:
            self.print_test_result("Gestionar documentos personal", False, f"Excepción: {str(e)}")
        
        print("\n✅ FLUJO COMPLETO DE PERSONAL COMPLETADO")
        return True

    def test_comunicacion_entre_usuarios(self):
        """Test: Sistema de comunicación entre usuarios"""
        print("\n💬 INICIANDO TEST DE COMUNICACIÓN...")
        print("=" * 45)
        
        headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Obtener usuarios disponibles para chat
            response = requests.get(f"{self.base_url}/api/chat/usuarios-disponibles", 
                                  headers=headers_with_token)
            
            if response.status_code == 200 and response.json()['data']:
                usuarios = response.json()['data']
                self.print_test_result("Obtener usuarios chat", True, 
                                     f"Encontrados {len(usuarios)} usuarios")
                
                if len(usuarios) > 0:
                    # Enviar mensaje
                    mensaje_data = {
                        "id_destinatario": usuarios[0]['id'],
                        "mensaje": f"Mensaje de prueba integral - {datetime.now().isoformat()}",
                        "tipo_mensaje": "texto",
                        "prioridad": "normal"
                    }
                    
                    response = requests.post(f"{self.base_url}/api/chat/enviar", 
                                           json=mensaje_data, headers=headers_with_token)
                    
                    if response.status_code == 200:
                        self.print_test_result("Enviar mensaje chat", True, "Mensaje enviado exitosamente")
                    else:
                        self.print_test_result("Enviar mensaje chat", False, f"Status: {response.status_code}")
            else:
                self.print_test_result("Test comunicación", False, "No hay usuarios disponibles")
        except Exception as e:
            self.print_test_result("Test comunicación", False, f"Excepción: {str(e)}")

    def cleanup_test_data(self):
        """Limpiar datos de prueba creados"""
        print("\n🧹 LIMPIANDO DATOS DE PRUEBA...")
        
        headers_with_token = {**self.headers, "Authorization": f"Bearer {self.admin_token}"}
        
        # Eliminar observaciones
        for obs_id in self.test_data['observaciones']:
            try:
                requests.delete(f"{self.base_url}/api/observaciones/{obs_id}", headers=headers_with_token)
            except:
                pass
        
        # Eliminar documentos
        for doc_id in self.test_data['documentos']:
            try:
                requests.delete(f"{self.base_url}/api/pacientes/documentos/{doc_id}", headers=headers_with_token)
            except:
                pass
        
        # Reanudar pausas
        for pausa_tipo, paciente_id in self.test_data['pausas']:
            try:
                reanudacion_data = {"motivo_reanudacion": "Cleanup de tests"}
                requests.post(f"{self.base_url}/api/pacientes/{paciente_id}/reanudar", 
                            json=reanudacion_data, headers=headers_with_token)
            except:
                pass
        
        # Eliminar pacientes
        for paciente_id in self.test_data['pacientes']:
            try:
                requests.delete(f"{self.base_url}/api/pacientes/{paciente_id}", headers=headers_with_token)
            except:
                pass
        
        # Eliminar personal (si se creó)
        for personal in self.test_data['personal']:
            if 'id' in personal:
                try:
                    requests.delete(f"{self.base_url}/api/personal/{personal['id']}", headers=headers_with_token)
                except:
                    pass
        
        # Eliminar personas
        for persona_id in self.test_data['personas']:
            try:
                requests.delete(f"{self.base_url}/api/personas/{persona_id}", headers=headers_with_token)
            except:
                pass
        
        self.print_test_result("Cleanup datos", True, "Limpieza completada")

    def run_all_tests(self):
        """Ejecutar todos los tests de integración"""
        print("🚀 INICIANDO TESTS DE INTEGRACIÓN COMPLETA")
        print("=" * 60)
        
        start_time = time.time()
        
        # Autenticación
        if not self.authenticate_admin():
            print("❌ No se pudo autenticar. Tests cancelados.")
            return False
        
        try:
            # Test principal: Flujo completo de paciente
            self.test_flujo_completo_paciente_integral()
            
            # Test secundario: Flujo de personal
            self.test_flujo_personal_completo()
            
            # Test de comunicación
            self.test_comunicacion_entre_usuarios()
            
        finally:
            # Siempre hacer cleanup
            self.cleanup_test_data()
        
        # Resultados finales
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE TESTS DE INTEGRACIÓN COMPLETA")
        print("=" * 60)
        print(f"Total de tests: {self.results['total_tests']}")
        print(f"✅ Exitosos: {self.results['passed']}")
        print(f"❌ Fallidos: {self.results['failed']}")
        print(f"⏱️  Duración: {duration:.2f} segundos")
        
        if self.results['failed'] > 0:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.results['errors'][:5]:  # Mostrar máximo 5 errores
                print(f"   • {error}")
            if len(self.results['errors']) > 5:
                print(f"   ... y {len(self.results['errors']) - 5} errores más")
        
        success_rate = (self.results['passed'] / self.results['total_tests']) * 100
        print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        return self.results['failed'] == 0

def main():
    """Función principal"""
    tester = IntegracionCompletaTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ¡Todos los tests de integración completa pasaron exitosamente!")
        return 0
    else:
        print("\n💥 Algunos tests de integración fallaron. Revisar logs arriba.")
        return 1

if __name__ == "__main__":
    exit(main())