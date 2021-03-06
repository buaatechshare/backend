# global-site packages
from datetime import datetime

# django&restframework packges
from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator

# third-party packges

# my-own packages
from .models import UserProfile,Message,Follow,ExpertCheckForm,ExpertProfile, Fields, Tags

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name','phone','email','user_add_time','isExpert')

class UserUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        instance = super(UserUpdateSerializer,self).update(instance=instance,validated_data=validated_data)
        instance.save()
        return instance

    def validate(self, attrs):
        attrs['username'] = attrs['email']
        return attrs

    class Meta:
        model = UserProfile
        fields = ('name','email')

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

class UserInMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name','userID')

class MessageGetSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)
    senderID = UserInMessageSerializer()
    receiverID = UserInMessageSerializer()
    class Meta:
        model = Message
        fields = ('senderID','receiverID','content','add_time')

class MessagePostSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = ('senderID','receiverID','content','add_time')

class ExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertProfile
        fields = ('user','introduction','constitution','realName')

class FollowGetSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)
    followID = ExpertSerializer()
    class Meta:
        model = Follow
        fields = '__all__'

class FollowPostSerializer(serializers.ModelSerializer):
    add_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'
        validatiors = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('userID','followID'),
                message='invalid request',
            )
        ]

class ExpertApplySerializer(serializers.ModelSerializer):
    formID = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExpertCheckForm
        fields = ('expertID','formID','userID','introduction','constitution','realName')

class ExpertCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertCheckForm
        fields = '__all__'


class FieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fields
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    userID = serializers.IntegerField()
    field = serializers.IntegerField()

    class Meta:
        model = Tags
        fields = ('userID', 'field')

    #def create(self, validated_data):
    #    tag = super().create(validated_data)
    #    userID = validated_data.get('userID')
    #    field = validated_data.get('field')
    #    tag.userID = userID
    #    tag.field = field
    #    tag.save()
    #    return tag