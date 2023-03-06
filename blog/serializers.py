from rest_framework import serializers
from django.shortcuts import get_object_or_404
import datetime

from django.contrib.auth.models import User

from requests import request


from .models import Author, Category, Post, Comment, Like, CommentLike, Rating, Dislike, CommentDislike, PostView, Theme



class AuthorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField()

    class Meta:
        model = Author
        fields ='__all__'

class CategorySerializer(serializers.ModelSerializer):
    published_post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id','name', 'published_post_count']

    def get_published_post_count(self, obj):
        return obj.posts.filter(is_published=True).count()

class LikeSerializer(serializers.ModelSerializer):

    post = serializers.StringRelatedField()
    
    liker = serializers.StringRelatedField()
    liker_id = serializers.StringRelatedField()

    class Meta:
        model = Like
        fields = ('id', 'post','liker', 'liker_id', 'is_liked')

class DislikeSerializer(serializers.ModelSerializer):

    post = serializers.StringRelatedField()
    
    liker = serializers.StringRelatedField()
    liker_id = serializers.StringRelatedField()

    class Meta:
        model = Dislike
        fields = ('id', 'post','liker', 'liker_id', 'is_disliked')

class RatingSerializer(serializers.ModelSerializer):

    post = serializers.StringRelatedField()
    rater = serializers.StringRelatedField()
    rater_id = serializers.StringRelatedField()
    class Meta:
        model = Rating
        fields = ('id', 'post', 'value','rater', 'rater_id')

class CommentLikeSerializer(serializers.ModelSerializer):

    comment = serializers.StringRelatedField()
    liker = serializers.StringRelatedField()
    liker_id = serializers.StringRelatedField()
    
    class Meta:
        model = CommentLike
        fields = ('id', 'comment', 'liker', 'liker_id', 'is_liked')

class CommentDislikeSerializer(serializers.ModelSerializer):

    comment = serializers.StringRelatedField()
    liker = serializers.StringRelatedField()
    liker_id = serializers.StringRelatedField()
    
    class Meta:
        model = CommentDislike
        fields = ('id', 'comment', 'liker', 'liker_id', 'is_disliked')

class CommentSerializer(serializers.ModelSerializer):

    commentor = serializers.StringRelatedField(read_only=True)
    commentor_id = serializers.StringRelatedField()
    post = serializers.StringRelatedField(read_only=True)
    post_id = serializers.StringRelatedField()
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()
    like_count =serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    
    
   

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'post', 'title', 'comment', 'commentor','commentor_id', 'like_count', 'dislike_count', 'created_date','updated_date']

    def get_created_date(self, obj):
        return datetime.datetime.strftime(obj.created_date, '%d,%m,%Y')

    def get_updated_date(self, obj):
        return datetime.datetime.strftime(obj.updated_date, '%d,%m,%Y')

    def get_like_count(self, obj):
        return CommentLike.objects.filter(comment_id=obj.id, is_liked=True ).count()

    def get_dislike_count(self, obj):
        return CommentDislike.objects.filter(comment_id=obj.id, is_disliked=True).count()

class PostSerializer(serializers.ModelSerializer):

    category =serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    author = serializers.StringRelatedField()
    author_id = serializers.IntegerField(read_only=True)
    created = serializers.SerializerMethodField()
    last_update = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    rate_count =serializers.SerializerMethodField()
    rate_avg = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    visit_count = serializers.SerializerMethodField()

    #bookmark = serializers.SerializerMethodField()

    comments = CommentSerializer(many=True, read_only=True)
    favourites = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'image', 'slug', 'category', 'category_id', 'author', 'author_id', 'comments_count', 'comments', 'like_count', 'dislike_count', 'visit_count', 'favourites', 'rate_count', 'rate_avg', 'is_published', 'created','last_update')

    def get_created(self, obj):
        return datetime.datetime.strftime(obj.created_date, '%d,%m,%Y')

    def get_last_update(self, obj):
        return datetime.datetime.strftime(obj.updated_date, '%d, %m, %Y')

    def get_like_count(self, obj):
        return Like.objects.filter(post_id=obj.id, is_liked=True ).count()

    def get_dislike_count(self, obj):
        return Dislike.objects.filter(post_id=obj.id, is_disliked=True).count()

    def get_comments_count(self, obj):
        return Comment.objects.filter(post_id = obj.id).count()

    def get_rate_count(self, obj):
        return Rating.objects.filter(post_id=obj.id).count()

    def get_rate_avg(self, obj):
        rates = Rating.objects.filter(post_id=obj.id)
        count = 0
        total_rate = 0
        for rate in rates:
            count +=1
            total_rate += rate.value
        avg = 0
        if count == 0:
            avg = 0
        else:
            avg = total_rate/count
        return avg.__round__(2)

    def get_visit_count(self, obj):
        return PostView.objects.filter(post=obj).count()

class ThemeSerializer(serializers.ModelSerializer):

    theme_owner = serializers.StringRelatedField()
    theme_owner_id = serializers.IntegerField(read_only=True)


    class Meta:
        model = Theme
        fields = ('id', 'theme_owner_id', 'theme_owner', 'theme_name', 'first_color', 'second_color', 'font_color', 'font_size')
