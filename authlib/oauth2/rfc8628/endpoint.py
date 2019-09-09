from authlib.common.security import generate_token
from authlib.common.urls import add_params_to_qs


class DeviceAuthorizationEndpoint(object):
    USER_CODE_TYPE = 'string'

    #: The lifetime in seconds of the "device_code" and "user_code"
    EXPIRES_IN = 1800

    #: The minimum amount of time in seconds that the client SHOULD
    #: wait between polling requests to the token endpoint.
    INTERVAL = 5

    RESPONSE_HEADER = [
        ('Content-Type', 'application/json'),
        ('Cache-Control', 'no-store'),
        ('Pragma', 'no-cache'),
    ]

    def __init__(self, server, verification_uri):
        self.server = server
        self.verification_uri = verification_uri

    def validate_authorization_request(self, request):
        # https://tools.ietf.org/html/rfc8628#section-3.1
        self.server.validate_requested_scope(request.scope)
        self.server.authenticate_client(request, ['none'])

    def create_authorization_response(self, request):
        self.validate_authorization_request(request)

        device_code = self.create_device_code()
        user_code = self.create_user_code()
        verification_uri = self.verification_uri
        verification_uri_complete = add_params_to_qs(
            verification_uri, [('user_code', user_code)])

        data = {
            'device_code': device_code,
            'user_code': user_code,
            'verification_uri': verification_uri,
            'verification_uri_complete': verification_uri_complete,
            'expires_in': self.EXPIRES_IN,
            'interval': self.INTERVAL,
        }

        self.save_device_credential(request.client_id, request.scope, data)
        return 200, data, self.RESPONSE_HEADER

    def create_user_code(self):
        # https://tools.ietf.org/html/rfc8628#section-6.1
        if self.USER_CODE_TYPE == 'digital':
            return create_digital_user_code()
        return create_string_user_code()

    def create_device_code(self):
        return generate_token(42)

    def save_device_credential(self, client_id, scope, data):
        raise NotImplementedError()


def create_string_user_code():
    base = 'BCDFGHJKLMNPQRSTVWXZ'
    return '-'.join([generate_token(4, base), generate_token(4, base)])


def create_digital_user_code():
    base = '0123456789'
    return '-'.join([
        generate_token(3, base),
        generate_token(3, base),
        generate_token(3, base),
    ])