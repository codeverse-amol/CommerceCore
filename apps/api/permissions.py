from rest_framework.permissions import BasePermission



class ReadOnlyPermission(BasePermission):
    """
    Allow only GET, HEAD and OPTIONS.
    """

    def has_permission(self, request, view):
        return request.method in ["GET", "HEAD", "OPTIONS"]
    

class OnlyPostPermission(BasePermission):

    def has_permission(self, request, view):
        return request.method == "POST"