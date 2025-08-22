"""
FotoPerfilComponent.py
Manejo de operaciones de base de datos para fotos de perfil
Centro Tía Glenda - Sistema de Gestión de Fotos de Perfil
"""

from src.utils.database.database import DataBaseHandle
from src.utils.general.logger import Logger
import os
import shutil
from PIL import Image
import uuid

logger = Logger()

class FotoPerfilComponent:
    
    UPLOAD_FOLDER = 'fotos_perfil'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE = (800, 800)  # Tamaño máximo de imagen
    
    @staticmethod
    def subir_foto_perfil(usuario_id, archivo, usuario_modificacion=None):
        """
        Subir y procesar foto de perfil
        """
        try:
            # Validar archivo
            validacion = FotoPerfilComponent._validar_archivo(archivo)
            if not validacion['success']:
                return validacion
            
            # Crear directorio si no existe
            if not os.path.exists(FotoPerfilComponent.UPLOAD_FOLDER):
                os.makedirs(FotoPerfilComponent.UPLOAD_FOLDER)
            
            # Generar nombre único para el archivo
            db = DataBaseHandle()
            
            # Obtener extensión del archivo
            extension = archivo.filename.rsplit('.', 1)[1].lower()
            
            # Generar ruta usando función de base de datos
            query_ruta = "SELECT generar_ruta_foto_perfil(%s, %s)"
            resultado_ruta = db.getRecords(query_ruta, (usuario_id, extension))
            
            if not resultado_ruta:
                return {'success': False, 'message': 'Error al generar ruta de archivo'}
            
            ruta_relativa = resultado_ruta[0]['generar_ruta_foto_perfil']
            ruta_completa = os.path.join(os.getcwd(), ruta_relativa)
            
            # Crear directorio padre si no existe
            os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
            
            # Procesar y guardar imagen
            resultado_procesado = FotoPerfilComponent._procesar_imagen(archivo, ruta_completa)
            if not resultado_procesado['success']:
                return resultado_procesado
            
            # Actualizar base de datos
            query_update = "SELECT actualizar_foto_perfil(%s, %s, %s)"
            params_update = (usuario_id, ruta_relativa, usuario_modificacion or usuario_id)
            resultado_update = db.getRecords(query_update, params_update)
            
            if resultado_update and resultado_update[0]['actualizar_foto_perfil']:
                return {
                    'success': True,
                    'ruta_foto': ruta_relativa,
                    'mensaje': 'Foto de perfil actualizada exitosamente'
                }
            else:
                # Si falla la actualización, eliminar archivo guardado
                if os.path.exists(ruta_completa):
                    os.remove(ruta_completa)
                return {'success': False, 'message': 'Error al actualizar foto en base de datos'}
                
        except Exception as e:
            logger.log_error(f"Error en subir_foto_perfil: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_foto_perfil(usuario_id):
        """
        Obtener información de la foto de perfil del usuario
        """
        try:
            db = DataBaseHandle()
            
            query = """
                SELECT 
                    u.foto_perfil,
                    u.fecha_modificacion,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo
                FROM usuario u
                JOIN persona p ON u.id_persona = p.id
                WHERE u.id = %s
            """
            
            resultado = db.getRecords(query, (usuario_id,))
            
            if resultado:
                foto_info = dict(resultado[0])
                
                # Verificar si el archivo existe físicamente
                if foto_info['foto_perfil']:
                    ruta_completa = os.path.join(os.getcwd(), foto_info['foto_perfil'])
                    foto_info['archivo_existe'] = os.path.exists(ruta_completa)
                    
                    if foto_info['archivo_existe']:
                        # Obtener información adicional del archivo
                        stat_info = os.stat(ruta_completa)
                        foto_info['tamaño_archivo'] = stat_info.st_size
                    else:
                        foto_info['tamaño_archivo'] = 0
                else:
                    foto_info['archivo_existe'] = False
                    foto_info['tamaño_archivo'] = 0
                
                # Convertir fecha a string
                if 'fecha_modificacion' in foto_info and foto_info['fecha_modificacion']:
                    foto_info['fecha_modificacion'] = foto_info['fecha_modificacion'].isoformat()
                
                return {
                    'success': True,
                    'foto_perfil': foto_info
                }
            else:
                return {'success': False, 'message': 'Usuario no encontrado'}
                
        except Exception as e:
            logger.log_error(f"Error en obtener_foto_perfil: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def eliminar_foto_perfil(usuario_id, usuario_modificacion=None):
        """
        Eliminar foto de perfil del usuario
        """
        try:
            # Primero obtener la ruta actual de la foto
            foto_actual = FotoPerfilComponent.obtener_foto_perfil(usuario_id)
            if not foto_actual['success']:
                return foto_actual
            
            ruta_archivo = foto_actual['foto_perfil'].get('foto_perfil')
            
            # Eliminar registro en base de datos
            db = DataBaseHandle()
            query = "SELECT eliminar_foto_perfil(%s, %s)"
            params = (usuario_id, usuario_modificacion or usuario_id)
            resultado = db.getRecords(query, params)
            
            if resultado and resultado[0]['eliminar_foto_perfil']:
                # Eliminar archivo físico si existe
                if ruta_archivo:
                    ruta_completa = os.path.join(os.getcwd(), ruta_archivo)
                    if os.path.exists(ruta_completa):
                        try:
                            os.remove(ruta_completa)
                        except Exception as e:
                            logger.log_error(f"Error eliminando archivo físico: {str(e)}")
                
                return {
                    'success': True,
                    'message': 'Foto de perfil eliminada exitosamente'
                }
            else:
                return {'success': False, 'message': 'Error al eliminar foto de perfil'}
                
        except Exception as e:
            logger.log_error(f"Error en eliminar_foto_perfil: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def validar_tipo_imagen_db(tipo_mime):
        """
        Validar tipo de imagen usando función de base de datos
        """
        try:
            db = DataBaseHandle()
            query = "SELECT validar_tipo_imagen(%s)"
            resultado = db.getRecords(query, (tipo_mime,))
            
            if resultado:
                return resultado[0]['validar_tipo_imagen']
            return False
                
        except Exception as e:
            logger.log_error(f"Error en validar_tipo_imagen_db: {str(e)}")
            return False
    
    @staticmethod
    def _validar_archivo(archivo):
        """
        Validar archivo de imagen
        """
        if not archivo:
            return {'success': False, 'message': 'No se proporcionó archivo'}
        
        if archivo.filename == '':
            return {'success': False, 'message': 'No se seleccionó archivo'}
        
        # Validar extensión
        if not archivo.filename or '.' not in archivo.filename:
            return {'success': False, 'message': 'Archivo sin extensión válida'}
        
        extension = archivo.filename.rsplit('.', 1)[1].lower()
        if extension not in FotoPerfilComponent.ALLOWED_EXTENSIONS:
            return {'success': False, 'message': f'Extensión no permitida. Permitidas: {", ".join(FotoPerfilComponent.ALLOWED_EXTENSIONS)}'}
        
        # Validar tamaño (aproximado)
        # Nota: En aplicaciones reales, se debería validar el tamaño real
        archivo.seek(0, os.SEEK_END)
        tamaño = archivo.tell()
        archivo.seek(0)
        
        if tamaño > FotoPerfilComponent.MAX_FILE_SIZE:
            return {'success': False, 'message': f'Archivo muy grande. Máximo: {FotoPerfilComponent.MAX_FILE_SIZE // (1024*1024)}MB'}
        
        # Validar tipo MIME si está disponible
        if hasattr(archivo, 'content_type'):
            if not FotoPerfilComponent.validar_tipo_imagen_db(archivo.content_type):
                return {'success': False, 'message': 'Tipo de archivo no válido'}
        
        return {'success': True}
    
    @staticmethod
    def _procesar_imagen(archivo, ruta_destino):
        """
        Procesar imagen: redimensionar y optimizar
        """
        try:
            # Guardar archivo temporal
            temp_path = ruta_destino + '.temp'
            archivo.save(temp_path)
            
            # Abrir y procesar imagen con Pillow
            with Image.open(temp_path) as img:
                # Convertir a RGB si es necesario
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar manteniendo proporción
                img.thumbnail(FotoPerfilComponent.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                
                # Guardar imagen optimizada
                img.save(ruta_destino, 'JPEG', quality=85, optimize=True)
            
            # Eliminar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {'success': True, 'message': 'Imagen procesada exitosamente'}
            
        except Exception as e:
            # Limpiar archivos temporales en caso de error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(ruta_destino):
                os.remove(ruta_destino)
            
            logger.log_error(f"Error procesando imagen: {str(e)}")
            return {'success': False, 'message': f'Error procesando imagen: {str(e)}'}
    
    @staticmethod
    def obtener_estadisticas_fotos():
        """
        Obtener estadísticas de uso de fotos de perfil
        """
        try:
            db = DataBaseHandle()
            
            query = """
                SELECT 
                    COUNT(*) as total_usuarios,
                    COUNT(foto_perfil) as usuarios_con_foto,
                    COUNT(*) - COUNT(foto_perfil) as usuarios_sin_foto,
                    ROUND(
                        (COUNT(foto_perfil)::FLOAT / COUNT(*)::FLOAT) * 100, 2
                    ) as porcentaje_con_foto
                FROM usuario
                WHERE estado = 'activo'
            """
            
            resultado = db.getRecords(query)
            
            if resultado:
                stats = dict(resultado[0])
                return {
                    'success': True,
                    'estadisticas': stats
                }
            else:
                return {
                    'success': True,
                    'estadisticas': {
                        'total_usuarios': 0,
                        'usuarios_con_foto': 0,
                        'usuarios_sin_foto': 0,
                        'porcentaje_con_foto': 0
                    }
                }
                
        except Exception as e:
            logger.log_error(f"Error en obtener_estadisticas_fotos: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}