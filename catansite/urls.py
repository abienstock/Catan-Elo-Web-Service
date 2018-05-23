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

from . import views

urlpatterns = [
	url(r'^$', views.landing, name='landing'),
	url(r'^(?P<league_name>[a-zA-z]+)/leaderboard/$', views.leaderboard, name='leaderboard'),
    url(r'^results/(?P<game_id>[0-9]+)/$', views.game_results, name='game_results'),
    url(r'^(?P<league_name>[a-zA-z]+)/new_game/$', views.new_game, name='new_game'),
    url(r'^(?P<league_name>[a-zA-z]+)/add_game/$', views.add_game, name='add_game'),
    url(r'^(?P<league_name>[a-zA-z]+)/edit_game/(?P<game_id>[0-9]+)/$', views.edit_game, name='edit_game'),
    url(r'^(?P<league_name>[a-zA-z]+)/games/$', views.games, name='games'),
    url(r'^(?P<league_name>[a-zA-z]+)/player_stats/$', views.player_stats_main, name='player_stats_main'),    
    url(r'^(?P<league_name>[a-zA-z]+)/player_stats/(?P<username>[a-zA-Z]+)/$', views.player_stats, name='player_stats'),
    url(r'^admin/', admin.site.urls),
    url(r'^new_account/$', views.new_acct, name='new_acct'),
    url('accounts/', include('django.contrib.auth.urls')),
    url(r'^new_league/$', views.new_league, name='new_league'),
    url(r'^add_league/$', views.add_league, name='add_league')
]