# pylint: disable=line-too-long, no-member

import importlib
import json
import logging
import mimetypes
import tempfile
import time

from io import BytesIO

import aiofiles
import requests

from PIL import Image

from django.conf import settings
from django.core import files
from django.core.files.base import File
from django.http import HttpResponse
from django.utils import timezone

from simple_messaging.models import IncomingMessage, IncomingMessageMedia, BlockedSender

logger = logging.getLogger(__name__) # pylint: disable=invalid-name

from .models import fetch_matrix_client

def process_outgoing_message(outgoing_message, metadata=None): # pylint: disable=too-many-branches, too-many-locals, too-many-statements
    if metadata is None:
        metadata = {}

    client = fetch_matrix_client(metadata)

    content_uris = []

    for media_item in outgoing_message.media.all():
        file_stat = await aiofiles.os.stat(media_item.content_file.path)
    
        async with aiofiles.open(image, "r+b") as media_file:
            resp, _maybe_keys = await client.upload(
                media_file,
                content_type=media_item.content_type,
                filename=os.path.basename(media_item.content_file.path),
                filesize=file_stat.st_size,
            )
        if isinstance(resp, UploadResponse):
            content_uris.append(resp.content_uri)
        else:
            print(f"Failed to upload image. Failure response: {resp}")

    for content_uri in content_uris:
        content = {
            "body": os.path.basename(media_item.content_file.path),
            "info": {
                "size": file_stat.st_size,
                "mimetype": media_item.content_type,
                "thumbnail_info": None,
                "w": width,  # width in pixel
                "h": height,  # height in pixel
                "thumbnail_url": None,
            },
            "msgtype": "m.image", # TODO: Check type
            "url": content_uri,
        }

        try:
            await client.room_send(room_id, message_type="m.room.message", content=content)
        except Exception:
            print(f"Image send of file {image} failed.")


    transmission_metadata = {}

    if outgoing_message.transmission_metadata is not None:
        try:
            transmission_metadata = json.loads(outgoing_message.transmission_metadata)
        except ValueError:
            transmission_metadata = {}

    outgoing_message_content = outgoing_message.fetch_message(transmission_metadata)

    await client.room_send(
        outgoing_message.current_destination(),
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": outgoing_message_content
        },
    )

    await client.close()

    metadata['twilio_sid'] = twilio_sids

    return metadata

    # return None

def simple_messaging_media_enabled(outgoing_message): # pylint: disable=unused-argument
    try:
        return settings.SIMPLE_MESSAGING_MEDIA_ENABLED
    except AttributeError:
        pass

    return True

def process_incoming_request(request): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    pass

    # payload = {
    #     destination: room.machine_name,
    #     body: event.body,
    #     formatted_body: event.formatted_body,
    #     body_format: event.body,
    # }

    # payload = {
    #     destination: room.machine_name,
    #     body: event.body,
    #     url: url
    # }
    

    # if request.POST.get('MessageSid', None) is None:
    #     return None

    # response = '<?xml version="1.0" encoding="UTF-8" ?><Response>'

    # responses = []

    # for app in settings.INSTALLED_APPS:
    #     try:
    #         response_module = importlib.import_module('.simple_messaging_api', package=app)

    #         responses.extend(response_module.simple_messaging_response(request.POST))
    #     except ImportError:
    #         pass
    #     except AttributeError:
    #         pass

    # for message in responses:
    #     response += '<Message>' + message + '</Message>'

    # response += '</Response>'

    # if request.method == 'POST': # pylint: disable=too-many-nested-blocks
    #     sender = request.POST['From']

    #     if BlockedSender.objects.filter(sender=sender).count() > 0:
    #         response = '<?xml version="1.0" encoding="UTF-8" ?><Response></Response>'

    #         logging.info('[simple_messaging_twilio] Blocked incoming message from %s.', sender)

    #         return HttpResponse(response, content_type='text/xml')

    #     record_responses = True

    #     for app in settings.INSTALLED_APPS:
    #         try:
    #             response_module = importlib.import_module('.simple_messaging_api', package=app)

    #             record_responses = response_module.simple_messaging_record_response(request.POST)
    #         except ImportError:
    #             pass
    #         except AttributeError:
    #             pass

    #     if record_responses:
    #         now = timezone.now()

    #         destination = request.POST['To']

    #         incoming = IncomingMessage(recipient=destination, sender=sender)
    #         incoming.receive_date = now
    #         incoming.message = request.POST['Body'].strip()
    #         incoming.transmission_metadata = json.dumps(dict(request.POST), indent=2)

    #         incoming.save()

    #         incoming.encrypt_sender()

    #         num_media = 0

    #         media_objects = {}

    #         if 'NumMedia' in request.POST:
    #             num_media = int(request.POST['NumMedia'])

    #             for i in range(0, num_media):
    #                 media = IncomingMessageMedia(message=incoming)

    #                 media.content_url = request.POST['MediaUrl' + str(i)]
    #                 media.content_type = request.POST['MediaContentType' + str(i)]
    #                 media.index = i

    #                 media.save()

    #                 media_response = requests.get(media.content_url, timeout=120)

    #                 if media_response.status_code != requests.codes.ok:
    #                     continue

    #                 filename = media.content_url.split('/')[-1]

    #                 extension = mimetypes.guess_extension(media.content_type)

    #                 if extension is not None:
    #                     if extension == '.jpe':
    #                         extension = '.jpg'

    #                     filename += extension

    #                 file_bytes = BytesIO()
    #                 file_bytes.write(media_response.content)

    #                 media.content_file.save(filename, files.File(file_bytes))
    #                 media.save()

    #                 media_objects[filename] = {
    #                     'content': file_bytes.getvalue(),
    #                     'mime-type': media.content_type
    #                 }

    #         for app in settings.INSTALLED_APPS:
    #             try:
    #                 response_module = importlib.import_module('.simple_messaging_api', package=app)

    #                 response_module.process_incoming_message(incoming)
    #             except ImportError:
    #                 pass
    #             except AttributeError:
    #                 pass

    # return HttpResponse(response, content_type='text/xml')
