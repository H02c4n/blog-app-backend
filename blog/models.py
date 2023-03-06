from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django_extensions.db.fields import AutoSlugField
from PIL import Image



def rewrite_slug(content):
    return content.replace(' ', '_').lower()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name= models.CharField(max_length=40, blank=True, null=True)
    image = models.ImageField(upload_to="profile/images", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    # def save(self, *args, **kwargs):
    #     ###image resize###
    #     super().save(*args, **kwargs)
    #     if self.image:
    #         img = Image.open(self.image)
    #         if img.height > 600 or img.width>600:
    #             output_size = (300,300)
    #             img.thumbnail(output_size)
    #             img.save(self.image)

class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = AutoSlugField(populate_from='name', slugify_function=rewrite_slug)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = AutoSlugField(populate_from='title', slugify_function=rewrite_slug)
    content = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, related_name='posts')
    image = models.ImageField(upload_to="posts/images", blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    favourites = models.ManyToManyField(User, related_name='favourite', default=None, blank=True)
    is_published = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     ###image resize###
    #     super().save(*args, **kwargs)
    #     if self.image:
    #         img = Image.open(self.image)
    #         if img.height > 800 or img.width>1000:
    #             output_size = (750,400)
    #             img.thumbnail(output_size)
    #             img.save(self.image.name)
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    commentor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.post}--{self.title}'
    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='l_posts')
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.post.title}--{self.liker}'

class Dislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='d_posts')
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    is_disliked = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.post.title}--{self.liker}'

class Rating(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
        )

    def __str__(self):
        return f'{self.post}-{self.rater}-{self.value}'

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='l_comments')
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.comment.comment}--{self.liker}'

class CommentDislike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='d_comments')
    liker = models.ForeignKey(User, on_delete=models.CASCADE)
    is_disliked = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.comment.comment}--{self.liker}'

class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class Theme(models.Model):
    theme_name = models.CharField(max_length=32, blank=True, null=True)
    theme_owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='themes')
    first_color = models.CharField(max_length=7, blank=True, null=True)
    second_color = models.CharField(max_length=7, blank=True, null=True)
    font_color = models.CharField(max_length=7, blank=True, null=True)
    font_size = models.PositiveSmallIntegerField(
        validators= [MinValueValidator(16), MaxValueValidator(32)]
        )

    def __str__(self):
        return f'{self.theme_name}'
    
    