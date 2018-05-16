import math

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse

from .models import Game, Player, PlayerInGame

def index(request):
	players = Player.objects.order_by('-elo')
	context = {'players': players}
	return render(request, 'leaderboard/index.html', context)

def games(request):
	games = Game.objects.all()
	context = {'games': games}
	return render(request, 'leaderboard/games.html', context)

def new_player(request):
	return render(request, 'leaderboard/new_player.html')

def add_player(request):
	pname = request.POST['player_name']
	p = Player(player_name = pname)
	p.save()
	return HttpResponseRedirect(reverse('new_game'))

def game_results(request, game_id):
	game = get_object_or_404(Game, pk=game_id)
	return render(request, 'leaderboard/game.html', {'game': game})

def new_game(request):
	players = Player.objects.all()
	context = {'players': players}
	return render(request, 'leaderboard/new_game.html', context)

def player_stats(request, player_name):
	player = Player.objects.filter(player_name=player_name)
	if not player.exists():
		raise Http404("Player does not exist")
	games = PlayerInGame.objects.filter(player__player_name=player_name)
	return render(request, 'leaderboard/player_stats.html', {'games': games, 'player': player})

def calc_expected(elo_a, elo_b):
	return 1.0 / (1.0 + 10.0 ** ((elo_b-elo_a)/400.0))

def calc_elo(exp, score, margin, k=32.0):
	return k * math.log(math.fabs(margin) + 1) * (score - exp)

def new_elo(elo_a, elo_b, score_a, score_b):
	# returns new elo rating of player A
	if score_a > score_b:
		return calc_elo(calc_expected(elo_a, elo_b), 1.0, score_a - score_b)
	elif score_a == score_b:
		return calc_elo(calc_expected(elo_a, elo_b), 0.5, score_a - score_b)
	else:
		return calc_elo(calc_expected(elo_a, elo_b), 0.0, score_a - score_b)

def update_ratings(elo_info):
	num_players = len(elo_info)
	i = 0
	while i < num_players:
		j = i + 1
		while j < num_players:
			elo_info[i][0].elo = elo_info[i][0].elo + new_elo(elo_info[i][1], elo_info[j][1], int(elo_info[i][2]), int(elo_info[j][2]))
			elo_info[j][0].elo = elo_info[j][0].elo + new_elo(elo_info[j][1], elo_info[i][1], int(elo_info[j][2]), int(elo_info[i][2]))
			elo_info[i][0].save()
			elo_info[j][0].save()
			j += 1
		i += 1

def add_player_to_game(game, pname, pscore):
	p = Player.objects.filter(player_name=pname)
	if not p.exists():
		p = Player(player_name = pname)
		p.save()
	else:
		p = p.first()
	pig = PlayerInGame(game = game, player = p, score = pscore)
	pig.save()
	return p;

def add_game(request):
	g = Game(played_date=timezone.now())
	g.save()

	elo_info = []

	for i in range(5):
		pname = request.POST['player_name'+str(i)]
		pscore = request.POST['player_score'+str(i)]
		if (i < 2 or (pname != "None" and pscore != "None")):
			p = add_player_to_game(g, pname, pscore)
			elo_info.append((p, p.elo, pscore))

	update_ratings(elo_info)

	return HttpResponseRedirect(reverse('game_results', args=(g.id,)))
