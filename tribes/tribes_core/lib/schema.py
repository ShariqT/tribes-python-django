SCHEMA = {
    '1.0': {
        'THING': {
            "identifier": 'str',
            "name": 'str',
            "url": 'str'
        },
        'FOLLOW_ACTION': {
            "followee": 'obj',
            "agent": 'obj'
        },
        'CREATIVE_WORK': {
            "author": 'obj',
            "video": 'obj',
            "text": 'text',
            "audio": 'str',
            "thumbnailURL": 'str',
            "image": 'str'
        },
        'MESSAGE': {
            "dateRead": 'date',
            "dateSent": 'date',
            "dateReceived": 'date',
            "sender": 'obj',
            "receipent": 'obj',
            "messageAttachment": 'obj'
        }
    }
}