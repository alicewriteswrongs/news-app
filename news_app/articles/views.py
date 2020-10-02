from django.http import Http404
from django.shortcuts import render
from news_app.articles.models import Edition
from rest_framework import viewsets
from rest_framework import permissions
from news_app.articles.serializers import EditionSerializer


class EditionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Edition.objects.all()
    serializer_class = EditionSerializer
    permission_classes = [permissions.AllowAny]


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
