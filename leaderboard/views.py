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
	players = Player.objects.all()
	context = {'players': players}
	return render(request, 'leaderboard/new_game.html', context)
	#return HttpResponseRedirect(reverse('new_game', args=(players)))	

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

def calc_expected(A, B):
	return 1.0 / (1.0 + 10.0 ** ((B-A)/400.0))

def calc_elo(exp, score, k=32.0):
	return k * (score - exp)

def new_elo(A, B, score):
	# returns new elo rating of player A
	return calc_elo(calc_expected(A, B), score)

def update_ratings(elo_info):
	num_players = len(elo_info)
	i = 0
	while i < num_players:
		j = i + 1
		while j < num_players:
			if int(elo_info[i][2]) > int(elo_info[j][2]):
				elo_info[i][0].elo = elo_info[i][0].elo + new_elo(elo_info[i][1], elo_info[j][1], 1.0)
				elo_info[j][0].elo = elo_info[j][0].elo + new_elo(elo_info[j][1], elo_info[i][1], 0.0)
			elif int(elo_info[i][2]) == int(elo_info[j][2]):
				elo_info[i][0].elo = elo_info[i][0].elo + new_elo(elo_info[i][1], elo_info[j][1], 0.5)
				elo_info[j][0].elo = elo_info[j][0].elo + new_elo(elo_info[j][1], elo_info[i][1], 0.5)
			else:
				elo_info[i][0].elo = elo_info[i][0].elo + new_elo(elo_info[i][1], elo_info[j][1], 0.0)
				elo_info[j][0].elo = elo_info[j][0].elo + new_elo(elo_info[j][1], elo_info[i][1], 1.0)
			elo_info[i][0].save()
			elo_info[j][0].save()
			j += 1
		i += 1

def add_game(request):
	g = Game(played_date=timezone.now())
	g.save()

	elo_info = []

	pname = request.POST['player_name1']
	pscore = request.POST['player_score1']
	p1 = Player.objects.filter(player_name=pname)
	if not p1.exists():
		p1 = Player(player_name = pname)
		p1.save()
	else:
		p1 = p1.first()
	pig1 = PlayerInGame(game = g, player = p1, score = pscore)
	pig1.save()
	elo_info.append((p1, p1.elo, pscore))

	pname = request.POST['player_name2']
	pscore = request.POST['player_score2']
	p2 = Player.objects.filter(player_name=pname)
	if not p2.exists():
		p2 = Player(player_name = pname)
		p2.save()
	else:
		p2 = p2.first()		
	pig2 = PlayerInGame(game = g, player = p2, score = pscore)
	pig2.save()
	elo_info.append((p2, p2.elo, pscore))

	pname = request.POST['player_name3']
	pscore = request.POST['player_score3']
	if (pname != "None" and pscore != ""):
		p3 = Player.objects.filter(player_name=pname)
		if not p3.exists():
			p3 = Player(player_name = pname)
			p3.save()
		else:
			p3 = p3.first()					
		pig3 = PlayerInGame(game = g, player = p3, score = pscore)
		pig3.save()
		elo_info.append((p3, p3.elo, pscore))

	pname = request.POST['player_name4']
	pscore = request.POST['player_score4']
	if (pname != "None" and pscore != ""):
		p4 = Player.objects.filter(player_name=pname)
		if not p4.exists():
			p4 = Player(player_name = pname)
			p4.save()
		else:
			p4 = p4.first()								
		pig4 = PlayerInGame(game = g, player = p4, score = pscore)
		pig4.save()
		elo_info.append((p4, p4.elo, pscore))

	pname = request.POST['player_name5']
	pscore = request.POST['player_score5']
	if (pname != "None" and pscore != ""):	
		p5 = Player.objects.filter(player_name=pname)
		if not p5.exists():
			p5 = Player(player_name = pname)
			p5.save()
		else:
			p5 = p5.first()								
		pig5 = PlayerInGame(game = g, player = p5, score = pscore)
		pig5.save()
		elo_info.append((p5, p5.elo, pscore))

	update_ratings(elo_info)

	return HttpResponseRedirect(reverse('game_results', args=(g.id,)))
