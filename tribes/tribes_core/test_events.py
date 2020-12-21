from tribes_core.lib import events
from tribes_core import models
from datetime import datetime
import pytest

def test_create_person_event():
    p = events.PERSON()
    assert p.name == 'PERSON'
    assert p.data['identifier'] == ''
    assert p.data["name"] == ''
    assert p.data["url"] == ''

def test_create_follow_event():
    follow = events.FOLLOW()
    assert follow.name == 'FOLLOW'
    assert follow.data["followee"] == {}
    assert follow.data["agent"] == {}

# def test_create_message_event():
#     message = events.MESSAGE()
#     assert message.name == 'MESSAGE'
#     assert message.data["dateRead"] == datetime()
#     assert message.data["dateSent"] == datetime()
#     assert message.data["dateReceived"] == datetime()
#     assert message.data["sender"] == {}
#     assert message.data["receipent"] == {}
#     assert message.data['messageAttachment'] == {}
#     assert message.data["identifier"] == 0


def test_create_person_from_dict():
    data = {
        'identifier': 'abcd',
        'name': 'Torres',
        'url': 'example.com'
    }
    p = events.PERSON.create_from_dict(data)
    assert p.data['name'] == 'Torres'
    assert p.data['identifier'] == 'abcd'
    assert p.data['url'] == 'example.com'

def test_create_follow_event_from_dict():
    data = {
        'followee': {'identifier': 'ccc', 'url': 'no.com', 'name': 'Bob'},
        'agent': { 'identifier': 'bbb', 'url': 'example.com', 'name': 'Torres'}
    }
    f = events.FOLLOW.create_from_dict(data)
    assert f.data['followee']['identifier'] == 'ccc'
    assert f.data['followee']['url'] == 'no.com'
    assert f.data['agent']['url'] == 'example.com'
    assert f.data['agent']['identifier'] == 'bbb'


def test_create_message_event_from_dict():
    data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': 'nnn', 'url': 'mo.com', 'name': 'Test'},
        'receipent': {'identifier': 'xxx', 'url': 'moomoo.com', 'name': 'Test2'},
        'messageAttachment': {'image': 'image.jpg'}

    }
    m = events.MESSAGE.create_from_dict(data)
    assert m.data['dateRead'] == '2020-10-01 00:00:00'
    assert m.data['dateSent'] == '2020-10-01 00:00:00'
    assert m.data['dateReceived'] == '2020-10-01 00:00:00'
    assert m.data['sender'] == {'identifier': 'nnn', 'url': 'mo.com', 'name': 'Test'}
    assert m.data['receipent'] == {'identifier': 'xxx', 'url': 'moomoo.com', 'name': 'Test2'}
    assert m.data['messageAttachment'] == {'image': 'image.jpg'}



def test_converting_to_jsonld():
    message_data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': 'nnn', 'url': 'mo.com', 'name': 'Test'},
        'receipent': {'identifier': 'xxx', 'url': 'moomoo.com', 'name': 'Test2'},
        'messageAttachment': {'image': 'image.jpg'}

    }

    evt = events.MESSAGE.create_from_dict(message_data)
    evt_ld = evt.to_jsonld()
    assert '"@type": "MESSAGE"' in evt_ld
    assert '"identifier": "xxx"' in evt_ld


    person_data = {
        'identifier': 'abcd',
        'name': 'Torres',
        'url': 'example.com'
    }
    p = events.PERSON.create_from_dict(person_data)
    p_ld = p.to_jsonld()
    assert '"@type": "PERSON"' in p_ld
    assert '"name": "Torres"' in p_ld


@pytest.mark.django_db
def test_set_model():
    sub = models.SubscriptionPerson(identifier='aaa', url='url.com', name='Test1')
    person = models.Person(identifier='bbb', url='a.com', name='Test2')
    sub.save()
    person.save()

    message_data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': sub.identifier, 'url': sub.url, 'name': sub.name},
        'receipent': {'identifier': person.identifier, 'url': person.url, 'name': person.name},
        'messageAttachment': {'image': 'image.jpg'}
    }
    evt = events.MESSAGE.create_from_dict(message_data)
    evt.set_model(models.Message())
    sub_query = models.SubscriptionPerson.objects.filter(identifier='aaa')
    assert len(sub_query) == 1

@pytest.mark.django_db
def test_create_person_event_from_db_record():
    model = models.Person()
    model.name = 'Test'
    model.identifier = 'abbb'
    model.url = 'example.com'
    model.is_owner = True
    person_event = events.PERSON.create_from_db_record(model)
    assert person_event.data['name'] == model.name
    assert 'is_owner' not in person_event.data.keys()
    assert 'is_followed' not in person_event.data.keys()

@pytest.mark.django_db
def test_create_message_event_from_db_record():
    sender = models.Person()
    sender.name = 'Test'
    sender.identifier = 'aaa'
    sender.url = 'example.com'
    sender.save()

    receipent = models.Person()
    receipent.name = 'Test'
    receipent.identifier = 'bbb'
    receipent.url = 'test.com'
    receipent.save()

    post = models.Post()
    post.author = sender.name
    post.video = None
    post.text = 'Example message'
    post.audio = None
    post.thumbnailURL = 'link'
    post.image = None
    post.save()

    model = models.Message()
    model.dateRead = None
    model.dateSent = datetime(year=2020, month=1, day=1, hour=0, minute=0, second=0)
    model.sender = sender
    model.receipent = receipent
    model.messageAttachment = post
    model.save()

    message_event = events.MESSAGE.create_from_db_record(model)
    assert message_event.data['dateSent'] == '2020-01-01 00:00:00'
    assert message_event.data['dateReceived'] != None
    assert message_event.data['sender'] == {'identifier': 'aaa', 'url':'example.com', 'name': 'Test'}
    assert message_event.data['receipent'] == {'identifier': 'bbb', 'url':'test.com', 'name': 'Test'}
    assert message_event.data['messageAttachment'] == {'author': 'Test', 'video': None, 'image': None, 'audio': None, 'text': 'Example message', 'thumbnailURL': 'link'}
