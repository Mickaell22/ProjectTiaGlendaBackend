"""
FotoPerfilComponent.py
Manejo de operaciones de base de datos para fotos de perfil
Centro Tia Glenda - Sistema de Gestion de Fotos de Perfil
"""

from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
import os
from PIL import Image
import uuid


class FotoPerfilComponent:

    # En Railway: STORAGE_BASE_PATH = /data/documentos (mount del volume)
    STORAGE_BASE_PATH = os.environ.get('STORAGE_BASE_PATH', '')
    UPLOAD_FOLDER = os.path.join(STORAGE_BASE_PATH, 'fotos_perfil') if STORAGE_BASE_PATH else 'fotos_perfil'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE = (800, 800)

    @staticmethod
    def _get_ruta_completa(ruta_relativa):
        """Resolver ruta completa del archivo en disco"""
        if os.path.isabs(ruta_relativa):
            return ruta_relativa
        return os.path.join(os.getcwd(), ruta_relativa)

    @staticmethod
    def subir_foto_perfil(usuario_id, archivo, usuario_modificacion=None):
        """Subir y procesar foto de perfil"""
        try:
            # Validar archivo
            validacion = FotoPerfilComponent._validar_archivo(archivo)
            if not validacion['success']:
                return validacion

            # Crear directorio si no existe
            ruta_upload = FotoPerfilComponent._get_ruta_completa(FotoPerfilComponent.UPLOAD_FOLDER)
            os.makedirs(ruta_upload, exist_ok=True)

            # PASO 1: Obtener foto anterior para eliminarla despues
            db = DataBaseHandle()
            query_foto_anterior = """
                SELECT foto_perfil FROM usuario WHERE id = %s
            """
            foto_anterior_result = db.getRecords(query_foto_anterior, (usuario_id,))
            foto_anterior = None
            if foto_anterior_result and foto_anterior_result[0]['foto_perfil']:
                foto_anterior = foto_anterior_result[0]['foto_perfil']
                HandleLogs.write_log(f"Foto anterior encontrada para usuario {usuario_id}: {foto_anterior}")

            # PASO 2: Generar nombre unico - siempre .jpg porque se convierte a JPEG
            nombre_archivo = f"perfil_{usuario_id}_{uuid.uuid4().hex[:8]}.jpg"
            ruta_relativa = os.path.join(FotoPerfilComponent.UPLOAD_FOLDER, nombre_archivo)
            ruta_completa = FotoPerfilComponent._get_ruta_completa(ruta_relativa)

            # Crear directorio padre si no existe
            os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)

            # PASO 3: Procesar y guardar imagen nueva
            resultado_procesado = FotoPerfilComponent._procesar_imagen(archivo, ruta_completa)
            if not resultado_procesado['success']:
                return resultado_procesado

            # PASO 4: Actualizar base de datos con la nueva foto
            try:
                db = DataBaseHandle()
                update_query = """
                    UPDATE usuario
                    SET foto_perfil = %s,
                        usuario_modificacion = %s,
                        fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """

                # Normalizar separadores para consistencia en BD
                ruta_bd = ruta_relativa.replace('\\', '/')
                success = db.ExecuteNonQuery(update_query, (ruta_bd, usuario_modificacion, usuario_id))

                if success:
                    # PASO 5: Eliminar foto anterior solo SI la actualizacion fue exitosa
                    if foto_anterior:
                        ruta_foto_anterior = FotoPerfilComponent._get_ruta_completa(foto_anterior)
                        if os.path.exists(ruta_foto_anterior):
                            try:
                                os.remove(ruta_foto_anterior)
                                HandleLogs.write_log(f"Foto anterior eliminada: {ruta_foto_anterior}")
                            except Exception as e:
                                HandleLogs.write_error(f"Error eliminando foto anterior {ruta_foto_anterior}: {str(e)}")

                    return {
                        'success': True,
                        'ruta_foto': ruta_bd,
                        'message': 'Foto de perfil actualizada exitosamente'
                    }
                else:
                    # Si falla la actualizacion de BD, eliminar archivo nuevo
                    if os.path.exists(ruta_completa):
                        os.remove(ruta_completa)
                    return {
                        'success': False,
                        'message': 'Error actualizando base de datos'
                    }
            except Exception as db_error:
                # Si falla la actualizacion de BD, eliminar archivo nuevo
                if os.path.exists(ruta_completa):
                    os.remove(ruta_completa)
                HandleLogs.write_error(f"Error actualizando foto en BD: {str(db_error)}")
                return {
                    'success': False,
                    'message': f'Error de base de datos: {str(db_error)}'
                }

        except Exception as e:
            HandleLogs.write_error(f"Error en subir_foto_perfil: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def obtener_foto_perfil(usuario_id):
        """Obtener informacion de la foto de perfil del usuario"""
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

                # Verificar si el archivo existe fisicamente
                if foto_info['foto_perfil']:
                    ruta_completa = FotoPerfilComponent._get_ruta_completa(foto_info['foto_perfil'])
                    foto_info['archivo_existe'] = os.path.exists(ruta_completa)

                    if foto_info['archivo_existe']:
                        stat_info = os.stat(ruta_completa)
                        foto_info['tamano_archivo'] = stat_info.st_size
                    else:
                        foto_info['tamano_archivo'] = 0
                else:
                    foto_info['archivo_existe'] = False
                    foto_info['tamano_archivo'] = 0

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
            HandleLogs.write_error(f"Error en obtener_foto_perfil: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def eliminar_foto_perfil(usuario_id, usuario_modificacion=None):
        """Eliminar foto de perfil del usuario"""
        try:
            # Primero obtener la ruta actual de la foto
            foto_actual = FotoPerfilComponent.obtener_foto_perfil(usuario_id)
            if not foto_actual['success']:
                return foto_actual

            ruta_archivo = foto_actual['foto_perfil'].get('foto_perfil')

            # Eliminar foto de la base de datos
            try:
                db = DataBaseHandle()
                update_query = """
                    UPDATE usuario
                    SET foto_perfil = NULL,
                        usuario_modificacion = %s,
                        fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """

                success = db.ExecuteNonQuery(update_query, (usuario_modificacion, usuario_id))

                if not success:
                    return {
                        'success': False,
                        'message': 'Error actualizando base de datos'
                    }

                # Si la actualizacion de BD fue exitosa, eliminar archivo fisico
                if ruta_archivo:
                    ruta_completa = FotoPerfilComponent._get_ruta_completa(ruta_archivo)
                    if os.path.exists(ruta_completa):
                        try:
                            os.remove(ruta_completa)
                        except Exception as e:
                            HandleLogs.write_error(f"Error eliminando archivo fisico: {str(e)}")

            except Exception as db_error:
                HandleLogs.write_error(f"Error eliminando foto en BD: {str(db_error)}")
                return {
                    'success': False,
                    'message': f'Error de base de datos: {str(db_error)}'
                }

            return {
                'success': True,
                'message': 'Foto de perfil eliminada exitosamente'
            }

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_foto_perfil: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def validar_tipo_imagen_db(tipo_mime):
        """Validar tipo de imagen"""
        tipos_validos = [
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/gif',
            'image/webp'
        ]
        return tipo_mime.lower() in tipos_validos

    @staticmethod
    def _validar_archivo(archivo):
        """Validar archivo de imagen"""
        if not archivo:
            return {'success': False, 'message': 'No se proporciono archivo'}

        if archivo.filename == '':
            return {'success': False, 'message': 'No se selecciono archivo'}

        # Validar extension
        if not archivo.filename or '.' not in archivo.filename:
            return {'success': False, 'message': 'Archivo sin extension valida'}

        extension = archivo.filename.rsplit('.', 1)[1].lower()
        if extension not in FotoPerfilComponent.ALLOWED_EXTENSIONS:
            return {'success': False, 'message': f'Extension no permitida. Permitidas: {", ".join(FotoPerfilComponent.ALLOWED_EXTENSIONS)}'}

        # Validar tamano
        archivo.seek(0, os.SEEK_END)
        tamano = archivo.tell()
        archivo.seek(0)

        if tamano > FotoPerfilComponent.MAX_FILE_SIZE:
            return {'success': False, 'message': f'Archivo muy grande. Maximo: {FotoPerfilComponent.MAX_FILE_SIZE // (1024*1024)}MB'}

        # Validar tipo MIME si esta disponible
        if hasattr(archivo, 'content_type') and archivo.content_type:
            if not FotoPerfilComponent.validar_tipo_imagen_db(archivo.content_type):
                return {'success': False, 'message': 'Tipo de archivo no valido'}

        return {'success': True}

    @staticmethod
    def _procesar_imagen(archivo, ruta_destino):
        """Procesar imagen: redimensionar y optimizar. Siempre guarda como JPEG."""
        temp_path = ruta_destino + '.temp'
        try:
            archivo.save(temp_path)

            with Image.open(temp_path) as img:
                # Convertir a RGB si es necesario (JPEG no soporta alpha)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Redimensionar manteniendo proporcion
                img.thumbnail(FotoPerfilComponent.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)

                # Guardar imagen optimizada como JPEG
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

            HandleLogs.write_error(f"Error procesando imagen: {str(e)}")
            return {'success': False, 'message': f'Error procesando imagen: {str(e)}'}

    @staticmethod
    def obtener_estadisticas_fotos():
        """Obtener estadisticas de uso de fotos de perfil"""
        try:
            db = DataBaseHandle()

            query = """
                SELECT
                    COUNT(*) as total_usuarios,
                    COUNT(foto_perfil) as usuarios_con_foto,
                    COUNT(*) - COUNT(foto_perfil) as usuarios_sin_foto,
                    CASE
                        WHEN COUNT(*) > 0
                        THEN ROUND((COUNT(foto_perfil)::numeric / COUNT(*)) * 100, 1)
                        ELSE 0
                    END as porcentaje_con_foto
                FROM usuario
                WHERE estado = 'activo'
            """

            resultado = db.getRecords(query)

            if resultado:
                stats = dict(resultado[0])
                # Convertir Decimal a float para JSON
                if 'porcentaje_con_foto' in stats:
                    stats['porcentaje_con_foto'] = float(stats['porcentaje_con_foto'])
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
            HandleLogs.write_error(f"Error en obtener_estadisticas_fotos: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
