from django.db import models
from django_countries.fields import CountryField

TOP_HEADLINES = "top-headlines"
EVERYTHING = "everything"

QUERY_TYPE_CHOICES = [
    (TOP_HEADLINES, "Top Headlines"),
    (EVERYTHING, "Everything"),
]

class NewsAPIQuery(models.Model):
    keyword = models.CharField(max_length=50, null=True, blank=True)
    country = CountryField()
    category = models.CharField(max_length=20, null=True, blank=True)
    sources = models.CharField(max_length=200, null=True, blank=True)
    query_type = models.CharField(
        max_length = 13,
        choices = QUERY_TYPE_CHOICES,
        default = TOP_HEADLINES
    )
