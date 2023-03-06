from django.shortcuts import render, get_object_or_404, HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view

from .models import Author, Category, Post, Comment, Like, CommentLike, Dislike, Rating, CommentDislike, PostView, Theme
from .serializers import (
    AuthorSerializer, 
    CategorySerializer, 
    PostSerializer, 
    CommentSerializer,
    LikeSerializer,
    DislikeSerializer,
    CommentLikeSerializer,
    RatingSerializer,
    CommentDislikeSerializer,
    ThemeSerializer
    )



# Create your views here.


class AuthorMVS(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class= AuthorSerializer

class CategoryMVS(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class= CategorySerializer

class PostMVS(ModelViewSet):
    queryset = Post.objects.all().select_related('category')
    serializer_class= PostSerializer
    parser_classes = [MultiPartParser, FormParser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
       
        view_qs = PostView.objects.filter(user=request.user, post=instance)
        if not view_qs.exists():
            PostView.objects.create(post=instance,user=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #print(serializer.validated_data)
        current_user = self.request.user
        serializer.validated_data['author_id'] = current_user.id
        #print(serializer.validated_data)
        self.perform_create(serializer)
        return HttpResponse('sdsdlkfsdfs')
        #headers = self.get_success_headers(serializer.data)
        #return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        category_id = self.kwargs.get('category_pk')
        if category_id == None:
            return Post.objects.all()
        else:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise NotFound('A category with this id does not exist')
            return self.queryset.filter(category=category, is_published=True)
        
@api_view(['GET'])
def favourite_add(request, id):
    post = get_object_or_404(Post, id=id)
    if post.favourites.filter(id=request.user.id).exists():
        post.favourites.remove(request.user)
    else:
        post.favourites.add(request.user)
    return Response('success')

class AuthorPostMVS(ModelViewSet):
    queryset = Post.objects.all().select_related('category')
    serializer_class= PostSerializer
    parser_classes = [MultiPartParser, FormParser]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset.filter(author_id=self.request.user.id)
        
class CommentMVS(ModelViewSet):
    queryset = Comment.objects.all().select_related('post')
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        post_id = self.kwargs.get('post_pk')
        comment = Comment.objects.filter(post_id=post_id, commentor_id=current_user.id)
        if comment.exists():
            raise ValidationError(f'{current_user} is commented before!')
        else:
            post_id = self.kwargs.get('post_pk')
            serializer.validated_data['commentor_id'] = current_user.id
            serializer.validated_data['post_id'] = post_id
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id == None:
            return self.queryset
        else:
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFound('A post with this id does not exist.')
            return self.queryset.filter(post=post)

class LikeMVS(ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        post_id = self.kwargs.get('post_pk')
        like = Like.objects.filter(post_id=post_id, liker_id=current_user.id)
        if like.exists():
            return Response(serializer.data)
        else:
            post_id = self.kwargs.get('post_pk')
            serializer.validated_data['liker_id'] = current_user.id
            serializer.validated_data['post_id'] = post_id
            serializer.validated_data['is_liked'] = True
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        if self.request.user.id == instance.liker.id:
            if instance.is_liked == True:
                serializer.validated_data['is_liked'] = False
            else:
                serializer.validated_data['is_liked'] = True
        
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id == None:
            return self.queryset
        else:
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFound('A post with this id does not exist.')
            return self.queryset.filter(post=post)
            
class DislikeMVS(ModelViewSet):
    queryset = Dislike.objects.all()
    serializer_class = DislikeSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        post_id = self.kwargs.get('post_pk')
        dislike = Dislike.objects.filter(post_id=post_id, liker_id=current_user.id)
        if dislike.exists():
            return Response(serializer.data)
        else:
            post_id = self.kwargs.get('post_pk')
            serializer.validated_data['liker_id'] = current_user.id
            serializer.validated_data['post_id'] = post_id
            serializer.validated_data['is_disliked'] = True
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        if self.request.user.id == instance.liker.id:
            if instance.is_disliked == True:
                serializer.validated_data['is_disliked'] = False
            else:
                serializer.validated_data['is_disliked'] = True
        
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id == None:
            return self.queryset
        else:
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFound('A post with this id does not exist.')
            return self.queryset.filter(post=post)

class RatingMVS(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id == None:
            return self.queryset
        else:
            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                raise NotFound('A post with this id does not exist.')
            return self.queryset.filter(post=post)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        post_id = self.kwargs.get('post_pk')
        rating = Rating.objects.filter(post_id=post_id, rater_id=current_user.id)
        
        if rating.exists():
            raise ValidationError(f'{current_user} is rated before!')
        else:
            post_id = self.kwargs.get('post_pk')
            serializer.validated_data['rater_id'] = current_user.id
            serializer.validated_data['post_id'] = post_id
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CommentLikeMVS(ModelViewSet):
    queryset = CommentLike.objects.all().select_related('comment')
    serializer_class = CommentLikeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        comment_id = self.kwargs.get('comment_pk')
        comment_like = CommentLike.objects.filter(comment_id=comment_id, liker_id=current_user.id)
        if comment_like.exists():
            return Response(serializer.data)
        else:
            comment_id = self.kwargs.get('comment_pk')
            serializer.validated_data['liker_id'] = current_user.id
            serializer.validated_data['comment_id'] = comment_id
            serializer.validated_data['is_liked'] = True
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if self.request.user.id == instance.liker.id:
            if instance.is_liked == True:
                serializer.validated_data['is_liked'] = False
            else:
                serializer.validated_data['is_liked'] = True
        
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        comment_id = self.kwargs.get('comment_pk')
        if comment_id == None:
            return self.queryset
        else:
            try:
                comment = Comment.objects.get(id=comment_id)
            except Comment.DoesNotExist:
                raise NotFound('A Comment with this id does not exist.')
            return self.queryset.filter(comment=comment)
        
class CommentDislikeMVS(ModelViewSet):
    queryset = CommentDislike.objects.all().select_related('comment')
    serializer_class = CommentDislikeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        comment_id = self.kwargs.get('comment_pk')
        comment_dislike = CommentDislike.objects.filter(comment_id=comment_id, liker_id=current_user.id)
        if comment_dislike.exists():
            return Response(serializer.data)
        else:
            comment_id = self.kwargs.get('comment_pk')
            serializer.validated_data['liker_id'] = current_user.id
            serializer.validated_data['comment_id'] = comment_id
            serializer.validated_data['is_disliked'] = True
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if self.request.user.id == instance.liker.id:
            if instance.is_disliked == True:
                serializer.validated_data['is_disliked'] = False
            else:
                serializer.validated_data['is_disliked'] = True
        
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        comment_id = self.kwargs.get('comment_pk')
        if comment_id == None:
            return self.queryset
        else:
            try:
                comment = Comment.objects.get(id=comment_id)
            except Comment.DoesNotExist:
                raise NotFound('A Comment with this id does not exist.')
            return self.queryset.filter(comment=comment)

class ThemeMVS(ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = self.request.user
        serializer.validated_data['theme_owner_id'] = current_user.id
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    