import math

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Game, UserInGame, League, UserInLeague

def landing(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('leagues'))
	else:
		return HttpResponseRedirect(reverse('login'))

def leaderboard(request, league_name):
	league = get_object_or_404(League, league_name = league_name)
	usersinleague = league.userinleague_set.order_by('-elo')
	context = {'league_name': league_name, 'usersinleague': usersinleague}
	return render(request, 'catansite/leaderboard.html', context)

def games(request, league_name):
	league = get_object_or_404(League, league_name = league_name)
	games = league.game_set.all()
	usersinleague = league.userinleague_set.all()
	context = {'league_name': league_name, 'games': games, 'usersinleague': usersinleague, 'league_name': league_name}
	return render(request, 'catansite/games.html', context)

def game_results(request, league_name, game_id):
	game = get_object_or_404(Game, pk=game_id)
	context = {'league_name': league_name, 'game': game}
	return render(request, 'catansite/game.html', context)

def new_game(request):
	user = request.user
	leagues = user.league_set.all()
	context = {'leagues': leagues}
	return render(request, 'catansite/new_game.html', context)

def new_game_in_league(request):
	league_name = request.POST['league_name']
	league = get_object_or_404(League, league_name = league_name)	
	uils = league.userinleague_set.all()
	context = {'uils': uils, 'league_name': league_name}
	return render(request, 'catansite/new_game_in_league.html', context)

def player_stats(request, league_name, username):
	league = get_object_or_404(League, league_name = league_name)
	uigs = UserInGame.objects.filter(game__league = league, uil__user__username = username)
	context = {'league_name': league_name, 'uigs': uigs, 'username': username}
	return render(request, 'catansite/player_stats.html', context)

def player_stats_main(request, league_name):
	league = get_object_or_404(League, league_name = league_name)	
	uils = league.userinleague_set.all()
	context = {'league_name': league_name, 'uils': uils, 'league_name': league_name}
	return render(request, 'catansite/player_stats_main.html', context)

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

def add_player_to_game(game, uname, uscore, league):
	uil = UserInLeague.objects.get(user__username=uname, league=league)
	uig = UserInGame(game = game, uil = uil, score = uscore)
	return uil, uig;

def add_game(request, league_name):
	league = get_object_or_404(League, league_name = league_name)
	g = Game(played_date=timezone.now(), league = league)
	g.save()	

	elo_info = []
	names = []
	uigs = []

	for i in range(5):
		uname = request.POST['username'+str(i)]
		if uname in names and uname != 'None':
			g.delete()			
			raise SuspiciousOperation("User attempted to input '%s' twice into a game." % uname)
		names.append(uname)
		uscore = request.POST['user_score'+str(i)]
		if i < 2 and (uname == 'None' or uscore == 'None'):
			g.delete()			
			raise SuspiciousOperation("Info for first two players must be completely filled in.")
		elif i < 2 or (uname != "None" or uscore != "None"):
			if uname == 'None' or uscore == 'None':
				g.delete()			
				raise SuspiciousOperation("Info for player must be completely filled in.")
			(uil, uig) = add_player_to_game(g, uname, uscore, league)
			uigs.append(uig)
			elo_info.append((uil, uil.elo, uscore))

	for uig in uigs:
		uig.save()

	update_ratings(elo_info)

	return HttpResponseRedirect(reverse('game_results', args=(league_name, g.id,)))

def recalc_elo(league):
	uils = league.userinleague_set.all()
	for uil in uils:
		uil.elo = 1500
		uil.save()

	games = league.game_set.all()
	for game in games:
		gameusers = game.useringame_set.all()
		elo_info = []
		for u in gameusers:
			uscore = u.score
			uil = u.uil
			elo_info.append((uil, uil.elo, uscore))
		update_ratings(elo_info)


def edit_game(request, league_name, game_id):
	league = get_object_or_404(League, league_name = league_name)
	g = Game.objects.get(pk=game_id)

	names = []
	uigs = []

	for i in range(5):
		uname = request.POST['username'+str(i)]
		if uname in names and uname != 'None':
			raise SuspiciousOperation("User attempted to input '%s' twice into a game." % uname)
		names.append(uname)
		uscore = request.POST['user_score'+str(i)]
		if i < 2 and (uname == 'None' or uscore == 'None'):
			raise SuspiciousOperation("Info for first two players must be completely filled in.")
		elif (i < 2 or (uname != "None" or uscore != "None")):
			if uname == 'None' or uscore == 'None':
				raise SuspiciousOperation("Info for player must be completely filled in.")
			(uil, uig) = add_player_to_game(g, uname, uscore, league)
			uigs.append(uig)

	g.uils.clear()

	for uig in uigs:
		uig.save()

	recalc_elo(league)

	return HttpResponseRedirect(reverse('game_results', args=(league_name, g.id,)))

def new_acct(request):
	users = User.objects.all()
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponse("User created successfully!")
	else:
		form = UserCreationForm()
		return render(request, 'registration/create_acct.html', {'form': form})

def new_league(request):
	return render(request, 'catansite/new_league.html')

def add_user_to_league(league, uname):
	u = User.objects.get(username=uname)
	uil = UserInLeague(league = league, user = u)
	uil.save()

def add_league(request):
	league_name = request.POST['league_name']
	if League.objects.filter(league_name = league_name).exists():
		raise SuspiciousOperation("League with name '%s' already exists." % league_name)
	l = League(league_name = league_name)
	l.save()	
	league_name = request.POST['league_name']

	names = []

	for i in range(10):
		uname = request.POST['user_name'+str(i)]
		if uname in names and uname != '':
			raise SuspiciousOperation("User attempted to input '%s' twice into a league." % uname)
		names.append(uname)
		if i < 2 and uname == '':
			raise SuspiciousOperation("Must provide at least two players.")
		elif (i < 2 or uname != ''):
			add_user_to_league(l, uname)
	return HttpResponseRedirect(reverse('leaderboard', args=(l.league_name,)))

def leagues(request):
	leagues = request.user.league_set.all()
	context = {'leagues': leagues}
	return render(request, 'catansite/leagues.html', context)
