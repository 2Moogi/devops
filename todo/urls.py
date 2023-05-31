from django.urls import path
from todo.views import TodoAPIView, ColorPriorityView, ColorView, PriorityNameView

urlpatterns = [
    path("todo/", TodoAPIView.as_view()),
    path("todo/<int:pk>/", TodoAPIView.as_view()),
    path("color/", ColorView.as_view()),
    path("color/priority/", ColorPriorityView.as_view()),
    path("name/priority/", PriorityNameView.as_view()),
]

