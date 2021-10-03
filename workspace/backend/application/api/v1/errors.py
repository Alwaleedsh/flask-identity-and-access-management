from flask import jsonify

from . import bp

@bp.app_errorhandler(400)
def bad_request(error):
    # body:
    response = jsonify(
        {
            "success": False, 
            "error": 400,
            "message": str(error)
        }
    )

    return response, 400

@bp.app_errorhandler(401)
def unauthorized(error):
    # body:
    response = jsonify(
        {
            "success": False, 
            "error": 401,
            "message": str(error)
        }
    )

    return response, 403  

@bp.app_errorhandler(403)
def forbidden(error):
    # body:
    response = jsonify(
        {
            "success": False, 
            "error": 403,
            "message": str(error)
        }
    )

    return response, 403    

@bp.app_errorhandler(404)
def not_found(error):
    # body:
    response = jsonify(
        {
            "success": False, 
            "error": 404,
            "message": str(error)
        }
    )

    return response, 404

@bp.errorhandler(422)
def unprocessable(error):
    # body:
    response = jsonify(
        {
            "success": False, 
            "error": 422,
            "message": str(error)
        }
    )

    return response, 422

@bp.app_errorhandler(500)
def internal_server_error(error):
    # body:
    response = jsonify(
        {
            "success": False, 
            "error": 500,
            "message": str(error)
        }
    )

    return response, 500