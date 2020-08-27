from django.db import models
from django_countries.fields import CountryField
from requests import get
from django.conf import settings
from dateutil import parser
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup

TOP_HEADLINES = "top-headlines"
EVERYTHING = "everything"

QUERY_TYPE_CHOICES = [
    (TOP_HEADLINES, "Top Headlines"),
    (EVERYTHING, "Everything"),
]

QUERY_TYPE_DICT = { k:v for k,v in QUERY_TYPE_CHOICES }

LANGUAGE_CHOICES = [
    ("ar", "Arabic"),
    ("de", "German"),
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("he", "Hebrew"),
    ("it", "Italian"),
    ("nl", "Dutch"),
    ("no", "Norwegian"),
    ("pt", "Portuguese"),
    ("ru", "Russia"),
    ("se", "Swedish"),
    ("zh", "Chinese")
]

LANGUAGE_DICT = { k:v for k,v in LANGUAGE_CHOICES }


class NewsAPIQuery(models.Model):
    keyword = models.CharField(max_length=50, null=True, blank=True)
    country = CountryField(blank=True)
    category = models.CharField(max_length=20, null=True, blank=True)
    sources = models.CharField(max_length=200, null=True, blank=True)
    query_type = models.CharField(
        max_length = 13,
        choices = QUERY_TYPE_CHOICES,
        default = TOP_HEADLINES
    )
    language = models.CharField(
        max_length=2,
        choices = LANGUAGE_CHOICES,
        null=True,
        blank=True
    )

    def base_api_url(self):
        return "https://newsapi.org/v2/{}".format(self.query_type)

    def params(self):
        params = {
            "q": self.keyword,
            "country":  self.country.code if self.country.code != "" else None,
            "sources": self.sources,
            "category": self.category,
            "language": self.language
        }
        return { k: v for k,v in params.items() if v != None}

    def get_results(self):
        response = get(
            self.base_api_url(),
            params = self.params(),
            headers = { "X-Api-Key": settings.NEWS_API_KEY }
                "url" = article["url"],
        )
        return response.json()

    def fetch_and_save_new_articles(self):
        for article in self.get_results()["articles"]:
            Article.objects.get_or_create(
                url = article["url"],
                defaults = {
                    "source" : article["source"]["name"],
                    "title" : article["title"],
                    "description" : article["description"] or "",
                    "publish_date" : parser.isoparse(article["publishedAt"])
                }
            )

    def __str__(self):
        repr = "{}".format(QUERY_TYPE_DICT[self.query_type])
        if self.country.code != "":
            repr += " in {}".format(self.country.name)

        if self.keyword != None:
            repr += " with keyword '{}'".format(self.keyword)

        if self.category != None:
            repr += " in category '{}'".format(self.category)

        if self.sources != None:
            repr += " from sources '{}'".format(self.sources)

        if self.language != None:
            repr += " in {}".format(LANGUAGE_DICT[self.language])

        return repr

class RSSFeed(models.Model):
    display_name = models.CharField(max_length = 100)
    url = models.URLField(
        max_length=300
    )

    def fetch_and_save_new_articles(self):
        feed = feedparser.parse(self.url)
        for entry in feed.entries:
            Article.objects.update_or_create(
                url = entry['link'],
                defaults= {
                    "source" : self.display_name,
                    "title" : entry['title'],
                    "description":  BeautifulSoup(entry['description']).text,
                    "url" : entry['link'],
                    "publish_date" : datetime(*entry['published_parsed'][:6])
                }
            )

    def __str__(self):
        return self.display_name

class Article(models.Model):
    source = models.CharField(max_length= 50)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    url = models.URLField(
        max_length = 500
    )
    publish_date = models.DateTimeField()

    def __str__(self):
        return self.title
