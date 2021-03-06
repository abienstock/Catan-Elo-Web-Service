"""catansite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    url(r'^$', views.landing, name='landing'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/leaderboard/$', views.leaderboard, name='leaderboard'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/results/(?P<game_id>[0-9]+)/$', views.game_results, name='game_results'),
    url(r'^new_game/$', views.new_game, name='new_game'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/new_game/$', views.new_game, name='new_game'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/games/$', views.games, name='games'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/games/(?P<game_id>[0-9]+)/$', views.games, name='games'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/player_histories/$', views.player_histories_main, name='player_histories_main'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/player_histories/(?P<username>[a-zA-Z0-9@.+-_]+)/$', views.player_histories, name='player_histories'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/new_account/$', views.new_acct, name='new_acct'),
    url('accounts/', include('django.contrib.auth.urls')),
    url(r'^new_league/$', views.new_league, name='new_league'),
    url(r'^leagues/$', views.leagues, name='leagues'),
    url(r'^(?P<league_name>[a-zA-z0-9_ ]+)/$', views.league_home, name='league_home')
]

urlpatterns += staticfiles_urlpatterns()