from django.contrib import admin

from news_app.articles.models import NewsAPIQuery, Article

# Register your models here.

admin.site.register(NewsAPIQuery)
admin.site.register(Article)
