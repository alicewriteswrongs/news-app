from news_app.articles.models import Edition
from rest_framework import serializers


class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = ['display_name', 'refreshed', 'feed']
        read_only_fields = ['display_name', 'refreshed', 'feed']

#         def get_feed
