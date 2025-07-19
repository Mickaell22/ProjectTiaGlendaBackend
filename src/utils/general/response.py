from flask import jsonify

def response_success(data=None, message="Operacion exitosa"):
    """Respuesta de exito estandar"""
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 200

def response_error(message="Error en la operacion", code=400):
    """Respuesta de error estandar"""
    return jsonify({
        "status": "error",
        "message": message,
        "code": code
    }), code

def response_inserted(data=None, message="Registro creado exitosamente"):
    """Respuesta para registros insertados"""
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 201

def internal_response(success=True, data=None, message=""):
    """Respuesta interna para comunicacion entre servicios"""
    return {
        "success": success,
        "data": data,
        "message": message
    }