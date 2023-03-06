from django.contrib import admin
from .models import Author, Category, Post, Comment, Like, CommentLike, Rating, Dislike, CommentDislike, PostView, Theme
# Register your models here.


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(CommentLike)
admin.site.register(Like)
admin.site.register(Rating)
admin.site.register(Dislike)
admin.site.register(CommentDislike)
admin.site.register(PostView)
admin.site.register(Theme)