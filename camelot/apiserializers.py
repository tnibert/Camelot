from rest_framework import serializers
from .forms import validate_image
from .constants import MAXPHOTODESC


class PhotoUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(validators=[validate_image])


class PhotoDescriptSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=MAXPHOTODESC)