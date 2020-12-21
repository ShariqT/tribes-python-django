from tribes_core.lib import signals
from tribes_core import models
from tribes_core.lib import events
from tribes_core.lib import utils
from tribes_core.lib import actions
import pytest
from tribes_django import settings as dj_settings
import os



@pytest.mark.django_db
def test_generate_encrypted_message_for_followers(mocker):
    fake_request = mocker.patch('tribes_core.lib.signals.distribute_messages')
    fake_http = mocker.patch('requests.post')
    keysA = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_A_keys"))
    keysB = actions.load_keys(os.path.join(dj_settings.BASE_DIR, "member_B_keys"))

    record1 = models.Person(identifier=str(keysA['public'].export(private_key=False, as_dict=True)), name='Test', url='test.com')
    record1.save()
    record1.is_follower = True
    record1.save()
    record2 = models.Person(identifier=str(keysB['public'].export(private_key=False, as_dict=True)), name='Test 2', url='test2.com')
    record2.is_follower = True
    record2.save()
    data = {
        'dateRead': '2020-10-01 00:00:00',
        'dateSent': '2020-10-01 00:00:00',
        'dateReceived': '2020-10-01 00:00:00',
        'sender': {'identifier': keysA['public'].export(private_key=False, as_dict=True), 'url': 'mo.com', 'name': 'Test'},
        'receipent': {'identifier': keysB['public'].export(private_key=False, as_dict=True), 'url': 'moomoo.com', 'name': 'Test2'},
        'messageAttachment': {'image': 'image.jpg'}
    }
    message = events.MESSAGE.create_from_dict(data)

    site_list = signals.generate_encrypted_message_for_followers(message)
    assert site_list[0]['url'] == 'test.com'
    assert site_list[1]['url'] == 'test2.com'
