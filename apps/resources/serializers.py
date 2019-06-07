# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator

# third-party packges

# my-own packages
from .models import Comment,Collection,PaperCheckForm
from users.serializers import UserInMessageSerializer


class CollectionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('userID','resourceID')

class PaperGetSerializer(serializers.Serializer):
    paperName = serializers.CharField(max_length=255)
    abstract = serializers.CharField(max_length=1000)
    paperID = serializers.CharField(max_length=255)
    author = serializers.ListField()
    authorID = serializers.ListField()

class PatentGetSerializer(serializers.Serializer):
    patentName = serializers.CharField(max_length=255)
    rightHolder = serializers.CharField(max_length=255)
    summary = serializers.CharField(max_length=1000)
    patentID = serializers.CharField(max_length=255)

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

class PaperCheckPostSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)
    class Meta:
        model = PaperCheckForm
        fields = ('userID','title','author','doi','abstract','file','add_time')

class PaperCheckFormSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    add_time = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = PaperCheckForm
        fields = '__all__'
