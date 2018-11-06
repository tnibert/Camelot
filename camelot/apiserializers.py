from rest_framework import serializers
from .forms import validate_image
from .constants import MAXPHOTODESC


class PhotoUploadSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=MAXPHOTODESC)
    image = serializers.ImageField(validators=[validate_image])