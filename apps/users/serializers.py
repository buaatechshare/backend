# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# third-party packges

# my-own packages
from .models import UserProfile,Message,Follow

class UserRegSerializer(serializers.ModelSerializer):
    name = serializers.CharField(label='用户名',required=True,allow_blank=False)
    password = serializers.CharField(
        style={'input_type':'password'},label='密码',
        write_only=True,required=True,
    )
    email = serializers.EmailField(required=True,allow_blank=False,
                                   validators=[UniqueValidator(queryset=UserProfile.objects.all(),message='该邮箱已注册')])
    phone = serializers.CharField(required=True,allow_blank=False,validators=[UniqueValidator(queryset=UserProfile.objects.all(),message='该手机号已注册')])

    def create(self, validated_data):
        user = super(UserRegSerializer,self).create(validated_data=validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, attrs):
        attrs['username'] = attrs['email']
        return attrs

    class Meta:
        model = UserProfile
        fields = ('email','name','phone','password')

class MessageSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = ('senderID','receiverID','content','add_time')

class FollowSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'
