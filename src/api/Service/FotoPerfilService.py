"""
FotoPerfilService.py
Logica de negocio para fotos de perfil
Centro Tia Glenda - Sistema de Gestion de Fotos de Perfil
"""

from src.api.Components.FotoPerfilComponent import FotoPerfilComponent
from src.utils.general.logs import HandleLogs
import os


class FotoPerfilService:

    @staticmethod
    def subir_foto_perfil(archivo, usuario_autenticado):
        """Procesar subida de foto de perfil del usuario autenticado"""
        try:
            resultado = FotoPerfilComponent.subir_foto_perfil(
                usuario_autenticado['id'],
                archivo,
                usuario_autenticado['id']
            )

            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en subir_foto_perfil: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def subir_foto_perfil_admin(archivo, usuario_id, usuario_admin):
        """Subir foto de perfil por administrador"""
        try:
            # Solo administradores pueden cambiar fotos de otros usuarios
            if usuario_admin.get('rol', '').lower() != 'administrador':
                return {'success': False, 'message': 'Solo administradores pueden realizar esta accion'}

            # Validar que el usuario objetivo existe y esta en el mismo centro
            if not FotoPerfilService._validar_usuario_mismo_centro(usuario_id, usuario_admin.get('id_centro')):
                return {'success': False, 'message': 'Usuario no encontrado o no pertenece al mismo centro'}

            resultado = FotoPerfilComponent.subir_foto_perfil(
                usuario_id,
                archivo,
                usuario_admin['id']
            )

            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en subir_foto_perfil_admin: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def obtener_foto_perfil(usuario_id, usuario_autenticado):
        """Obtener informacion de foto de perfil"""
        try:
            resultado = FotoPerfilComponent.obtener_foto_perfil(usuario_id)
            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_foto_perfil: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def obtener_mi_foto_perfil(usuario_autenticado):
        """Obtener foto de perfil del usuario autenticado"""
        try:
            resultado = FotoPerfilComponent.obtener_foto_perfil(usuario_autenticado['id'])
            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_mi_foto_perfil: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def eliminar_foto_perfil(usuario_autenticado):
        """Eliminar foto de perfil del usuario autenticado"""
        try:
            resultado = FotoPerfilComponent.eliminar_foto_perfil(
                usuario_autenticado['id'],
                usuario_autenticado['id']
            )

            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_foto_perfil: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def eliminar_foto_perfil_admin(usuario_id, usuario_admin):
        """Eliminar foto de perfil por administrador"""
        try:
            # Solo administradores pueden eliminar fotos de otros usuarios
            if usuario_admin.get('rol', '').lower() != 'administrador':
                return {'success': False, 'message': 'Solo administradores pueden realizar esta accion'}

            # Validar que el usuario objetivo existe y esta en el mismo centro
            if not FotoPerfilService._validar_usuario_mismo_centro(usuario_id, usuario_admin.get('id_centro')):
                return {'success': False, 'message': 'Usuario no encontrado o no pertenece al mismo centro'}

            resultado = FotoPerfilComponent.eliminar_foto_perfil(
                usuario_id,
                usuario_admin['id']
            )

            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_foto_perfil_admin: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def obtener_archivo_foto(ruta_foto, usuario_autenticado):
        """Obtener archivo fisico de foto de perfil"""
        try:
            if not ruta_foto:
                return {'success': False, 'message': 'Ruta de foto no proporcionada'}

            # Resolver ruta completa
            ruta_completa = FotoPerfilComponent._get_ruta_completa(ruta_foto)

            # Validar que el archivo existe
            if not os.path.exists(ruta_completa):
                return {'success': False, 'message': 'Archivo de foto no encontrado'}

            # Proteccion contra path traversal: resolver ruta real y verificar
            # que esta dentro del directorio de fotos permitido
            ruta_real = os.path.realpath(ruta_completa)
            carpeta_fotos_real = os.path.realpath(
                FotoPerfilComponent._get_ruta_completa(FotoPerfilComponent.UPLOAD_FOLDER)
            )

            if not ruta_real.startswith(carpeta_fotos_real + os.sep) and ruta_real != carpeta_fotos_real:
                return {'success': False, 'message': 'Acceso a archivo no autorizado'}

            return {
                'success': True,
                'ruta_archivo': ruta_real,
                'message': 'Archivo encontrado'
            }

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_archivo_foto: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def obtener_estadisticas_fotos(usuario_admin):
        """Obtener estadisticas de fotos de perfil (solo admin)"""
        try:
            if usuario_admin.get('rol', '').lower() != 'administrador':
                return {'success': False, 'message': 'Solo administradores pueden ver estadisticas'}

            resultado = FotoPerfilComponent.obtener_estadisticas_fotos()
            return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_fotos: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def _validar_usuario_mismo_centro(usuario_id, centro_admin):
        """Validar que el usuario pertenece al mismo centro que el admin"""
        try:
            from src.utils.database.connection_db import DataBaseHandle

            db = DataBaseHandle()
            query = """
                SELECT COUNT(*) as existe
                FROM usuario
                WHERE id = %s AND id_centro = %s AND estado = 'activo'
            """

            resultado = db.getRecords(query, (usuario_id, centro_admin))

            if resultado and resultado[0]['existe'] > 0:
                return True

            return False

        except Exception as e:
            HandleLogs.write_error(f"Error en _validar_usuario_mismo_centro: {str(e)}")
            return False

    @staticmethod
    def obtener_formatos_soportados():
        """Obtener informacion sobre formatos soportados"""
        return {
            'success': True,
            'formatos': {
                'extensiones_permitidas': list(FotoPerfilComponent.ALLOWED_EXTENSIONS),
                'tamano_maximo_mb': FotoPerfilComponent.MAX_FILE_SIZE // (1024 * 1024),
                'tamano_maximo_bytes': FotoPerfilComponent.MAX_FILE_SIZE,
                'dimension_maxima': FotoPerfilComponent.MAX_IMAGE_SIZE,
                'tipos_mime_soportados': [
                    'image/jpeg',
                    'image/jpg',
                    'image/png',
                    'image/gif',
                    'image/webp'
                ]
            }
        }
