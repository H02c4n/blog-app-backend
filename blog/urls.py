
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import AuthorMVS, CategoryMVS, PostMVS, CommentMVS,LikeMVS, CommentLikeMVS, DislikeMVS, RatingMVS, CommentDislikeMVS, AuthorPostMVS, favourite_add, ThemeMVS

router = SimpleRouter()


#?#Single router##
router.register('author', AuthorMVS)
router.register('author-posts', AuthorPostMVS)
router.register('categories', CategoryMVS, basename='categories')
router.register('posts', PostMVS, basename='posts')
router.register('comments', CommentMVS, basename='comments')
router.register('likes', LikeMVS, basename='likes')
router.register('dislikes', DislikeMVS, basename='dislikes')
router.register('ratings', RatingMVS, basename='ratings')
router.register('themes', ThemeMVS, basename='themes')



#!#Nested router##
#?#Category base##
category_base_router = NestedSimpleRouter(router, 'categories', lookup='category')

category_base_router.register('posts', PostMVS, basename='posts')

#?#Post base##
post_base_router = NestedSimpleRouter(router, 'posts', lookup='post')

post_base_router.register('comments', CommentMVS, basename='comments')
post_base_router.register('likes', LikeMVS, basename='likes')
post_base_router.register('dislikes', DislikeMVS, basename='dislikes')
post_base_router.register('ratings', RatingMVS, basename='ratings')



comment_base_router = NestedSimpleRouter(post_base_router, 'comments', lookup='comment')

comment_base_router.register('likes', CommentLikeMVS, basename='likes')
comment_base_router.register('dislikes', CommentDislikeMVS, basename='dislikes')



urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_base_router.urls)),
    path('', include(post_base_router.urls)),
    path('', include(comment_base_router.urls)),
    path('fav/<int:id>/', favourite_add, name='favourite_add'),
]




