# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator

# third-party packges

# my-own packages
from .models import Comment,Collection
from users.serializers import UserInMessageSerializer


class CollectionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('userID','resourceID')

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('userID','resourceID','content','rate')

class CommentGetSerializer(serializers.ModelSerializer):
    userID = UserInMessageSerializer()
    class Meta:
        model = Comment
        fields = ('userID','content','rate','add_time')


    # commentID = models.AutoField(primary_key=True)
    # userID = models.ForeignKey(UserProfile,to_field='userID',on_delete=models.CASCADE)
    # resourceID = models.CharField(max_length=255)
    # content = models.TextField()
    # rate = models.IntegerField()
    # add_time = models.DateTimeField(default=datetime.now,)
