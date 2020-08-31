from django.contrib import admin

from news_app.articles.models import (
    NewsAPIQuery,
    Article,
    RSSFeed,
    Edition
)

# Register your models here.

admin.site.register(NewsAPIQuery)
admin.site.register(Article)
admin.site.register(RSSFeed)
admin.site.register(Edition)
