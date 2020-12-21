from tribes_core.lib import actions
from tribes_django import settings as dj_settings
from tribes_core.lib import events
from tribes_core.models import Message, SubscriptionPerson, Post, Person
import os
import pytest, pprint
from tribes_core.lib import utils


def test_encrypting_and_decoding():
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))

    data = {
        'identifier': keysA['public'].export(private_key=False, as_dict=True),
        'name': 'Torres',
        'url': 'example.com'
    }
    p = events.PERSON.create_from_dict(data)

    message_encrypted_with_B = utils.encrypt_raw_event(p, keysB['public'])

    decrypted_evt = actions.decode_event_and_set_to_model(message_encrypted_with_B, 'PERSON', key_path='./member_B_keys', model=None)

    assert decrypted_evt.data['name'] == 'Torres'
    assert decrypted_evt.data['url'] == 'example.com'


def test_encrypting_from_json_key_representation():
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))
    data = {
        'identifier': keysA['public'].export(private_key=False, as_dict=True),
        'name': 'Torres',
        'url': 'example.com'
    }
    p = events.PERSON.create_from_dict(data)

    message_encrypted_with_B = utils.encrypt_raw_event(p, keysB['public'].export(private_key=False, as_dict=True), is_dict=True)

    decrypted_evt = actions.decode_event_and_set_to_model(message_encrypted_with_B, 'PERSON', key_path='./member_B_keys', model=None)

    assert decrypted_evt.data['name'] == 'Torres'
    assert decrypted_evt.data['url'] == 'example.com'


@pytest.mark.django_db
def test_encrypting_and_decoding_message():
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))

    data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': keysA['public'].export(private_key=False, as_dict=True), 'url': 'mo.com', 'name': 'Test'},
        'receipent': {'identifier': keysB['public'].export(private_key=False, as_dict=True), 'url': 'moomoo.com', 'name': 'Test2'},
        'messageAttachment': {'image': 'image.jpg'}
    }

    pprint.pprint(data)
    message = events.MESSAGE.create_from_dict(data)

    message_encrypted_with_A = utils.encrypt_raw_event(message, keysA['public'])
    message_model = Message()
    decrypted_evt = actions.decode_event_and_set_to_model(message_encrypted_with_A, 'MESSAGE', key_path='./member_A_keys', model=message_model)
    assert type(decrypted_evt.model.sender) is Person
    assert type(decrypted_evt.model.messageAttachment) is Post
    assert decrypted_evt.data['sender']['url'] == 'mo.com'

@pytest.mark.django_db
def test_create_new_subscription_from_follow_request():
    data = {
        'followee': {'identifier': 'ccc', 'url': 'no.com', 'name': 'Bob'},
        'agent': { 'identifier': 'bbb', 'url': 'example.com', 'name': 'Torres'}
    }

    f = events.FOLLOW.create_from_dict(data)
    result = actions.create_new_subscription_from_follow_request(f)
    assert result is True
    sub = SubscriptionPerson.objects.filter(identifier='ccc')[0]
    assert sub.identifier == 'ccc'
    assert sub.url == 'no.com'


@pytest.mark.django_db
def test_sub_url_to_make_new_follow(client):
    dj_settings.KEY_PATH = os.path.join(dj_settings.BASE_DIR, "member_B_keys")
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))

    data = {
        'followee': {'identifier': keysA['public'].export(private_key=False, as_dict=True), 'url': 'no.com', 'name': 'Bob'},
        'agent': { 'identifier': keysB['public'].export(private_key=False, as_dict=True), 'url': 'example.com', 'name': 'Torres'}
    }
    f = events.FOLLOW.create_from_dict(data)
    encrypted_data = utils.encrypt_raw_event(f, keysB['public'])
    res = client.post('/tribes/sub', {'data': encrypted_data})
    assert res.status_code == 200

@pytest.mark.django_db
def test_check_if_message_from_sub():
    dj_settings.KEY_PATH = os.path.join(dj_settings.BASE_DIR, "member_B_keys")
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))

    sub_in_db = SubscriptionPerson()
    sub_in_db.name = 'Test'
    sub_in_db.url = 'mo.com'
    sub_in_db.identifier = keysA['public'].export(private_key=False, as_dict=True)
    sub_in_db.is_followed = False
    sub_in_db.save()

    data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': keysA['public'].export(private_key=False, as_dict=True), 'url': 'mo.com', 'name': 'Test'},
        'receipent': {'identifier': keysB['public'].export(private_key=False, as_dict=True), 'url': 'moomoo.com', 'name': 'Test2'},
        'messageAttachment': {'image': 'image.jpg'}
    }
    message = events.MESSAGE.create_from_dict(data)
    assert actions.check_if_message_from_sub(message) == True


def test_send_new_or_updated_messages(mocker):
    fake_signal = mocker.patch('tribes_core.lib.signals.distribute_messages')
    dj_settings.KEY_PATH = os.path.join(dj_settings.BASE_DIR, "member_B_keys")
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))
    data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': keysA['public'].export(private_key=False, as_dict=True), 'url': 'mo.com', 'name': 'Test'},
        'receipent': {'identifier': keysB['public'].export(private_key=False, as_dict=True), 'url': 'moomoo.com', 'name': 'Test2'},
        'messageAttachment': {'image': 'image.jpg'}
    }
    message = events.MESSAGE.create_from_dict(data)
    actions.send_new_or_updated_messages(message)
    fake_signal.send.assert_called_once()
    fake_signal.send.assert_called_once_with(sender="MessageConsumer", msg=message)

@pytest.mark.django_db
def test_create_message_action():
    short_message = 'short message'
    sender = Person(url='url.com', name='Sender Man', identifier='dkd')
    to = Person(url='sub.com', name='To Man', identifier='aaa')
    evt = actions.create_message(short_message,
        sender,
        to,
        image='pics.jpg', 
        audio='test.mpeg', 
        video='vid.mp4',
        )
    
    assert evt.data['messageAttachment']['text'] == short_message
    assert evt.data['messageAttachment']['video'] == 'vid.mp4'
    assert evt.data['messageAttachment']['image'] == 'pics.jpg'
    assert evt.data['sender']['url'] == 'url.com'




