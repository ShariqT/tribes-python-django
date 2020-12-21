import os, json
from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from jwcrypto.jwe import JWE
from tribes_core.lib import exceptions 
from tribes_core.lib import events
from jwcrypto.common import json_encode, json_decode
from tribes_django import settings
from tribes_core import models
from tribes_core.lib import signals
from datetime import datetime

"""
check_for_pems -- takes in a list of files from an directory
will check to see if the public and private PEM files are in 
the directory
"""
def check_for_pems(save_path):
    try:
        directory_files = os.listdir(save_path)
        if 'private.pem' in directory_files and 'public.pem' in directory_files:
            return True
        return False
    except FileNotFoundError:
        return False

"""
generate_pems -- takes in a string file path that will be the
destination of the generated JWK keys. Returns True or raises
an KeyNotMadeException.
"""
def generate_pems(save_path):
    if os.path.isdir(save_path) is False:
        os.mkdir(save_path)
    try:
        key_obj = JWK.generate(kty='RSA', size=2048)
        public_pem_bytes = key_obj.export_to_pem(password=None)
        priv_pem_bytes = key_obj.export_to_pem(private_key=True, password=None)

        pub = open(os.path.join(save_path, "public.pem"), 'wb+')
        pub.write(public_pem_bytes)
        pub.close()

        priv = open(os.path.join(save_path, "private.pem"), 'wb+')
        priv.write(priv_pem_bytes)
        priv.close()

        return True
    except Exception as e:
        raise exceptions.KeyNotCreated(repr(e))


def create_public_thumbprint(save_path):
    key = JWK.from_pem(os.path.join(save_path, "public.pem"))
    return key.export()

def encrypt_raw_event(evt, public_key, is_dict=False):
    payload = evt.to_jsonld()
    if is_dict is True:
        public_key = JWK.from_json(json_encode(public_key))
    protected_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256CBC-HS512",
        "typ": "JWE",
        "kid": public_key.thumbprint(),
    }
    data = JWE(
        payload.encode('utf-8'),
        recipient=public_key,
        protected=protected_header
    )

    return data.serialize()



def load_keys(save_path):
    fppub = open(os.path.join(save_path, "public.pem"), 'rb')
    fppriv = open(os.path.join(save_path, "private.pem"), 'rb')
    pub_key = JWK.from_pem(fppub.read())
    priv_key = JWK.from_pem(fppriv.read())
    fppub.close()
    fppriv.close()
    return {'public': pub_key, 'private': priv_key}

def unpack_message(packed_message):
    message_event = events.MESSAGE.create_from_dict(json.loads(packed_message))
    return message_event

def unpack_person(packed_person):
    person_event = events.PERSON.create_from_dict(json.loads(packed_person))
    return person_event

def unpack_follow(packed_follow):
    follow_event = events.FOLLOW.create_from_dict(json.loads(packed_follow))
    return follow_event

def decrypt_and_decode(raw_string, key_pair):
    token = JWE()
    token.deserialize(raw_string, key=key_pair['private'])
    return token.payload

def decode_event_and_set_to_model(encrypted_event, event_type, model=None, key_path=None):
    if key_path is None:
        keys = load_keys(settings.KEY_PATH)
    else:
        keys = load_keys(key_path)
    raw_evt = None
    if event_type == 'MESSAGE':
        raw_evt = unpack_message(decrypt_and_decode(encrypted_event, keys))
    elif event_type == 'PERSON':
        raw_evt = unpack_person(decrypt_and_decode(encrypted_event, keys))
    elif event_type == 'FOLLOW':
        raw_evt = unpack_follow(decrypt_and_decode(encrypted_event, keys))
    else:
        raise exceptions.EventTypeNotFound('Could not find {} in event Types'.format(event_type))

    if model is not None:
        raw_evt.set_model(model)
        raw_evt.save_event_to_db()

    return raw_evt


def create_new_subscription_from_follow_request(follow_event, is_sub=True):
    try:
        if is_sub is True:
            follow_model = models.SubscriptionPerson()
            follow_model.identifier = follow_event.data['followee']['identifier']
            follow_model.url = follow_event.data['followee']['url']
            follow_model.name = follow_event.data['followee']['name']
            follow_model.save()
        else:
            follow_model = models.SubscriptionPerson()
            follow_model.identifier = follow_event.data['agent']['identifier']
            follow_model.url = follow_event.data['agent']['url']
            follow_model.name = follow_event.data['agent']['name']
            follow_model.is_sub = False
            follow_model.save()
        return True
    except Exception as e:
        print(e)
        return False


def check_if_message_from_sub(message_evt):
    record = models.SubscriptionPerson.objects.filter(
        url = message_evt.data['sender']['url'],
        name = message_evt.data['sender']['name'],
        identifier = message_evt.data['sender']['identifier'],
        is_followed = False
    )
    if record is None:
        return False
    else:
        return True



def send_new_or_updated_messages(message_evt):
    signals.distribute_messages.send(sender="MessageConsumer", msg=message_evt)


def create_message(message, sender, receipent, **kwargs):
    post_info = {}
    post_info['text'] = message
    post_info['video'] = kwargs['video'] if 'video' in kwargs.keys() else None
    post_info['audio'] = kwargs['audio'] if 'audio' in kwargs.keys() else None
    post_info['author'] = sender.name
    post_info['image'] = kwargs['image'] if 'image' in kwargs.keys() else None

    data = {
        'dateRead': None,
        'dateSent': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'dateReceived': None,
        'sender': {'identifier': sender.identifier, 'url': sender.url, 'name': sender.name },
        'receipent': {'identifier': receipent.identifier, 'url': receipent.url, 'name': receipent.name },
        'messageAttachment': post_info
    }
    evt = events.MESSAGE.create_from_dict(data)
    evt.set_model(models.Message())
    return evt
    
# @TODO: fill out this function to get the name
def get_site_owner_name():
    return "Site Owner"

def get_all_message_drafts():
    return models.Post.objects.filter(is_draft = True)

def get_draft_by_id(id):
    return models.Post.objects.get(id=id)

def read_message():
    pass

