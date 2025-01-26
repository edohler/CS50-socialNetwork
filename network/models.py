from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
	user = models.ForeignKey("User", on_delete=models.CASCADE)
	body = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)
	like = models.IntegerField(default=0, blank=True)

	def serialize(self):
		return {
			"id": self.id,
			"user": self.user.username,
			"body": self.body,
			"timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
			"like": self.like
		}

class Follow(models.Model):
	user = models.ForeignKey("User", on_delete=models.PROTECT, related_name="current_user")
	following = models.ForeignKey("User", on_delete=models.PROTECT, related_name='following_user')

	def serialize(self):
		return {
			"id": self.id,
			"user": self.user.username,
			"following": self.following.username
		}

class Like(models.Model):
	post = models.ForeignKey("Post", on_delete=models.PROTECT, related_name="post_in_like")
	user = models.ForeignKey("User", on_delete=models.PROTECT, related_name="user_in_like")

	def serialize(self):
		return {
			"id": self.id,
			"post": self.postID.id,
			"user": self.user.username,
		}
