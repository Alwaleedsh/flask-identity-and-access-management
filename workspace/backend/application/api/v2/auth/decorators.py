from jose import jwt
from urllib.request import urlopen
import json

from flask import current_app as app
from flask import request, abort

from functools import wraps


class AuthError(Exception):
    """ exception for Auth0 JWT verification
    """
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

#  AUTHENTICATION
#  ----------------------------------------------------------------
def get_token():
    """ obtains the Auth0 JWT token from the Authorization header
    """
    # get authorization header:
    auth = request.headers.get('Authorization', None)
    

    # authorization header should be included:
    if auth is None:
        raise AuthError(
            {
                'code': 'authorization_header_missing',
                'description': 'Authorization header is expected.'
            }, 
            401
        )
    

    # authorization header should be 'Bearer [JWT]'
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization header must start with "Bearer".'
            }, 
            401
        )
    elif len(parts) == 1:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Token not found.'
            }, 
            401
        )
    elif len(parts) > 2:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization header must be bearer token.'
            }, 
            401
        )

    # extract JWT:
    token = parts[1]

    return token


def verify_decode_token(token):
    """ verify and decode JWT for Auth0
    """
    # load public keys:
    jsonurl = urlopen(f'{app.config["AUTH0_API_DOMAIN"]}.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # extract JWT header:
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 
            401
        )

    # select the public key declared in JWT:
    rsa_key = None
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    # if matching key is selected:
    if not (rsa_key is None):
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=app.config["AUTH0_API_SIGNATURE_ALGORITHMS"],
                audience=app.config["AUTH0_API_AUDIENCE"],
                issuer=app.config["AUTH0_API_DOMAIN"]
            )

            return payload
        # if token has expired:
        except jwt.ExpiredSignatureError:
            raise AuthError(
                {
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 
                401
            )
        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    'code': 'invalid_claims',
                    'description': 'Incorrect claims. Please, check the audience and issuer.'
                }, 
                401
            )
        except Exception:
            raise AuthError(
                {
                    'code': 'invalid_header',
                    'description': 'Unable to parse authentication token.'
                }, 
                400
            )
    # if no matching key is found:
    raise AuthError(
        {
            'code': 'invalid_header',
            'description': 'Unable to find the appropriate key.'
        }, 
        400
    )

#  AUTHORIZATION
#  ----------------------------------------------------------------
class Permission:
    GET_DRINKS_DETAIL = 'get:drinks-detail'
    POST_DRINKS = 'post:drinks'
    PATCH_DRINKS = 'patch:drinks'
    DELETE_DRINKS = 'delete:drinks'


def check_permission(payload, permission):
    """ RBAC
    """
    if 'permissions' not in payload:
        raise AuthError(
            {
                'code': 'invalid_claims',
                'description': 'Permissions not included in JWT.'
            }, 
            400
        )

    if permission not in payload['permissions']:
        raise AuthError(
            {
                'code': 'unauthorized',
                'description': 'Permission not found.'
            }, 
            403
        )

#  AUTHENTICATION
#  ----------------------------------------------------------------
def requires_auth(permission = None):
    """ decorator for authentication
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # get JWT token:
                token = get_token()
                # authentication:
                payload = verify_decode_token(token)
                # authorization:
                if not (permission is None):
                    check_permission(payload, permission)
            except AuthError as e:
                abort(e.status_code, description=e.error["description"])
                
            return f(payload, *args, **kwargs)
        return decorated_function
    return decorator