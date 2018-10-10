from django.conf.urls import url # This gives us access to the function url
from . import views           # connect 'views file' that is on the same level as this file
  
urlpatterns = [
    # use regex to match paths with specific functions in view.py

    url(r'^$', views.home),     #connect an empty path to the home function in views file
    url(r'^give_score$', views.give_score),     #to get original/real score
    url(r'^make_my_own$', views.make_my_own),     #to get random score
]