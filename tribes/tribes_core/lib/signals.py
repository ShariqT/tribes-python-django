import django.dispatch
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from tribes_django import settings
from tribes_core import models
from tribes_core.lib.utils import encrypt_raw_event
distribute_messages = django.dispatch.Signal()

def generate_encrypted_message_for_followers(message_evt):
    site_list = []
    followers = models.Person.objects.filter(is_follower=True)
    for follower in followers:
        entry = dict()
        entry['url'] = follower.url
        entry['message'] = encrypt_raw_event(message_evt, follower.identifier, is_dict=True)
        site_list.append(entry)
    return site_list

def notifier(sender, **kwargs):
    site_list = generate_encrypted_message_for_followers(kwargs['msg'])
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)("distribute_messages", {
        "type":"mailout",
        "site_list": site_list
    })

distribute_messages.connect(notifier)