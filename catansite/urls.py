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
	url(r'^leaderboard/$', views.leaderboard, name='leaderboard'),
    url(r'^results/(?P<game_id>[0-9]+)/$', views.game_results, name='game_results'),
    url(r'^new_game/$', views.new_game, name='new_game'),
    url(r'^add_game/$', views.add_game, name='add_game'),
    url(r'^edit_game/(?P<game_id>[0-9]+)/$', views.edit_game, name='edit_game'),
    url(r'^new_player/$', views.new_player, name='new_player'),
    url(r'^add_player/$', views.add_player, name='add_player'),
    url(r'^games/$', views.games, name='games'),
    url(r'^player_stats/(?P<player_name>[a-zA-Z]+)/$', views.player_stats, name='player_stats'),
    url(r'^player_stats/$', views.player_stats_main, name="player_stats_main"),
    url(r'^admin/', admin.site.urls),
]