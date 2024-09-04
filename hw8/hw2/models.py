from mongoengine import Document, StringField, BooleanField

class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True, unique=True)
    message_sent = BooleanField(default=False)
    additional_info = StringField()