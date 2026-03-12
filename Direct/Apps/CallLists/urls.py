from django.urls import path

from .views import RandomListCallView, CommentsRandomList, FileUploadRandomTest

app_name = "CallList"

urlpatterns = [
    path("random-test/", RandomListCallView.as_view(), name="random-test"),
    path("random-list-filter/<str:table>/", RandomListCallView.as_view(), name="random-list-export"),
    path("random-list-export/", RandomListCallView.as_view(), name="random-list-export"),
    path("random-test-file/<int:detail_randomlist_id>/", FileUploadRandomTest.as_view(), name="random-test-file"),
    path("comments-random-test/<int:detail_randomlist_id>/", CommentsRandomList.as_view(), name="comments-random-test"),
    path("comment-random-test/", CommentsRandomList.as_view(), name="comment-random-test"),
    path("comment-random-test/<int:id>/", CommentsRandomList.as_view(), name="comment-random-test")
]
