# src/utils/general/utf8_helper.py

import json
import unicodedata
from flask import request
from src.utils.general.logs import HandleLogs

class UTF8Helper:
    """Helper para manejo robusto de UTF-8 en sesiones terapia"""
    
    @staticmethod
    def normalize_text(text):
        """Normalizar texto para evitar problemas de encoding"""
        if not text:
            return text
        
        try:
            # Convertir a string si no lo es
            if not isinstance(text, str):
                text = str(text)
            
            # Normalizar caracteres Unicode (NFD -> NFC)
            text = unicodedata.normalize('NFC', text)
            
            # Limpiar caracteres problemáticos pero mantener acentos básicos
            # Solo remover caracteres de control
            cleaned = ''.join(char for char in text if unicodedata.category(char) != 'Cc')
            
            return cleaned
            
        except Exception as e:
            HandleLogs.write_error(f"UTF8Helper.normalize_text - Error normalizing text: {str(e)}")
            # Fallback: remover solo caracteres problemáticos conocidos
            try:
                return text.encode('utf-8', errors='ignore').decode('utf-8')
            except:
                return str(text)
    
    @staticmethod
    def safe_get_json(flask_request=None):
        """Obtener JSON de request de forma segura para UTF-8"""
        if flask_request is None:
            flask_request = request
            
        try:
            # Intentar obtener JSON normalmente
            data = flask_request.get_json(force=True)
            if data is None:
                return None, "No se pudieron procesar los datos JSON"
            
            # Normalizar todos los campos de texto
            normalized_data = UTF8Helper._normalize_json_data(data)
            return normalized_data, None
            
        except UnicodeDecodeError as e:
            HandleLogs.write_error(f"UTF8Helper.safe_get_json - UTF-8 decode error: {str(e)}")
            
            # Intentar con fallback de encoding
            try:
                raw_data = flask_request.get_data()
                if raw_data:
                    # Intentar decodificar con diferentes encodings
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            text = raw_data.decode(encoding)
                            data = json.loads(text)
                            normalized_data = UTF8Helper._normalize_json_data(data)
                            HandleLogs.write_log(f"UTF8Helper.safe_get_json - Recovered with encoding: {encoding}")
                            return normalized_data, None
                        except:
                            continue
                            
                return None, "Error de codificación en los datos enviados. Verifica que no haya caracteres especiales problemáticos"
                
            except Exception as fallback_e:
                HandleLogs.write_error(f"UTF8Helper.safe_get_json - Fallback error: {str(fallback_e)}")
                return None, "Error crítico de codificación en los datos"
                
        except Exception as e:
            HandleLogs.write_error(f"UTF8Helper.safe_get_json - JSON parse error: {str(e)}")
            return None, "Error al procesar los datos JSON"
    
    @staticmethod
    def _normalize_json_data(data):
        """Normalizar recursivamente los datos JSON"""
        if isinstance(data, dict):
            return {key: UTF8Helper._normalize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [UTF8Helper._normalize_json_data(item) for item in data]
        elif isinstance(data, str):
            return UTF8Helper.normalize_text(data)
        else:
            return data
    
    @staticmethod
    def safe_database_string(text, max_length=None):
        """Preparar string de forma segura para la base de datos"""
        if not text:
            return text
            
        try:
            # Normalizar texto
            normalized = UTF8Helper.normalize_text(text)
            
            # Truncar si hay límite de longitud
            if max_length and len(normalized) > max_length:
                normalized = normalized[:max_length].strip()
                
            return normalized
            
        except Exception as e:
            HandleLogs.write_error(f"UTF8Helper.safe_database_string - Error: {str(e)}")
            return str(text)[:max_length] if max_length else str(text)
    
    @staticmethod
    def clean_observaciones(observaciones):
        """Limpiar específicamente el campo de observaciones"""
        if not observaciones:
            return ""
            
        # Límite razonable para observaciones
        cleaned = UTF8Helper.safe_database_string(observaciones, max_length=2000)
        
        # Remover saltos de línea problemáticos pero mantener formato básico
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        # Limitar saltos de línea consecutivos
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
            
        return cleaned.strip()