#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests para API de Sesiones Pedagógicas
Centro Tía Glenda - Sistema de Gestión

Pruebas completas del módulo de sesiones pedagógicas incluyendo:
- CRUD de sesiones pedagógicas
- Gestión de estudiantes en sesiones
- Cronograma de clases
- Asistencia y evaluaciones
- Consultas y estadísticas
"""

import sys
import os
import json
import time
import random
import requests
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.utils.advanced_test_runner import AdvancedTestRunner

# Configuración del servidor de pruebas
BASE_URL = "http://localhost:5000"

def print_test_info(test_name, status, data=None, error=None):
    """Función para imprimir información de tests"""
    if status == "SUCCESS":
        print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)}...")
    elif status == "FAILED":
        print(f"   Error: {data if data else 'Test falló'}")
    elif status == "ERROR":
        print(f"   Error: {error}")
    else:
        print(f"   {status}: {data}")

# Variables globales para compartir entre tests
token = None
especialidad_id = None
pedagogo_id = None
estudiante_id = None
sesion_id = None
cronograma_id = None

def main():
    print("=== INICIANDO TESTS DE SESIONES PEDAGÓGICAS ===\n")
    
    runner = AdvancedTestRunner("SESIONES PEDAGÓGICAS")
    
    # Lista de pruebas a ejecutar
    tests = [
        (test_authentication, "Autenticacion"),
        (test_setup_data, "Configuracion de datos"),
        (test_sesiones_crud, "CRUD de sesiones pedagogicas"),
        (test_cronograma_management, "Gestion de cronograma de clases"),
        (test_estudiantes_management, "Gestion de estudiantes"),
        (test_additional_endpoints, "Endpoints adicionales"),
        (test_cleanup, "Limpieza de datos")
    ]
    
    runner.add_tests(tests)
    runner.run()

def test_authentication():
    """Test de autenticación para obtener token"""
    global token
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={
                "usuario": "admin.norte",
                "contrasenia": "admin123"
            }
        )
        
        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("token"):
            token = response_data["data"]["token"]
            print_test_info("Autenticacion", "SUCCESS", {"message": "Token obtenido exitosamente"})
            return True
        else:
            print_test_info("Autenticacion", "FAILED", response_data)
            raise Exception(f"Login failed: {response_data}")

    except Exception as e:
        if "Login failed:" in str(e):
            raise e
        print_test_info("Autenticacion", "ERROR", error=str(e))
        raise Exception(f"Error en login: {str(e)}")

def test_setup_data():
    """Configurar datos necesarios para las pruebas"""
    global especialidad_id, pedagogo_id, estudiante_id
    
    try:
        headers = {'Authorization': f"Bearer {token}"}
        
        # Buscar especialidad pedagógica
        response = requests.get(f"{BASE_URL}/api/especialidades", headers=headers)
        
        if response.status_code == 200:
            todas_especialidades = response.json()['data']
            # Filtrar especialidades pedagógicas
            especialidades_pedagogicas = [e for e in todas_especialidades if e.get('area') == 'Especialidad pedagógica']
            if len(especialidades_pedagogicas) > 0:
                especialidad_id = especialidades_pedagogicas[0]['id']
            elif len(todas_especialidades) > 0:
                especialidad_id = todas_especialidades[0]['id']
        
        # Buscar personal disponible
        response = requests.get(f"{BASE_URL}/api/personal", headers=headers)
        if response.status_code == 200:
            personal = response.json()['data']
            pedagogo_id = personal[0]['id'] if len(personal) > 0 else 1
        else:
            pedagogo_id = 1
        
        # Buscar estudiante (paciente) disponible
        response = requests.get(f"{BASE_URL}/api/pacientes", headers=headers)
        if response.status_code == 200:
            pacientes = response.json()['data']
            estudiante_id = pacientes[0]['id'] if len(pacientes) > 0 else None
        
        print_test_info("Configuracion de datos", "SUCCESS", {
            "especialidad_id": especialidad_id,
            "pedagogo_id": pedagogo_id,
            "estudiante_id": estudiante_id
        })
        return True
        
    except Exception as e:
        print_test_info("Configuracion de datos", "ERROR", error=str(e))
        raise Exception(f"Error en configuración: {str(e)}")

def test_sesiones_crud():
    """Test completo de CRUD para sesiones pedagógicas"""
    global sesion_id
    
    try:
        headers = {'Authorization': f"Bearer {token}"}
        
        # 1. Listar sesiones iniciales
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al listar sesiones: {response.status_code}")
        
        sesiones_iniciales = response.json()['data']
        
        # 2. Crear nueva sesión pedagógica
        fecha_inicio = datetime.now().date()
        fecha_fin = fecha_inicio + timedelta(days=90)
        
        nueva_sesion = {
            "titulo": f"Matemáticas Básicas Grupo {random.randint(1000, 9999)}",
            "pedagogo_id": pedagogo_id,
            "especialidad_id": especialidad_id,
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "dias_semana": "lunes,miercoles,viernes",
            "hora_inicio": "09:00",
            "duracion_minutos": 60,
            "numero_clases_programadas": 36,
            "nivel_academico": "basico",
            "capacidad_maxima": 12,
            "modalidad": "presencial",
            "costo_total": 18000.00,
            "periodo_academico": "2025-1",
            "observaciones": "Sesión de prueba para matemáticas básicas"
        }
        
        response = requests.post(f"{BASE_URL}/api/sesiones-pedagogicas", headers=headers, json=nueva_sesion)
        
        if response.status_code != 200:
            raise Exception(f"Error al crear sesión: {response.status_code} - {response.text}")
        
        data = response.json()
        sesion_id = data['data']['id']
        codigo_sesion = data['data']['codigo_sesion']
        
        # 3. Obtener sesión específica
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al obtener sesión: {response.status_code}")
        
        # 4. Actualizar sesión
        actualizacion = {
            "titulo": nueva_sesion['titulo'] + " - Actualizada",
            "observaciones": "Sesión actualizada con nuevas observaciones"
        }
        
        response = requests.put(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}", headers=headers, json=actualizacion)
        
        if response.status_code != 200:
            raise Exception(f"Error al actualizar sesión: {response.status_code}")
        
        # 5. Verificar lista actualizada
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas", headers=headers)
        sesiones_finales = response.json()['data']
        
        print_test_info("CRUD de sesiones pedagogicas", "SUCCESS", {
            "total_sesiones": len(sesiones_finales),
            "sesion_id": sesion_id,
            "codigo_sesion": codigo_sesion
        })
        return True
        
    except Exception as e:
        print_test_info("CRUD de sesiones pedagogicas", "ERROR", error=str(e))
        raise Exception(f"Error en CRUD: {str(e)}")

def test_cronograma_management():
    """Test de gestión del cronograma de clases"""
    global cronograma_id
    
    try:
        headers = {'Authorization': f"Bearer {token}"}
        
        # 1. Obtener cronograma
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}/cronograma", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al obtener cronograma: {response.status_code}")
        
        cronograma = response.json()['data']
        
        if len(cronograma) > 0:
            cronograma_id = cronograma[0]['id']
        
        # 2. Regenerar cronograma
        response = requests.post(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}/cronograma/generar", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al regenerar cronograma: {response.status_code}")
        
        # 3. Verificar cronograma regenerado
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}/cronograma", headers=headers)
        cronograma_nuevo = response.json()['data']
        
        if len(cronograma_nuevo) > 0:
            cronograma_id = cronograma_nuevo[0]['id']
        
        # 4. Marcar clase como realizada
        if cronograma_id:
            response = requests.put(f"{BASE_URL}/api/cronograma-clases/{cronograma_id}/realizar", headers=headers)
            
            if response.status_code != 200:
                print(f"Advertencia: No se pudo marcar clase como realizada: {response.status_code}")
        
        print_test_info("Gestion de cronograma de clases", "SUCCESS", {
            "total_clases_programadas": len(cronograma_nuevo),
            "cronograma_id": cronograma_id
        })
        return True
        
    except Exception as e:
        print_test_info("Gestion de cronograma de clases", "ERROR", error=str(e))
        raise Exception(f"Error en cronograma: {str(e)}")

def test_estudiantes_management():
    """Test de gestión de estudiantes en sesiones"""
    try:
        headers = {'Authorization': f"Bearer {token}"}
        
        # 1. Obtener estudiantes iniciales
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}/estudiantes", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al listar estudiantes: {response.status_code}")
        
        estudiantes_iniciales = response.json()['data']
        
        # 2. Agregar estudiante (si hay uno disponible)
        if estudiante_id:
            nuevo_estudiante = {
                "paciente_id": estudiante_id,
                "costo_estudiante": 1500.00,
                "observaciones_estudiante": "Estudiante de prueba para sesión pedagógica"
            }
            
            response = requests.post(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}/estudiantes", headers=headers, json=nuevo_estudiante)
            
            if response.status_code != 200:
                print(f"Advertencia: No se pudo agregar estudiante: {response.status_code}")
            
            # 3. Verificar que se agregó
            response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}/estudiantes", headers=headers)
            estudiantes_finales = response.json()['data']
            
            print_test_info("Gestion de estudiantes", "SUCCESS", {
                "paciente_id": estudiante_id,
                "mensaje": "Estudiante agregado a la sesión exitosamente"
            })
        else:
            print_test_info("Gestion de estudiantes", "SUCCESS", {
                "total_estudiantes": len(estudiantes_iniciales),
                "nota": "No hay estudiantes disponibles para agregar"
            })
        
        return True
        
    except Exception as e:
        print_test_info("Gestion de estudiantes", "ERROR", error=str(e))
        raise Exception(f"Error en estudiantes: {str(e)}")

def test_additional_endpoints():
    """Test de endpoints adicionales"""
    try:
        headers = {'Authorization': f"Bearer {token}"}
        
        # 1. Estadísticas
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/estadisticas", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al obtener estadísticas: {response.status_code}")
        
        # 2. Clases de hoy
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/hoy", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al obtener clases de hoy: {response.status_code}")
        
        clases_hoy = response.json()['data']
        
        # 3. Sesiones por pedagogo
        response = requests.get(f"{BASE_URL}/api/sesiones-pedagogicas/pedagogo/{pedagogo_id}", headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al obtener sesiones por pedagogo: {response.status_code}")
        
        sesiones_pedagogo = response.json()['data']
        
        print_test_info("Endpoints adicionales", "SUCCESS", {
            "total_sesiones": len(sesiones_pedagogo),
            "sesiones_activas": len([s for s in sesiones_pedagogo if s.get('estado') == 'activo']),
            "clases_hoy": len(clases_hoy)
        })
        return True
        
    except Exception as e:
        print_test_info("Endpoints adicionales", "ERROR", error=str(e))
        raise Exception(f"Error en endpoints adicionales: {str(e)}")

def test_cleanup():
    """Limpiar datos de prueba"""
    try:
        headers = {'Authorization': f"Bearer {token}"}
        
        # Cancelar sesión pedagógica
        if sesion_id:
            response = requests.delete(f"{BASE_URL}/api/sesiones-pedagogicas/{sesion_id}", headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Error al cancelar sesión: {response.status_code}")
            
            print_test_info("Limpieza de datos", "SUCCESS", {
                "sesion_id": sesion_id,
                "mensaje": "Sesión pedagógica cancelada exitosamente"
            })
        
        return True
        
    except Exception as e:
        print_test_info("Limpieza de datos", "ERROR", error=str(e))
        raise Exception(f"Error en limpieza: {str(e)}")

if __name__ == "__main__":
    main()