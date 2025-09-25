# src/utils/general/date_helpers.py

from datetime import datetime, date, time
import json
from typing import Any, Dict, List, Union


class DateHelpers:
    """
    Helper class para estandarizar el manejo de fechas y tiempos
    entre el backend y frontend, resolviendo los problemas de timezone
    documentados en CLAUDE.md

    PROBLEMA IDENTIFICADO:
    - Cronograma endpoints devuelven: "2025-08-06" (ISO format) ✅ SEGURO
    - Asistencias endpoints devuelven: "Wed, 06 Aug 2025 00:00:00 GMT" ❌ PROBLEMÁTICO
    """

    @staticmethod
    def serialize_date(date_obj: Union[date, datetime, None]) -> Union[str, None]:
        """
        Serializa un objeto date/datetime a formato ISO string consistente

        Args:
            date_obj: Objeto date, datetime o None

        Returns:
            String en formato YYYY-MM-DD o None
        """
        if date_obj is None:
            return None

        if isinstance(date_obj, datetime):
            return date_obj.date().isoformat()
        elif isinstance(date_obj, date):
            return date_obj.isoformat()
        else:
            return str(date_obj)

    @staticmethod
    def serialize_time(time_obj: Union[time, None]) -> Union[str, None]:
        """
        Serializa un objeto time a formato string consistente

        Args:
            time_obj: Objeto time o None

        Returns:
            String en formato HH:MM o None
        """
        if time_obj is None:
            return None

        if isinstance(time_obj, time):
            return time_obj.strftime('%H:%M')
        else:
            return str(time_obj)

    @staticmethod
    def serialize_datetime(datetime_obj: Union[datetime, None]) -> Union[str, None]:
        """
        Serializa un objeto datetime a formato ISO string consistente

        Args:
            datetime_obj: Objeto datetime o None

        Returns:
            String en formato YYYY-MM-DDTHH:MM:SS o None
        """
        if datetime_obj is None:
            return None

        if isinstance(datetime_obj, datetime):
            return datetime_obj.isoformat()
        else:
            return str(datetime_obj)

    @staticmethod
    def format_record_dates(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea todas las fechas y tiempos en un registro de base de datos
        para ser JSON serializable de manera consistente

        Args:
            record: Diccionario con datos del registro

        Returns:
            Diccionario con fechas formateadas
        """
        if not isinstance(record, dict):
            return record

        formatted_record = {}

        for key, value in record.items():
            if isinstance(value, date) and not isinstance(value, datetime):
                # CORRECCIÓN: Solo date objects van a formato YYYY-MM-DD
                formatted_record[key] = DateHelpers.serialize_date(value)
            elif isinstance(value, datetime):
                # CORRECCIÓN: datetime objects van a formato ISO completo
                formatted_record[key] = DateHelpers.serialize_datetime(value)
            elif isinstance(value, time):
                # time objects van a formato HH:MM
                formatted_record[key] = DateHelpers.serialize_time(value)
            else:
                formatted_record[key] = value

        return formatted_record

    @staticmethod
    def format_records_list(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formatea fechas en una lista de registros

        Args:
            records: Lista de diccionarios con registros

        Returns:
            Lista con fechas formateadas
        """
        if not isinstance(records, list):
            return records

        return [DateHelpers.format_record_dates(record) for record in records]

    @staticmethod
    def safe_json_serialize(data: Any) -> str:
        """
        Serializa datos a JSON manejando fechas de manera segura

        Args:
            data: Datos a serializar

        Returns:
            String JSON
        """
        def json_serializer(obj):
            if isinstance(obj, date) and not isinstance(obj, datetime):
                return DateHelpers.serialize_date(obj)
            elif isinstance(obj, datetime):
                return DateHelpers.serialize_datetime(obj)
            elif isinstance(obj, time):
                return DateHelpers.serialize_time(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(data, default=json_serializer, ensure_ascii=False)

    @staticmethod
    def parse_frontend_date(date_string: str) -> Union[date, None]:
        """
        Parsea una fecha que viene del frontend de manera segura

        Args:
            date_string: String de fecha del frontend

        Returns:
            Objeto date o None si no se puede parsear
        """
        if not date_string or date_string == 'null':
            return None

        try:
            # Formato esperado del frontend: YYYY-MM-DD
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            try:
                # Fallback: intentar con formato ISO completo
                return datetime.fromisoformat(date_string).date()
            except ValueError:
                return None

    @staticmethod
    def parse_frontend_time(time_string: str) -> Union[time, None]:
        """
        Parsea una hora que viene del frontend de manera segura

        Args:
            time_string: String de hora del frontend (HH:MM)

        Returns:
            Objeto time o None si no se puede parsear
        """
        if not time_string or time_string == 'null':
            return None

        try:
            return datetime.strptime(time_string, '%H:%M').time()
        except ValueError:
            return None

    @staticmethod
    def get_current_date_formatted() -> str:
        """
        Obtiene la fecha actual en formato consistente

        Returns:
            Fecha actual en formato YYYY-MM-DD
        """
        return date.today().isoformat()

    @staticmethod
    def get_current_datetime_formatted() -> str:
        """
        Obtiene fecha y hora actual en formato consistente

        Returns:
            DateTime actual en formato ISO
        """
        return datetime.now().isoformat()

    @staticmethod
    def validate_date_range(fecha_inicio: Union[str, date], fecha_fin: Union[str, date]) -> Dict[str, Any]:
        """
        Valida que un rango de fechas sea consistente

        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin

        Returns:
            Dict con resultado de validación
        """
        try:
            # Convertir strings a dates si es necesario
            if isinstance(fecha_inicio, str):
                fecha_inicio = DateHelpers.parse_frontend_date(fecha_inicio)
            if isinstance(fecha_fin, str):
                fecha_fin = DateHelpers.parse_frontend_date(fecha_fin)

            if not fecha_inicio or not fecha_fin:
                return {
                    'valid': False,
                    'error': 'Fechas de inicio y fin son requeridas'
                }

            if fecha_fin <= fecha_inicio:
                return {
                    'valid': False,
                    'error': 'Fecha de fin debe ser posterior a fecha de inicio'
                }

            # Validar que no sea un rango muy largo (más de 2 años)
            days_diff = (fecha_fin - fecha_inicio).days
            if days_diff > 730:  # 2 años aprox
                return {
                    'valid': False,
                    'error': 'El rango de fechas no puede ser mayor a 2 años'
                }

            return {
                'valid': True,
                'days_difference': days_diff
            }

        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validando fechas: {str(e)}'
            }


# Funciones de conveniencia para importación directa
def format_date_for_json(date_obj):
    """Función de conveniencia para formatear fechas para JSON"""
    return DateHelpers.serialize_date(date_obj)

def format_time_for_json(time_obj):
    """Función de conveniencia para formatear tiempo para JSON"""
    return DateHelpers.serialize_time(time_obj)

def format_datetime_for_json(datetime_obj):
    """Función de conveniencia para formatear datetime para JSON"""
    return DateHelpers.serialize_datetime(datetime_obj)

def safe_format_record(record):
    """Función de conveniencia para formatear un registro"""
    return DateHelpers.format_record_dates(record)