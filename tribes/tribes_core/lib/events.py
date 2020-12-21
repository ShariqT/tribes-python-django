from tribes_core.lib.schema import SCHEMA
import json
from tribes_core import models as tribe_model


class ByteEncoder(json.JSONEncoder):
    #pylint: disable=method-hidden
    def default(self, x):
        if isinstance(x, bytes):
            return str(x, "UTF-8")
        else:
            super().default(x)

class BaseEvent:
    def __init__(self):
        self.name = ''
        self.data = {}
        self.model = None
        self.schema_type_version = '1.0'
    
    """
        set_model takes in a django ORM model
        that will be attached to this event
    """
    def set_model(self, django_model):
        self.model = django_model
        for key in self.data.keys():
            setattr(self.model, key, self.data[key])
        
    
    """
        set_name takes in a string. This 
        sting will set the Event Name
    """
    def set_name(self, name):
        self.name = name
    
    """
        __set_default_data takes in Schema.org Model (e.g. THING, FollowAction)
        and sets up the data property with default values
    """
    def _set_default_data(self, data_type):
        self.data = {}
        valid_schema = SCHEMA[self.schema_type_version][data_type]
        for i in valid_schema.keys():
            if valid_schema[i] == 'str':
                self.data[i] = ''
            elif valid_schema[i] == 'int':
                self.data[i] = 0
            elif valid_schema[i] == 'float':
                self.data[i] = 0.0
            elif valid_schema[i] == 'text':
                self.data[i] = ''
            elif valid_schema[i] == 'obj':
                self.data[i] = {}
            else:
                self.data[i] = None
    
    """
        save_event_to_db will persist the event to the database
    """
    def save_event_to_db(self):
        self.model.save()


    def to_jsonld(self):
        print("calling tojsonld")
        return_obj = {}
        return_obj['@context'] = 'https://schema.org/'
        return_obj['@type'] = self.name
        for key in self.data.keys():
            return_obj[key] = self.data[key]
        return json.dumps(return_obj)

    @classmethod
    def create_from_dict(cls, data_dict):
        new_obj = cls()
        print('calling create from dict')
        data_keys = new_obj.data.keys()
        for key in data_dict.keys():
            if key in data_keys:
                new_obj.data[key] = data_dict[key]
        return new_obj
    
    @classmethod
    def create_from_db_record(cls, db_record):
        new_obj = cls()
        data_keys = new_obj.data.keys()
        for key in db_record.__dict__.keys():
            if key in data_keys:
                new_obj.data[key] = getattr(db_record, key)
        new_obj.set_model(db_record)
        return new_obj

    
    

class FOLLOW(BaseEvent):
    def __init__(self):
        super().__init__()
        self.set_name('FOLLOW')
        self._set_default_data('FOLLOW_ACTION')

class MESSAGE(BaseEvent):
    def __init__(self):
        super().__init__()
        self.set_name('MESSAGE')
        self._set_default_data('MESSAGE')
        

    def set_model(self, django_model):
        self.model = django_model
        self.model.dateSent = self.data['dateSent']
        self.model.dateReceived = self.data['dateReceived']
        self.model.dateRead = self.data['dateRead']
        sub = tribe_model.Person.objects.filter(url=self.data['sender']['url'])
        if len(sub) == 0:
            self.model.sender = tribe_model.Person()
            self.model.sender.identifier = self.data['sender']['identifier']
            self.model.sender.name = self.data['sender']['name']
            self.model.sender.url = self.data['sender']['url']
            self.model.sender.save()
        else:
            self.model.sender = sub[0]
        person = tribe_model.Person.objects.filter(url=self.data['receipent']['url'])
        if len(person) == 0:
            self.model.receipent = tribe_model.Person()
            self.model.receipent.identifier = self.data['receipent']['identifier']
            self.model.receipent.url = self.data['receipent']['url']
            self.model.receipent.name = self.data['receipent']['name']
            self.model.receipent.save()
        else:
            self.model.receipent = person[0]
        self.model.messageAttachment = tribe_model.Post()
        self.model.messageAttachment.author = self.data['receipent']['name']
        for k in self.data['messageAttachment'].keys():
            setattr(self.model.messageAttachment, k, self.data['messageAttachment'][k])
        self.model.messageAttachment.save()


    @classmethod
    def create_from_db_record(cls, db_record):
        new_obj = cls()
        data_keys = new_obj.data.keys()
        for key in db_record.__dict__.keys():
            if key in data_keys:
                if key == 'dateSent' or key == 'dateReceived' or key == 'dateRead':
                    if getattr(db_record, key) != None:
                        new_obj.data[key] = getattr(db_record, key).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        new_obj.data[key] = None
                else:
                    new_obj.data[key] = getattr(db_record, key)
        
        new_obj.data['sender'] = PERSON.create_from_db_record(db_record.sender).data
        new_obj.data['receipent'] = PERSON.create_from_db_record(db_record.receipent).data
        new_obj.data['messageAttachment'] = POST.create_from_db_record(db_record.messageAttachment).data
        print(new_obj.data)
        new_obj.set_model(db_record)
        return new_obj


class PERSON(BaseEvent):
    def __init__(self):
        super().__init__()
        self.set_name('PERSON')
        self._set_default_data('THING')
    
    def to_jsonld(self):
        return_obj = {}
        return_obj['@context'] = 'https://schema.org/'
        return_obj['@type'] = self.name
        for key in self.data.keys():
            return_obj[key] = self.data[key]
        return json.dumps(return_obj, cls=ByteEncoder)
    
    @classmethod
    def create_from_dict(cls, data_dict):
        new_obj = cls()
        print('calling create from dict')
        data_keys = new_obj.data.keys()
        for key in data_dict.keys():
            if key in data_keys:
                new_obj.data[key] = data_dict[key]
        return new_obj
    
    @classmethod
    def create_from_db_record(cls, db_record):
        new_obj = cls()
        data_keys = new_obj.data.keys()
        for key in db_record.__dict__.keys():
            if key in data_keys:
                new_obj.data[key] = getattr(db_record, key)
        new_obj.set_model(db_record)
        return new_obj


class POST(BaseEvent):
    def __init__(self):
        super().__init__()
        self.set_name('CREATIVE_WORK')
        self._set_default_data('CREATIVE_WORK')


