# src/api/Components/ConfiguracionComponent.py
from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
import json

class ConfiguracionComponent:
    
    def __init__(self):
        self.db = DataBaseHandle()
    
    # ============================================
    # MÉTODOS DE CONFIGURACIÓN GENERAL
    # ============================================
    
    def get_configuracion_general(self):
        """Obtener configuración general del sistema"""
        try:
            query = """
                SELECT 
                    nombre_centro,
                    logo_url,
                    direccion,
                    telefono,
                    email,
                    horario_inicio,
                    horario_fin,
                    zona_horaria,
                    formato_fecha,
                    formato_hora,
                    moneda,
                    idioma,
                    descripcion
                FROM configuracion_general 
                WHERE id = 1
            """
            
            result = self.db.getRecords(query)
            
            if result and len(result) > 0:
                config = result[0]
                return {
                    'success': True,
                    'data': {
                        'nombre_centro': config.get('nombre_centro'),
                        'logo_url': config.get('logo_url'),
                        'direccion': config.get('direccion'),
                        'telefono': config.get('telefono'),
                        'email': config.get('email'),
                        'horario_inicio': str(config.get('horario_inicio')) if config.get('horario_inicio') else None,
                        'horario_fin': str(config.get('horario_fin')) if config.get('horario_fin') else None,
                        'zona_horaria': config.get('zona_horaria'),
                        'formato_fecha': config.get('formato_fecha'),
                        'formato_hora': config.get('formato_hora'),
                        'moneda': config.get('moneda'),
                        'idioma': config.get('idioma'),
                        'descripcion': config.get('descripcion')
                    }
                }
            else:
                # Devolver configuración por defecto si no existe
                return {
                    'success': True,
                    'data': {
                        'nombre_centro': 'Centro Tía Glenda',
                        'logo_url': None,
                        'direccion': '',
                        'telefono': '',
                        'email': '',
                        'horario_inicio': '08:00:00',
                        'horario_fin': '17:00:00',
                        'zona_horaria': 'America/Guayaquil',
                        'formato_fecha': 'DD/MM/YYYY',
                        'formato_hora': '24h',
                        'moneda': 'USD',
                        'idioma': 'es',
                        'descripcion': ''
                    }
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en get_configuracion_general: {str(e)}")
            return {
                'success': False,
                'message': f'Error obteniendo configuración general: {str(e)}'
            }
    
    def update_configuracion_general(self, data):
        """Actualizar configuración general del sistema"""
        try:
            # Verificar si existe el registro
            check_query = "SELECT COUNT(*) as count FROM configuracion_general WHERE id = 1"
            check_result = self.db.getRecords(check_query)
            
            exists = check_result and len(check_result) > 0 and check_result[0].get('count', 0) > 0
            
            if exists:
                # Actualizar registro existente
                query = """
                    UPDATE configuracion_general SET
                        nombre_centro = %s,
                        logo_url = %s,
                        direccion = %s,
                        telefono = %s,
                        email = %s,
                        horario_inicio = %s,
                        horario_fin = %s,
                        zona_horaria = %s,
                        formato_fecha = %s,
                        formato_hora = %s,
                        moneda = %s,
                        idioma = %s,
                        descripcion = %s,
                        fecha_modificacion = NOW()
                    WHERE id = 1
                """
            else:
                # Crear nuevo registro
                query = """
                    INSERT INTO configuracion_general (
                        id, nombre_centro, logo_url, direccion, telefono, email,
                        horario_inicio, horario_fin, zona_horaria, formato_fecha,
                        formato_hora, moneda, idioma, descripcion,
                        fecha_creacion, fecha_modificacion
                    ) VALUES (
                        1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                """
            
            params = (
                data.get('nombre_centro'),
                data.get('logo_url'),
                data.get('direccion'),
                data.get('telefono'),
                data.get('email'),
                data.get('horario_inicio'),
                data.get('horario_fin'),
                data.get('zona_horaria'),
                data.get('formato_fecha'),
                data.get('formato_hora'),
                data.get('moneda'),
                data.get('idioma'),
                data.get('descripcion')
            )
            
            result = self.db.ExecuteNonQuery(query, params)
            
            if result:
                return {
                    'success': True,
                    'message': 'Configuración general actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando configuración general'
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en update_configuracion_general: {str(e)}")
            return {
                'success': False,
                'message': f'Error actualizando configuración general: {str(e)}'
            }
    
    # ============================================
    # MÉTODOS DE CONFIGURACIÓN DE SESIONES
    # ============================================
    
    def get_configuracion_sesiones(self):
        """Obtener configuración de sesiones terapéuticas y pedagógicas"""
        try:
            query = """
                SELECT 
                    duracion_sesion_terapia,
                    duracion_clase_pedagogica,
                    tolerancia_llegada_tarde,
                    tiempo_recordatorio,
                    permitir_cancelacion_horas,
                    permitir_reprogramacion_horas,
                    capacidad_maxima_clase,
                    sistema_calificaciones,
                    escala_calificacion_min,
                    escala_calificacion_max
                FROM configuracion_sesiones 
                WHERE id = 1
            """
            
            result = self.db.getRecords(query)
            
            if result and len(result) > 0:
                config = result[0]
                return {
                    'success': True,
                    'data': {
                        'duracion_sesion_terapia': config.get('duracion_sesion_terapia'),
                        'duracion_clase_pedagogica': config.get('duracion_clase_pedagogica'),
                        'tolerancia_llegada_tarde': config.get('tolerancia_llegada_tarde'),
                        'tiempo_recordatorio': config.get('tiempo_recordatorio'),
                        'permitir_cancelacion_horas': config.get('permitir_cancelacion_horas'),
                        'permitir_reprogramacion_horas': config.get('permitir_reprogramacion_horas'),
                        'capacidad_maxima_clase': config.get('capacidad_maxima_clase'),
                        'sistema_calificaciones': config.get('sistema_calificaciones'),
                        'escala_calificacion_min': config.get('escala_calificacion_min'),
                        'escala_calificacion_max': config.get('escala_calificacion_max')
                    }
                }
            else:
                # Devolver configuración por defecto
                return {
                    'success': True,
                    'data': {
                        'duracion_sesion_terapia': 60,
                        'duracion_clase_pedagogica': 45,
                        'tolerancia_llegada_tarde': 15,
                        'tiempo_recordatorio': 15,
                        'permitir_cancelacion_horas': 24,
                        'permitir_reprogramacion_horas': 24,
                        'capacidad_maxima_clase': 12,
                        'sistema_calificaciones': 'numerico',
                        'escala_calificacion_min': 1,
                        'escala_calificacion_max': 10
                    }
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en get_configuracion_sesiones: {str(e)}")
            return {
                'success': False,
                'message': f'Error obteniendo configuración de sesiones: {str(e)}'
            }
    
    def update_configuracion_sesiones(self, data):
        """Actualizar configuración de sesiones"""
        try:
            # Verificar si existe el registro
            check_query = "SELECT COUNT(*) as count FROM configuracion_sesiones WHERE id = 1"
            check_result = self.db.getRecords(check_query)
            
            exists = check_result and len(check_result) > 0 and check_result[0].get('count', 0) > 0
            
            if exists:
                # Actualizar registro existente
                query = """
                    UPDATE configuracion_sesiones SET
                        duracion_sesion_terapia = %s,
                        duracion_clase_pedagogica = %s,
                        tolerancia_llegada_tarde = %s,
                        tiempo_recordatorio = %s,
                        permitir_cancelacion_horas = %s,
                        permitir_reprogramacion_horas = %s,
                        capacidad_maxima_clase = %s,
                        sistema_calificaciones = %s,
                        escala_calificacion_min = %s,
                        escala_calificacion_max = %s,
                        fecha_modificacion = NOW()
                    WHERE id = 1
                """
            else:
                # Crear nuevo registro
                query = """
                    INSERT INTO configuracion_sesiones (
                        id, duracion_sesion_terapia, duracion_clase_pedagogica,
                        tolerancia_llegada_tarde, tiempo_recordatorio,
                        permitir_cancelacion_horas, permitir_reprogramacion_horas,
                        capacidad_maxima_clase, sistema_calificaciones,
                        escala_calificacion_min, escala_calificacion_max,
                        fecha_creacion, fecha_modificacion
                    ) VALUES (
                        1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                """
            
            params = (
                data.get('duracion_sesion_terapia'),
                data.get('duracion_clase_pedagogica'),
                data.get('tolerancia_llegada_tarde'),
                data.get('tiempo_recordatorio'),
                data.get('permitir_cancelacion_horas'),
                data.get('permitir_reprogramacion_horas'),
                data.get('capacidad_maxima_clase'),
                data.get('sistema_calificaciones'),
                data.get('escala_calificacion_min'),
                data.get('escala_calificacion_max')
            )
            
            result = self.db.ExecuteNonQuery(query, params)
            
            if result:
                return {
                    'success': True,
                    'message': 'Configuración de sesiones actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando configuración de sesiones'
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en update_configuracion_sesiones: {str(e)}")
            return {
                'success': False,
                'message': f'Error actualizando configuración de sesiones: {str(e)}'
            }
    
    # ============================================
    # MÉTODOS DE CONFIGURACIÓN DE NOTIFICACIONES
    # ============================================
    
    def get_configuracion_notificaciones(self, user_id=None):
        """Obtener configuración de notificaciones (global o por usuario)"""
        try:
            if user_id:
                # Configuración específica de usuario
                query = """
                    SELECT 
                        notificaciones_habilitadas,
                        notificaciones_sesion_terapia,
                        notificaciones_clase_pedagogica,
                        notificaciones_cancelaciones,
                        notificaciones_reprogramaciones,
                        tiempo_anticipacion_minutos,
                        sonido_habilitado,
                        modo_silencioso_inicio,
                        modo_silencioso_fin
                    FROM configuracion_notificaciones_usuario 
                    WHERE user_id = %s
                """
                params = (user_id,)
            else:
                # Configuración global
                query = """
                    SELECT 
                        notificaciones_habilitadas,
                        notificaciones_sesion_terapia,
                        notificaciones_clase_pedagogica,
                        notificaciones_cancelaciones,
                        notificaciones_reprogramaciones,
                        tiempo_anticipacion_minutos,
                        sonido_habilitado
                    FROM configuracion_notificaciones_global 
                    WHERE id = 1
                """
                params = None
            
            result = self.db.getRecords(query, params)
            
            if result and len(result) > 0:
                config = result[0]
                data = {
                    'notificaciones_habilitadas': config.get('notificaciones_habilitadas', True),
                    'notificaciones_sesion_terapia': config.get('notificaciones_sesion_terapia', True),
                    'notificaciones_clase_pedagogica': config.get('notificaciones_clase_pedagogica', True),
                    'notificaciones_cancelaciones': config.get('notificaciones_cancelaciones', True),
                    'notificaciones_reprogramaciones': config.get('notificaciones_reprogramaciones', True),
                    'tiempo_anticipacion_minutos': config.get('tiempo_anticipacion_minutos', 15),
                    'sonido_habilitado': config.get('sonido_habilitado', True)
                }
                
                if user_id:
                    data.update({
                        'modo_silencioso_inicio': str(config.get('modo_silencioso_inicio')) if config.get('modo_silencioso_inicio') else None,
                        'modo_silencioso_fin': str(config.get('modo_silencioso_fin')) if config.get('modo_silencioso_fin') else None
                    })
                
                return {
                    'success': True,
                    'data': data
                }
            else:
                # Devolver configuración por defecto
                default_data = {
                    'notificaciones_habilitadas': True,
                    'notificaciones_sesion_terapia': True,
                    'notificaciones_clase_pedagogica': True,
                    'notificaciones_cancelaciones': True,
                    'notificaciones_reprogramaciones': True,
                    'tiempo_anticipacion_minutos': 15,
                    'sonido_habilitado': True
                }
                
                if user_id:
                    default_data.update({
                        'modo_silencioso_inicio': None,
                        'modo_silencioso_fin': None
                    })
                
                return {
                    'success': True,
                    'data': default_data
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en get_configuracion_notificaciones: {str(e)}")
            return {
                'success': False,
                'message': f'Error obteniendo configuración de notificaciones: {str(e)}'
            }
    
    def update_configuracion_notificaciones(self, data, user_id=None):
        """Actualizar configuración de notificaciones"""
        try:
            if user_id:
                # Configuración específica de usuario
                check_query = "SELECT COUNT(*) as count FROM configuracion_notificaciones_usuario WHERE user_id = %s"
                check_params = (user_id,)
                table_name = "configuracion_notificaciones_usuario"
                where_clause = "user_id = %s"
                where_params = (user_id,)
                insert_id_field = "user_id"
                insert_id_value = user_id
            else:
                # Configuración global
                check_query = "SELECT COUNT(*) as count FROM configuracion_notificaciones_global WHERE id = 1"
                check_params = None
                table_name = "configuracion_notificaciones_global"
                where_clause = "id = 1"
                where_params = (1,)
                insert_id_field = "id"
                insert_id_value = 1
            
            check_result = self.db.getRecords(check_query, check_params)
            exists = check_result and len(check_result) > 0 and check_result[0].get('count', 0) > 0
            
            base_fields = [
                'notificaciones_habilitadas', 'notificaciones_sesion_terapia',
                'notificaciones_clase_pedagogica', 'notificaciones_cancelaciones',
                'notificaciones_reprogramaciones', 'tiempo_anticipacion_minutos', 
                'sonido_habilitado'
            ]
            
            if user_id:
                fields = base_fields + ['modo_silencioso_inicio', 'modo_silencioso_fin']
            else:
                fields = base_fields
            
            if exists:
                # Actualizar registro existente
                set_clause = ", ".join([f"{field} = %s" for field in fields])
                query = f"""
                    UPDATE {table_name} SET
                        {set_clause},
                        fecha_modificacion = NOW()
                    WHERE {where_clause}
                """
                params = [data.get(field) for field in fields] + list(where_params)
            else:
                # Crear nuevo registro
                fields_clause = ", ".join([insert_id_field] + fields + ['fecha_creacion', 'fecha_modificacion'])
                values_clause = ", ".join(['%s'] * (len(fields) + 3))
                query = f"""
                    INSERT INTO {table_name} ({fields_clause})
                    VALUES ({values_clause})
                """
                params = [insert_id_value] + [data.get(field) for field in fields] + ['NOW()', 'NOW()']
            
            result = self.db.ExecuteNonQuery(query, params)
            
            if result:
                return {
                    'success': True,
                    'message': 'Configuración de notificaciones actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando configuración de notificaciones'
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en update_configuracion_notificaciones: {str(e)}")
            return {
                'success': False,
                'message': f'Error actualizando configuración de notificaciones: {str(e)}'
            }
    
    # ============================================
    # MÉTODOS DE CONFIGURACIÓN DE SEGURIDAD
    # ============================================
    
    def get_configuracion_seguridad(self):
        """Obtener configuración de seguridad del sistema"""
        try:
            query = """
                SELECT 
                    longitud_minima_password,
                    requerir_mayusculas,
                    requerir_minusculas,
                    requerir_numeros,
                    requerir_simbolos,
                    expiracion_password_dias,
                    tiempo_sesion_minutos,
                    intentos_login_maximo,
                    tiempo_bloqueo_minutos,
                    habilitar_2fa,
                    audit_log_habilitado,
                    retener_logs_dias
                FROM configuracion_seguridad 
                WHERE id = 1
            """
            
            result = self.db.getRecords(query)
            
            if result and len(result) > 0:
                config = result[0]
                return {
                    'success': True,
                    'data': {
                        'longitud_minima_password': config.get('longitud_minima_password', 8),
                        'requerir_mayusculas': config.get('requerir_mayusculas', True),
                        'requerir_minusculas': config.get('requerir_minusculas', True),
                        'requerir_numeros': config.get('requerir_numeros', True),
                        'requerir_simbolos': config.get('requerir_simbolos', False),
                        'expiracion_password_dias': config.get('expiracion_password_dias', 90),
                        'tiempo_sesion_minutos': config.get('tiempo_sesion_minutos', 480),
                        'intentos_login_maximo': config.get('intentos_login_maximo', 5),
                        'tiempo_bloqueo_minutos': config.get('tiempo_bloqueo_minutos', 30),
                        'habilitar_2fa': config.get('habilitar_2fa', False),
                        'audit_log_habilitado': config.get('audit_log_habilitado', True),
                        'retener_logs_dias': config.get('retener_logs_dias', 365)
                    }
                }
            else:
                # Devolver configuración por defecto
                return {
                    'success': True,
                    'data': {
                        'longitud_minima_password': 8,
                        'requerir_mayusculas': True,
                        'requerir_minusculas': True,
                        'requerir_numeros': True,
                        'requerir_simbolos': False,
                        'expiracion_password_dias': 90,
                        'tiempo_sesion_minutos': 480,
                        'intentos_login_maximo': 5,
                        'tiempo_bloqueo_minutos': 30,
                        'habilitar_2fa': False,
                        'audit_log_habilitado': True,
                        'retener_logs_dias': 365
                    }
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en get_configuracion_seguridad: {str(e)}")
            return {
                'success': False,
                'message': f'Error obteniendo configuración de seguridad: {str(e)}'
            }
    
    def update_configuracion_seguridad(self, data):
        """Actualizar configuración de seguridad"""
        try:
            # Verificar si existe el registro
            check_query = "SELECT COUNT(*) as count FROM configuracion_seguridad WHERE id = 1"
            check_result = self.db.getRecords(check_query)
            
            exists = check_result and len(check_result) > 0 and check_result[0].get('count', 0) > 0
            
            if exists:
                # Actualizar registro existente
                query = """
                    UPDATE configuracion_seguridad SET
                        longitud_minima_password = %s,
                        requerir_mayusculas = %s,
                        requerir_minusculas = %s,
                        requerir_numeros = %s,
                        requerir_simbolos = %s,
                        expiracion_password_dias = %s,
                        tiempo_sesion_minutos = %s,
                        intentos_login_maximo = %s,
                        tiempo_bloqueo_minutos = %s,
                        habilitar_2fa = %s,
                        audit_log_habilitado = %s,
                        retener_logs_dias = %s,
                        fecha_modificacion = NOW()
                    WHERE id = 1
                """
            else:
                # Crear nuevo registro
                query = """
                    INSERT INTO configuracion_seguridad (
                        id, longitud_minima_password, requerir_mayusculas, requerir_minusculas,
                        requerir_numeros, requerir_simbolos, expiracion_password_dias,
                        tiempo_sesion_minutos, intentos_login_maximo, tiempo_bloqueo_minutos,
                        habilitar_2fa, audit_log_habilitado, retener_logs_dias,
                        fecha_creacion, fecha_modificacion
                    ) VALUES (
                        1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                """
            
            params = (
                data.get('longitud_minima_password'),
                data.get('requerir_mayusculas'),
                data.get('requerir_minusculas'),
                data.get('requerir_numeros'),
                data.get('requerir_simbolos'),
                data.get('expiracion_password_dias'),
                data.get('tiempo_sesion_minutos'),
                data.get('intentos_login_maximo'),
                data.get('tiempo_bloqueo_minutos'),
                data.get('habilitar_2fa'),
                data.get('audit_log_habilitado'),
                data.get('retener_logs_dias')
            )
            
            result = self.db.ExecuteNonQuery(query, params)
            
            if result:
                return {
                    'success': True,
                    'message': 'Configuración de seguridad actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando configuración de seguridad'
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en update_configuracion_seguridad: {str(e)}")
            return {
                'success': False,
                'message': f'Error actualizando configuración de seguridad: {str(e)}'
            }
    
    # ============================================
    # MÉTODOS AUXILIARES
    # ============================================
    
    def crear_tablas_configuracion(self):
        """Crear tablas de configuración si no existen"""
        try:
            # Tabla configuración general
            query_general = """
                CREATE TABLE IF NOT EXISTS configuracion_general (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    nombre_centro VARCHAR(100) NOT NULL DEFAULT 'Centro Tía Glenda',
                    logo_url VARCHAR(255),
                    direccion TEXT,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    horario_inicio TIME DEFAULT '08:00:00',
                    horario_fin TIME DEFAULT '17:00:00',
                    zona_horaria VARCHAR(50) DEFAULT 'America/Guayaquil',
                    formato_fecha VARCHAR(20) DEFAULT 'DD/MM/YYYY',
                    formato_hora VARCHAR(10) DEFAULT '24h',
                    moneda VARCHAR(5) DEFAULT 'USD',
                    idioma VARCHAR(5) DEFAULT 'es',
                    descripcion TEXT,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    fecha_modificacion TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT chk_single_config_general CHECK (id = 1)
                )
            """
            
            # Tabla configuración de sesiones
            query_sesiones = """
                CREATE TABLE IF NOT EXISTS configuracion_sesiones (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    duracion_sesion_terapia INTEGER DEFAULT 60,
                    duracion_clase_pedagogica INTEGER DEFAULT 45,
                    tolerancia_llegada_tarde INTEGER DEFAULT 15,
                    tiempo_recordatorio INTEGER DEFAULT 15,
                    permitir_cancelacion_horas INTEGER DEFAULT 24,
                    permitir_reprogramacion_horas INTEGER DEFAULT 24,
                    capacidad_maxima_clase INTEGER DEFAULT 12,
                    sistema_calificaciones VARCHAR(20) DEFAULT 'numerico',
                    escala_calificacion_min INTEGER DEFAULT 1,
                    escala_calificacion_max INTEGER DEFAULT 10,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    fecha_modificacion TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT chk_single_config_sesiones CHECK (id = 1)
                )
            """
            
            # Tabla configuración de notificaciones global
            query_notif_global = """
                CREATE TABLE IF NOT EXISTS configuracion_notificaciones_global (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    notificaciones_habilitadas BOOLEAN DEFAULT TRUE,
                    notificaciones_sesion_terapia BOOLEAN DEFAULT TRUE,
                    notificaciones_clase_pedagogica BOOLEAN DEFAULT TRUE,
                    notificaciones_cancelaciones BOOLEAN DEFAULT TRUE,
                    notificaciones_reprogramaciones BOOLEAN DEFAULT TRUE,
                    tiempo_anticipacion_minutos INTEGER DEFAULT 15,
                    sonido_habilitado BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    fecha_modificacion TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT chk_single_config_notif_global CHECK (id = 1)
                )
            """
            
            # Tabla configuración de notificaciones por usuario
            query_notif_usuario = """
                CREATE TABLE IF NOT EXISTS configuracion_notificaciones_usuario (
                    user_id INTEGER PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
                    notificaciones_habilitadas BOOLEAN DEFAULT TRUE,
                    notificaciones_sesion_terapia BOOLEAN DEFAULT TRUE,
                    notificaciones_clase_pedagogica BOOLEAN DEFAULT TRUE,
                    notificaciones_cancelaciones BOOLEAN DEFAULT TRUE,
                    notificaciones_reprogramaciones BOOLEAN DEFAULT TRUE,
                    tiempo_anticipacion_minutos INTEGER DEFAULT 15,
                    sonido_habilitado BOOLEAN DEFAULT TRUE,
                    modo_silencioso_inicio TIME,
                    modo_silencioso_fin TIME,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    fecha_modificacion TIMESTAMP DEFAULT NOW()
                )
            """
            
            # Tabla configuración de seguridad
            query_seguridad = """
                CREATE TABLE IF NOT EXISTS configuracion_seguridad (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    longitud_minima_password INTEGER DEFAULT 8,
                    requerir_mayusculas BOOLEAN DEFAULT TRUE,
                    requerir_minusculas BOOLEAN DEFAULT TRUE,
                    requerir_numeros BOOLEAN DEFAULT TRUE,
                    requerir_simbolos BOOLEAN DEFAULT FALSE,
                    expiracion_password_dias INTEGER DEFAULT 90,
                    tiempo_sesion_minutos INTEGER DEFAULT 480,
                    intentos_login_maximo INTEGER DEFAULT 5,
                    tiempo_bloqueo_minutos INTEGER DEFAULT 30,
                    habilitar_2fa BOOLEAN DEFAULT FALSE,
                    audit_log_habilitado BOOLEAN DEFAULT TRUE,
                    retener_logs_dias INTEGER DEFAULT 365,
                    fecha_creacion TIMESTAMP DEFAULT NOW(),
                    fecha_modificacion TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT chk_single_config_seguridad CHECK (id = 1)
                )
            """
            
            # Ejecutar consultas
            queries = [query_general, query_sesiones, query_notif_global, query_notif_usuario, query_seguridad]
            
            for query in queries:
                result = self.db.ExecuteNonQuery(query)
                if not result:
                    HandleLogs.write_error(f"Error creando tabla de configuración: {query[:50]}...")
                    return False
            
            HandleLogs.write_log("Tablas de configuración creadas exitosamente")
            return True
            
        except Exception as e:
            HandleLogs.write_error(f"Error en crear_tablas_configuracion: {str(e)}")
            return False