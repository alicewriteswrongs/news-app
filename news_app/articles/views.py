from django.http import Http404
from django.shortcuts import render
from news_app.articles.models import Edition
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from news_app.articles.serializers import EditionSerializer, ArticleSerializer
from rest_framework.decorators import action


class EditionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Edition.objects.all()
    serializer_class = EditionSerializer
    permission_classes = [permissions.AllowAny]

    @action(methods=["GET"], detail=True)
    def refresh(self, request, pk=None):
        try:
            edition = Edition.objects.get(id=pk)
        except Edition.DoesNotExist:
            return Response({ error: "not found"}, status=status.HTTP_400_BAD_REQUEST)
        feed = edition.refresh()
        data = ArticleSerializer(
            feed,
            many=True
        ).data
        return Response({ "feed": data, "refreshed": edition.refreshed })


def edition_detail(request, edition_id):
    try:
        edition = Edition.objects.get(id=edition_id)
    except Edition.DoesNotExist:
        raise Http404("Edition does not exist")

    return render(
        request,
        "articles/edition.html",
        {"edition": edition }
    )
