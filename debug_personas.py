#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from src.api.Service.PersonaService import PersonaService
from src.utils.general.logs import HandleLogs
import json

def test_personas():
    """Probar el servicio de personas directamente"""
    print("=== Probando PersonaService.get_personas() ===")
    
    try:
        # Simular request sin usuario actual (como si fuera admin)
        import flask
        from unittest.mock import Mock
        
        # Mock request global
        mock_request = Mock()
        mock_request.current_user = {'id_centro': None}  # Admin sin centro específico
        
        # Llamar al servicio
        result = PersonaService.get_personas()
        
        print(f"Status: {type(result)}")
        print(f"Response: {result}")
        
        # Si es un objeto Flask response, extraer datos
        if hasattr(result, 'get_json'):
            data = result.get_json()
            print(f"JSON Data: {json.dumps(data, indent=2, default=str)}")
        elif isinstance(result, tuple):
            print(f"Tuple response: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_personas()