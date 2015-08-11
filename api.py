'''
Created on Aug 9, 2015
@author: yuanx
'''
import protorpc
import endpoints
from models import Sharepoint, Comment
import main
from google.appengine.ext import ndb

WEB_CLIENT_ID = "702117983306-uo985e1nandi1slhh1gt8op69egjme34.apps.googleusercontent.com"
ANDROID_CLIENT_ID = "702117983306-7no2grmuh6tp219vojh1f85itbm4va54.apps.googleusercontent.com"
IOS_CLIENT_ID = ""

@endpoints.api(name="sharepointviewer", version="v1", description="Sharepoint viewer API",
audiences=[WEB_CLIENT_ID],
               allowed_client_ids=[endpoints.API_EXPLORER_CLIENT_ID, WEB_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID])
class SharepointViewerApi(protorpc.remote.Service):

    @Sharepoint.query_method(user_required=True, query_fields=("limit", "pageToken"),
                             name="sharepoint.listAll", path="sharepoint/listAll", http_method="GET")
    def sharepoint_list_all(self, query):
        """ list all the sharepoints in the server """
        return query.order(-Sharepoint.add_date)


    @Sharepoint.query_method(user_required=True, query_fields=("limit", "pageToken"), name="sharepoint.list",
                             path="sharepoint/list", http_method="GET")
    def sharepoint_list(self, query):
        """ list all the sharepoints belonged to the current user """
        user = endpoints.get_current_user()
        sharepoints = Sharepoint.query(Sharepoint.user_key == main.get_user_key(user)).order(-Sharepoint.add_date)
        return sharepoints

    @Sharepoint.method(user_required=True, name="sharepoint.insert", path="sharepoint/insert", http_method="POST")
    def sharepoint_insert(self, sharepoint):
        """ Update or insert a new Sharepoint """
        if sharepoint.from_datastore:
            sharepoint_with_parent = sharepoint
        else:
            user = endpoints.get_current_user()
            sharepoint_with_parent = Sharepoint(user_key=main.get_user_key(user), detail=sharepoint.detail,
                                                title=sharepoint.title, user_nickname=user.nickname())
        sharepoint_with_parent.put()
        return sharepoint_with_parent

    @Sharepoint.method(user_required=True, response_fields=("entityKey",), name="sharepoint.delete",
                       path="assignment/delete/{entityKey}", http_method="DELETE")
    def sharepoint_delete(self, sharepoint):
        """ Delete the sharepoint with the entityKey, plus all the associated comments"""
        if not sharepoint.from_datastore:
            raise endpoints.NotFoundException("No Sharepoint found for the given key")
        children = Comment.query(Comment.sharepoint_key == sharepoint.key)
        for comment in children:
            comment.key.delete()
        sharepoint.key.delete()
        return Sharepoint(title="deleted")

    @Comment.query_method(user_required=True, query_fields=("limit", "order", "pageToken", "sharepoint_key"),
                          name="comment.list", path="comment/list/{sharepoint_key}", http_method="GET")
    def comment_list(self, query):
        """ list all the comments under certain Sharepoint and belongs to the current user """
        user = endpoints.get_current_user()
        return query.filter(ndb.OR(Comment.from_user_key == main.get_user_key(user), Comment.to_user_key == main.get_user_key(user))).order(Comment.add_date, Comment.key)

    @Comment.method(user_required=True, name="comment.insert", path="comment/insert", http_method="POST")
    def comment_insert(self, comment):
        """ Update or insert a new comment """
        if comment.from_datastore:
            comment_with_parent = comment
        else:
            user = endpoints.get_current_user()
            comment_with_parent = Comment(sharepoint_key=comment.sharepoint_key,
                                          message=comment.message,
                                          from_user_key=main.get_user_key(user),
                                          from_user_nickname=user.nickname(),
                                          to_user_key=comment.to_user_key,
                                          to_user_nickname=comment.to_user_nickname)
        comment_with_parent.put()
        return comment_with_parent

    @Comment.method(user_required=True, response_fields=("entityKey",), name="comment.delete",
                    path="comment/delete/{entityKey}", http_method="DELETE")
    def comment_delete(self, comment):
        """Delete the comment with the entityKey """
        if not comment.from_datastore:
            raise endpoints.NotFoundException("No comment for the given key")
        user = endpoints.get_current_user()
        if comment.from_user_key != main.get_user_key(user):
            return Comment(message="DO_NOT_HAVE_ACCESS")
        comment.key.delete()
        return Comment()
app = endpoints.api_server([SharepointViewerApi], restricted=False)
