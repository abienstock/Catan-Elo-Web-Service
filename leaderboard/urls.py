from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^results/(?P<game_id>[0-9]+)/$', views.game_results, name='game_results'),
    url(r'^new_game/$', views.new_game, name='new_game'),
    url(r'^add_game/$', views.add_game, name='add_game'),
    url(r'^edit_game/(?P<game_id>[0-9]+)/$', views.edit_game, name='edit_game'),
    url(r'^new_player/$', views.new_player, name='new_player'),
    url(r'^add_player/$', views.add_player, name='add_player'),
    url(r'^games/$', views.games, name='games'),
    url(r'^player_stats/(?P<player_name>[a-zA-Z]+)/$', views.player_stats, name='player_stats'),
    url(r'^player_stats/$', views.player_stats_main, name="player_stats_main")
]