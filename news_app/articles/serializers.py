from news_app.articles.models import Edition, Article
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'source',
            'title',
            'description',
            'url',
            'publish_date',
            'edition'
        ]
        read_only_fields = [
            'source',
            'title',
            'description',
            'url',
            'publish_date',
            'edition'
        ]


class EditionSerializer(serializers.ModelSerializer):
    feed = serializers.SerializerMethodField()

    class Meta:
        model = Edition
        fields = ['display_name', 'refreshed', 'feed']
        read_only_fields = ['display_name', 'refreshed', 'feed']

    def get_feed(self, obj):
        return ArticleSerializer(
            obj.articles(),
            many=True
        ).data

