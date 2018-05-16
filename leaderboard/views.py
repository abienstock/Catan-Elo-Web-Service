from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse

from .models import Game, Player, PlayerInGame

def index(request):
	latest_game_list = Game.objects.order_by('-played_date')[:5]
	context = {'latest_game_list': latest_game_list}
	return render(request, 'leaderboard/index.html', context)

def game_results(request, game_id):
	game = get_object_or_404(Game, pk=game_id)
	return render(request, 'leaderboard/game.html', {'game': game})

def new_game(request):
	return render(request, 'leaderboard/new_game.html')

def player_stats(request, player_name):
	player = Player.objects.filter(player_name=player_name)
	if not player.exists():
		raise Http404("Player does not exist")
	games = PlayerInGame.objects.filter(player__player_name=player_name)
	return render(request, 'leaderboard/player_stats.html', {'games': games, 'player': player})

def add_game(request):
	g = Game(played_date=timezone.now())
	g.save()

	pname = request.POST['player_name1']
	p1 = Player.objects.filter(player_name=pname)
	if not p1.exists():
		p1 = Player(player_name = pname)
		p1.save()
	else:
		p1 = p1.first()
	pig1 = PlayerInGame(game = g, player = p1, score = request.POST['player_score1'])
	pig1.save()

	pname = request.POST['player_name2']
	p2 = Player.objects.filter(player_name=pname)
	if not p2.exists():
		p2 = Player(player_name = pname)
		p2.save()
	else:
		p2 = p2.first()		
	pig2 = PlayerInGame(game = g, player = p2, score = request.POST['player_score2'])
	pig2.save()

	pname = request.POST['player_name3']
	pscore = request.POST['player_score3']
	if (pname != "" and pscore != ""):
		p3 = Player.objects.filter(player_name=pname)
		if not p3.exists():
			p3 = Player(player_name = pname)
			p3.save()
		else:
			p3 = p3.first()					
		pig3 = PlayerInGame(game = g, player = p3, score = pscore)
		pig3.save()

	pname = request.POST['player_name4']
	pscore = request.POST['player_score4']
	if (pname != "" and pscore != ""):
		p4 = Player.objects.filter(player_name=pname)
		if not p4.exists():
			p4 = Player(player_name = pname)
			p4.save()
		else:
			p4 = p4.first()								
		pig4 = PlayerInGame(game = g, player = p4, score = pscore)
		pig4.save()

	pname = request.POST['player_name5']
	pscore = request.POST['player_score5']
	if (pname != "" and pscore != ""):	
		p5 = Player.objects.filter(player_name=pname)
		if not p5.exists():
			p5 = Player(player_name = pname)
			p5.save()
		else:
			p5 = p5.first()								
		pig5 = PlayerInGame(game = g, player = p5, score = pscore)
		pig5.save()

	return HttpResponseRedirect(reverse('game_results', args=(g.id,)))
