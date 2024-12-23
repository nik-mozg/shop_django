from django.utils.html import escape
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone", "avatar"]

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            return {
                "src": (
                    request.build_absolute_uri(obj.avatar.url)
                    if request
                    else obj.avatar.url
                ),
                "alt": escape(obj.fullName) if obj.fullName else "User avatar",
            }
        return None
