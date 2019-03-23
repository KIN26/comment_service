from rest_framework.generics import ListAPIView, RetrieveAPIView

from . import serializers


class PostList(ListAPIView):
    """
    List all Blogs or News
    """
    serializer_class = serializers.BlogListSerializer


class PostDetail(RetrieveAPIView):
    """
    Retrieve blog or news instance
    """
    serializer_class = serializers.BlogDetailSerializer
