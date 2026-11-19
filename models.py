from django.db import models

def fetch_matrix_client(configuration):
    homeserver = configuration.get('matrix_homeserver', None)

    if homeserver is None:
        if hasattr(settings, 'SIMPLE_MESSAGING_MATRIX_HOMESERVER'):
            homeserver = settings.SIMPLE_MESSAGING_MATRIX_HOMESERVER
        else:
            return None

    user_id = configuration.get('matrix_user_id', None)

    if user_id is None:
        if hasattr(settings, 'SIMPLE_MESSAGING_MATRIX_USER_ID'):
            user_id = settings.SIMPLE_MESSAGING_MATRIX_USER_ID
        else:
            return None

    device_id = configuration.get('matrix_device_id', None)

    if device_id is None:
        if hasattr(settings, 'SIMPLE_MESSAGING_MATRIX_DEVICE_ID'):
            device_id = settings.SIMPLE_MESSAGING_MATRIX_DEVICE_ID
        else:
            return None

    access_token = configuration.get('matrix_access_token', None)

    if access_token is None:
        if hasattr(settings, 'SIMPLE_MESSAGING_MATRIX_ACCESS_TOKEN'):
            access_token = settings.SIMPLE_MESSAGING_MATRIX_ACCESS_TOKEN
        else:
            return None

    client = AsyncClient(homeserver)

    client.access_token = access_token
    client.user_id = user_id
    client.device_id = device_id

    return client
    