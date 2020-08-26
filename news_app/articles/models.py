from django.db import models
from django_countries.fields import CountryField
from requests import get
from django.conf import settings

TOP_HEADLINES = "top-headlines"
EVERYTHING = "everything"

QUERY_TYPE_CHOICES = [
    (TOP_HEADLINES, "Top Headlines"),
    (EVERYTHING, "Everything"),
]

QUERY_TYPE_DICT = { k:v for k,v in QUERY_TYPE_CHOICES }

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

    def base_api_url(self):
        return "https://newsapi.org/v2/{}".format(self.query_type)

    def params(self):
        params = {
            "q": self.keyword,
            "country":  self.country.code if self.country.code != "" else None,
            "sources": self.sources,
            "category": self.category
        }
        return { k: v for k,v in params.items() if v != None}

    def get_results(self):
        response = get(
            self.base_api_url(),
            params = self.params(),
            headers = { "X-Api-Key": settings.NEWS_API_KEY }
        )
        return response.json()

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

        return repr
