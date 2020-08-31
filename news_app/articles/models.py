from django.db import models
from django_countries.fields import CountryField
from requests import get
from django.conf import settings
from dateutil import parser
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup

from news_app.articles.util import truncate

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

class Edition(models.Model):
    display_name = models.CharField(max_length=100)
    refreshed = models.DateTimeField()

    def __str__(self):
        return self.display_name

    def refresh(self):
        for query in NewsAPIQuery.objects.filter(edition=self):
            query.fetch_and_save_new_articles()

        for feed in RSSFeed.objects.filter(edition=self):
            feed.fetch_and_save_new_articles()

        self.refreshed = datetime.now()
        self.save()
        return self.feed()

    def feed(self):
        query = Article.objects.filter(
            edition=self
        ).order_by('-publish_date')
        return list(query)


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
    edition = models.ForeignKey(
        Edition,
        on_delete=models.CASCADE,
        null=True
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
        )
        return response.json()

    def fetch_and_save_new_articles(self):
        for article in self.get_results()["articles"]:
            Article.objects.get_or_create(
                url = article["url"],
                defaults = {
                    "source" : article["source"]["name"],
                    "title" : truncate(article["title"], 200),
                    "description":  truncate(article["description"] or "", 300),
                    "publish_date" : parser.isoparse(article["publishedAt"]),
                    "edition": self.edition
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
    edition = models.ForeignKey(
        Edition,
        on_delete=models.CASCADE,
        null=True
    )

    def parse_feed(self):
        feed = feedparser.parse(self.url)
        return feed

    def fetch_and_save_new_articles(self):
        feed = self.parse_feed()
        for entry in feed.entries:
            date = entry.get('published_parsed')
            if date is None:
                date = entry.get('updated_parsed')

            text = BeautifulSoup(
                entry['description'],
                features="html.parser"
            ).text

            Article.objects.update_or_create(
                url = entry['link'],
                defaults= {
                    "source" : self.display_name,
                    "title" : truncate(entry['title'], 200),
                    "description":  truncate(text, 300),
                    "url" : entry['link'],
                    "publish_date" : datetime(*date[:6]),
                    "edition": self.edition
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
    edition = models.ForeignKey(
        Edition,
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.title
