# pylint: disable=no-member, line-too-long, superfluous-parens

import json

from django.conf import settings
from django.core.management.base import BaseCommand

from quicksilver.decorators import handle_lock, handle_schedule, add_qs_arguments, handle_logging
from simple_messaging_switchboard.models import Channel

class LocalRequest:
    POST = {}
    GET = {}

    def __init__(self, details):
        self.POST.update(details)
        self.GET.update(details)

async def message_text_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    payload = {
        destination: room.machine_name,
        body: event.body,
        formatted_body: event.formatted_body,
        body_format: event.body,
    }

    local_request = LocalRequest(payload)

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            response = response_module.process_incoming_request(local_request)

            if response is not None:
                return response
        except ImportError:
            pass
        except AttributeError:
            pass

    raise Http404("No module found to process incoming message.")

async def message_media_callback(room: MatrixRoom, event: RoomMessageMedia) -> None:
    payload = {
        destination: room.machine_name,
        body: event.body,
        url: url
    }

    local_request = LocalRequest(payload)

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            response = response_module.process_incoming_request(local_request)

            if response is not None:
                return response
        except ImportError:
            pass
        except AttributeError:
            pass

    raise Http404("No module found to process incoming message.")


class Command(BaseCommand):
    help = 'Sets up a persistent listener for a Matrix endpoint'

    @add_qs_arguments
    def add_arguments(self, parser):
        parser.add_argument('channel', type=str, default='', help='Channel identifier for Matrix configuration.')

    @handle_logging
    @handle_schedule
    @handle_lock
    @log_scheduled_event
    def handle(self, *args, **options):
        configuration = {}

        channel = Channel.objects.filter(identifier=options.get('channel', None)).first()

        if channel is not None:
            configuration = channel.configuration

        client = fetch_matrix_client(configuration)

        client.add_event_callback(message_text_callback, RoomMessageText)
        client.add_event_callback(message_media_callback, RoomMessageText)

        asyncio.run(client.sync_forever(timeout=0))