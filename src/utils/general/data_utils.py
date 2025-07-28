"""
Utilidades para preparación y procesamiento de datos
Centraliza la lógica de procesamiento que estaba duplicada entre Service y Component layers
"""

class DataUtils:
    
    @staticmethod
    def prepare_observaciones(observaciones_input):
        """
        Preparar campo observaciones de forma estandarizada
        Args:
            observaciones_input: str o None - Input del usuario
        Returns:
            str o None - Observaciones procesadas (None si vacías)
        """
        if not observaciones_input:
            return None
        
        processed = observaciones_input.strip()
        return processed if processed else None
    
    @staticmethod
    def prepare_estado(estado_input, default='activo'):
        """
        Preparar campo estado con valor por defecto
        Args:
            estado_input: str o None - Estado del usuario
            default: str - Estado por defecto
        Returns:
            str - Estado final
        """
        return estado_input if estado_input else default
    
    @staticmethod
    def prepare_usuario_creacion(usuario_input, current_user_id=None):
        """
        Preparar campo usuario_creacion con fallback inteligente
        Args:
            usuario_input: int o None - Usuario del input
            current_user_id: int o None - ID del usuario actual de la sesión
        Returns:
            int - ID del usuario final (con fallback a 1 si es necesario)
        """
        if usuario_input:
            return usuario_input
        elif current_user_id:
            return current_user_id
        else:
            return 1  # Fallback para compatibilidad
    
    @staticmethod
    def prepare_create_data(data, current_user_id=None):
        """
        Preparar datos estándar para operaciones CREATE
        Args:
            data: dict - Datos de entrada
            current_user_id: int o None - ID del usuario actual
        Returns:
            dict - Datos procesados listos para Component
        """
        prepared = data.copy()
        
        # Procesar campos comunes
        if 'observaciones' in prepared:
            prepared['observaciones'] = DataUtils.prepare_observaciones(prepared.get('observaciones'))
        
        if 'estado' in prepared:
            prepared['estado'] = DataUtils.prepare_estado(prepared.get('estado'))
            
        if 'usuario_creacion' in prepared:
            prepared['usuario_creacion'] = DataUtils.prepare_usuario_creacion(
                prepared.get('usuario_creacion'), current_user_id
            )
        
        return prepared
    
    @staticmethod
    def prepare_update_data(data, current_user_id=None):
        """
        Preparar datos estándar para operaciones UPDATE
        Args:
            data: dict - Datos de entrada
            current_user_id: int o None - ID del usuario actual
        Returns:
            dict - Datos procesados listos para Component
        """
        prepared = data.copy()
        
        # Procesar campos comunes para updates
        if 'observaciones' in prepared:
            prepared['observaciones'] = DataUtils.prepare_observaciones(prepared.get('observaciones'))
            
        if 'usuario_modificacion' in prepared:
            prepared['usuario_modificacion'] = DataUtils.prepare_usuario_creacion(
                prepared.get('usuario_modificacion'), current_user_id
            )
        
        return prepared