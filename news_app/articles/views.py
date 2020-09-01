from django.http import Http404
from django.shortcuts import render
from news_app.articles.models import Edition

def edition_detail(request, edition_id):
    try:
        edition = Edition.objects.get(id=edition_id)
    except Edition.DoesNotExist:
        raise Http404("Edition does not exist")

    articles = edition.feed()
    return render(
        request,
        "articles/edition.html",
        {"articles": articles, "edition": edition }
    )
