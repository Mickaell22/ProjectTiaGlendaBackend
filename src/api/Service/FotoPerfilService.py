"""
FotoPerfilService.py
Lógica de negocio para fotos de perfil
Centro Tía Glenda - Sistema de Gestión de Fotos de Perfil
"""

from src.api.Components.FotoPerfilComponent import FotoPerfilComponent
from src.utils.general.logs import HandleLogs
import os


class FotoPerfilService:
    
    @staticmethod
    def subir_foto_perfil(archivo, usuario_autenticado):
        """
        Procesar subida de foto de perfil
        """
        try:
            # Validar permisos (usuarios solo pueden cambiar su propia foto, excepto admin)
            if not FotoPerfilService._validar_permisos_foto(usuario_autenticado, usuario_autenticado['id']):
                return {'success': False, 'message': 'No tienes permisos para cambiar esta foto de perfil'}
            
            # Subir foto
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
        """
        Subir foto de perfil por administrador
        """
        try:
            # Solo administradores pueden cambiar fotos de otros usuarios
            if usuario_admin.get('rol', '').lower() != 'administrador':
                return {'success': False, 'message': 'Solo administradores pueden realizar esta acción'}
            
            # Validar que el usuario objetivo existe y está en el mismo centro
            if not FotoPerfilService._validar_usuario_mismo_centro(usuario_id, usuario_admin['id_centro']):
                return {'success': False, 'message': 'Usuario no encontrado o no pertenece al mismo centro'}
            
            # Subir foto
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
        """
        Obtener información de foto de perfil
        """
        try:
            # Validar permisos
            if not FotoPerfilService._validar_permisos_ver_foto(usuario_autenticado, usuario_id):
                return {'success': False, 'message': 'No tienes permisos para ver esta foto de perfil'}
            
            resultado = FotoPerfilComponent.obtener_foto_perfil(usuario_id)
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_foto_perfil: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_mi_foto_perfil(usuario_autenticado):
        """
        Obtener foto de perfil del usuario autenticado
        """
        try:
            resultado = FotoPerfilComponent.obtener_foto_perfil(usuario_autenticado['id'])
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_mi_foto_perfil: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def eliminar_foto_perfil(usuario_autenticado):
        """
        Eliminar foto de perfil del usuario autenticado
        """
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
        """
        Eliminar foto de perfil por administrador
        """
        try:
            # Solo administradores pueden eliminar fotos de otros usuarios
            if usuario_admin.get('rol', '').lower() != 'administrador':
                return {'success': False, 'message': 'Solo administradores pueden realizar esta acción'}
            
            # Validar que el usuario objetivo existe y está en el mismo centro
            if not FotoPerfilService._validar_usuario_mismo_centro(usuario_id, usuario_admin['id_centro']):
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
        """
        Obtener archivo físico de foto de perfil
        """
        try:
            # Validar que la ruta existe
            if not ruta_foto:
                return {'success': False, 'message': 'Ruta de foto no proporcionada'}
            
            ruta_completa = os.path.join(os.getcwd(), ruta_foto)
            
            # Validar que el archivo existe
            if not os.path.exists(ruta_completa):
                return {'success': False, 'message': 'Archivo de foto no encontrado'}
            
            # Validar que la ruta está dentro del directorio permitido
            # Normalizar separadores de ruta para compatibilidad Windows/Linux
            ruta_normalizada = ruta_foto.replace('\\', '/')
            if not ruta_normalizada.startswith('fotos_perfil/'):
                return {'success': False, 'message': 'Acceso a archivo no autorizado'}
            
            # TODO: Implementar validación de que el usuario tiene permisos para ver esta foto específica
            # Esto requeriría una consulta adicional para verificar ownership
            
            return {
                'success': True,
                'ruta_archivo': ruta_completa,
                'mensaje': 'Archivo encontrado'
            }
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_archivo_foto: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_estadisticas_fotos(usuario_admin):
        """
        Obtener estadísticas de fotos de perfil (solo admin)
        """
        try:
            # Solo administradores pueden ver estadísticas
            if usuario_admin.get('rol', '').lower() != 'administrador':
                return {'success': False, 'message': 'Solo administradores pueden ver estadísticas'}
            
            resultado = FotoPerfilComponent.obtener_estadisticas_fotos()
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_fotos: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def _validar_permisos_foto(usuario_autenticado, usuario_objetivo_id):
        """
        Validar permisos para modificar foto de perfil
        """
        # Administradores pueden cambiar cualquier foto
        if usuario_autenticado.get('rol') == 'administrador':
            return True
        
        # Usuarios solo pueden cambiar su propia foto
        return usuario_autenticado['id'] == usuario_objetivo_id
    
    @staticmethod
    def _validar_permisos_ver_foto(usuario_autenticado, usuario_objetivo_id):
        """
        Validar permisos para ver foto de perfil
        """
        # Todos los usuarios autenticados del mismo centro pueden ver fotos de perfil
        # (esto es típico en sistemas internos de empresas)
        
        # TODO: Implementar validación de centro si es necesario
        # Por ahora, todos los usuarios autenticados pueden ver fotos
        
        return True
    
    @staticmethod
    def _validar_usuario_mismo_centro(usuario_id, centro_admin):
        """
        Validar que el usuario pertenece al mismo centro que el admin
        """
        try:
            from src.utils.database.database import DataBaseHandle
            
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
        """
        Obtener información sobre formatos soportados
        """
        return {
            'success': True,
            'formatos': {
                'extensiones_permitidas': list(FotoPerfilComponent.ALLOWED_EXTENSIONS),
                'tamaño_maximo_mb': FotoPerfilComponent.MAX_FILE_SIZE // (1024 * 1024),
                'tamaño_maximo_bytes': FotoPerfilComponent.MAX_FILE_SIZE,
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