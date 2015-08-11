'''
Created on Aug 8, 2015
@author: yuanx
'''
from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb.model import EndpointsModel

class Sharepoint(EndpointsModel):
    """ Sharepoint. """
    _message_fields_schema = ("entityKey", "title", "detail", "add_date", "user_key", "user_nickname")
    title = ndb.StringProperty()
    detail = ndb.StringProperty()
    add_date = ndb.DateTimeProperty(auto_now_add=True)
    user_key = ndb.KeyProperty()
    user_nickname = ndb.StringProperty()

class Comment(EndpointsModel):
    """ comment under certain sharepoint. """
    _message_fields_schema = ("entityKey", "sharepoint_key", "message", "from_user_key", "from_user_nickname",
                              "to_user_key", "to_user_nickname", "add_date")
    sharepoint_key = ndb.KeyProperty(kind=Sharepoint)
    message = ndb.StringProperty()
    from_user_key = ndb.KeyProperty()
    from_user_nickname = ndb.StringProperty()
    to_user_key = ndb.KeyProperty()
    to_user_nickname = ndb.StringProperty()
    add_date = ndb.DateTimeProperty(auto_now_add=True)

