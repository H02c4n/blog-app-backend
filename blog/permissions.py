from rest_framework import permissions



class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.blog_author

class IsCommentorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or 
            request.user == obj.commentor
            )