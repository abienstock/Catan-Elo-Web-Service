import math

from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail

from .models import Game, UserInGame, League, UserInLeague
from .forms import SignUpForm

def landing(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('leagues'))
	else:
		return HttpResponseRedirect(reverse('login'))

def leaderboard(request, league_name):
	league = get_object_or_404(League, league_name = league_name)
	usersinleague = league.userinleague_set.order_by('-elo')
	for user in usersinleague:
		if request.user.username == user.user.username:
			context = {'league_name': league_name, 'usersinleague': usersinleague}
			return render(request, 'catansite/leaderboard.html', context)
	return HttpResponseForbidden("<h1>Forbidden (403)</h1>User '%s' is not in league '%s'." % (request.user.username, league_name))

def game_results(request, league_name, game_id):
	league = get_object_or_404(League, league_name = league_name)	
	game = get_object_or_404(Game, pk=game_id)
	usersinleague = league.userinleague_set.all()
	for user in usersinleague:
		if request.user.username == user.user.username:
			context = {'league_name': league_name, 'game': game}
			return render(request, 'catansite/game.html', context)
	return HttpResponseForbidden("<h1>Forbidden (403)</h1>User '%s' is not in league '%s'." % (request.user.username, league_name))

def player_stats(request, league_name, username):
	league = get_object_or_404(League, league_name = league_name)
	uils = league.userinleague_set.all()
	games = league.game_set.all()
	uigs = UserInGame.objects.filter(game__league = league, uil__user__username = username)
	for user in uils:
		if request.user.username == user.user.username:
			context = {'games': games, 'league_name': league_name, 'uigs': uigs, 'username': username}
			return render(request, 'catansite/player_stats.html', context)
	return HttpResponseForbidden("<h1>Forbidden (403)</h1>User '%s' is not in league '%s'." % (request.user.username, league_name))			

def player_stats_main(request, league_name):
	league = get_object_or_404(League, league_name = league_name)
	games = league.game_set.all()	
	uils = league.userinleague_set.all()
	for user in uils:
		if request.user.username == user.user.username:
			context = {'games': games, 'uils': uils, 'league_name': league_name}
			return render(request, 'catansite/player_stats_main.html', context)
	return HttpResponseForbidden("<h1>Forbidden (403)</h1>User '%s' is not in league '%s'." % (request.user.username, league_name))

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

def new_game(request, league_name = ''):
	if request.method == 'POST':
		if 'league_name' in request.POST:
			league_name = request.POST['league_name']
			league = get_object_or_404(League, league_name = league_name)	
			uils = league.userinleague_set.all()
			context = {'uils': uils, 'league_name': league_name}
			return render(request, 'catansite/new_game.html', context)
		else:
			league = get_object_or_404(League, league_name = league_name)
			time = timezone.localtime(timezone.now())
			g = Game(played_date=time, league = league)
			g.save()	

			elo_info = []
			names = []
			uigs = []
			scores = []

			for i in range(5):
				uname = request.POST['username'+str(i)]
				if uname in names and uname != 'None':
					g.delete()			
					return HttpResponseBadRequest("<h1>Bad Request (400)</h1>User attempted to input '%s' twice into a game." % uname)
				names.append(uname)
				uscore = request.POST['user_score'+str(i)]
				scores.append(uscore)
				if i < 2 and (uname == 'None' or uscore == 'None'):
					g.delete()			
					return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Info for first two players must be completely filled in.")
				elif i < 2 or (uname != "None" or uscore != "None"):
					if uname == 'None' or uscore == 'None':
						g.delete()			
						return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Info for player must be completely filled in.")
					(uil, uig) = add_player_to_game(g, uname, uscore, league)
					uigs.append(uig)
					elo_info.append((uil, uil.elo, uscore))

			if scores.count('10') != 1:
				g.delete()
				return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Exactly one Player must have 10 points.")

			for uig in uigs:
				uig.save()

			update_ratings(elo_info)

			send_new_game_mail(league_name, uigs, league.userinleague_set.all(), time)
			return HttpResponseRedirect(reverse('game_results', args=(league_name, g.id,)))
	else:
		user = request.user
		leagues = user.league_set.all()
		context = {'leagues': leagues, 'league_name': None}
		return render(request, 'catansite/new_game.html', context)

def send_new_game_mail(league_name, uigs, uils, time):
	emails = []
	for uil in uils:
		emails.append(uil.user.email)
	message_body = "A new game has been added in the league '%s' at %s:\n\n" % (league_name, time)
	for uig in uigs:
		message_body += "%s: %s\n" % (uig.uil.user.username, uig.score)
	message_body += "\nThe updated elo ratings are:\n\n"
	for uil in uils:
		elo = float(uil.elo)
		message_body += "%s: %.2f\n" % (uil.user.username, elo)
	send_mail(
		"Catansite New Game",
		message_body,
		'catansite@gmail.com',
		emails,
		fail_silently = False,
	)

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

def games(request, league_name, game_id = 0):
	if request.method == 'POST':
		league = get_object_or_404(League, league_name = league_name)
		g = Game.objects.get(pk=game_id)

		old_scores = []
		old_uigs = g.useringame_set.all()
		for uig in old_uigs:
			old_scores.append((uig.uil.user.username, uig.score))

		names = []
		uigs = []
		scores = []

		for i in range(5):
			uname = request.POST['username'+str(i)]
			if uname in names and uname != 'None':
				return HttpResponseBadRequest("<h1>Bad Request (400)</h1>User attempted to input '%s' twice into a game." % uname)
			names.append(uname)
			uscore = request.POST['user_score'+str(i)]
			scores.append(uscore)
			if i < 2 and (uname == 'None' or uscore == 'None'):
				return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Info for first two players must be completely filled in.")
			elif (i < 2 or (uname != "None" or uscore != "None")):
				if uname == 'None' or uscore == 'None':
					return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Info for player must be completely filled in.")
				(uil, uig) = add_player_to_game(g, uname, uscore, league)
				uigs.append(uig)

		if scores.count('10') != 1:
				return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Exactly one Player must have 10 points.")

		g.uils.clear()

		for uig in uigs:
			uig.save()

		recalc_elo(league)

		send_edited_game_mail(league_name, uigs, league.userinleague_set.all(), timezone.localtime(g.played_date), old_scores)
		return HttpResponseRedirect(reverse('games', args=(league_name,)))
	else:
		league = get_object_or_404(League, league_name = league_name)
		games = league.game_set.all()
		usersinleague = league.userinleague_set.all()
		for user in usersinleague:
			if request.user.username == user.user.username:
				context = {'league_name': league_name, 'games': games, 'usersinleague': usersinleague, 'league_name': league_name}
				return render(request, 'catansite/games.html', context)
		return HttpResponseForbidden("<h1>Forbidden (403)</h1>User '%s' is not in league '%s'." % (request.user.username, league_name))

def send_edited_game_mail(league_name, uigs, uils, time, old_scores):
	emails = []
	for uil in uils:
		emails.append(uil.user.email)
	message_body = "The game in the league '%s', played at %s, has been updated.\n\nOld Scores:\n\n" % (league_name, time)
	for score in old_scores:
		message_body += "%s: %s\n" % (score[0], score[1])
	message_body += "\nNew scores:\n\n"
	for uig in uigs:
		message_body += "%s: %s\n" % (uig.uil.user.username, uig.score)
	message_body += "\nThe updated elo ratings are:\n\n"
	for uil in uils:
		elo = float(uil.elo)
		message_body += "%s: %.2f\n" % (uil.user.username, elo)
	send_mail(
		"Catansite Updated Game",
		message_body,
		'catansite@gmail.com',
		emails,
		fail_silently = False,
	)

def new_acct(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return HttpResponseRedirect(reverse('leagues'))
	else:
		form = SignUpForm()
	return render(request, 'registration/create_acct.html', {'form': form})

def new_league(request):
	if request.method == 'POST':
		league_name = request.POST['league_name']
		if League.objects.filter(league_name = league_name).exists():
			return HttpResponseBadRequest("<h1>Bad Request (400)</h1>League with name '%s' already exists." % league_name)
		l = League(league_name = league_name)
		l.save()	
		league_name = request.POST['league_name']

		names = []

		for i in range(10):
			uname = request.POST['user_name'+str(i)]
			if uname in names and uname != '':
				l.delete()
				return HttpResponseBadRequest("<h1>Bad Request (400)</h1>User attempted to input '%s' twice into a league." % uname)
			names.append(uname)
			if i < 2 and uname == '':
				l.delete()
				return HttpResponseBadRequest("<h1>Bad Request (400)</h1>Must provide at least two players.")
			elif (i < 2 or uname != ''):
				try:
					add_user_to_league(l, uname)
				except:
					l.delete()
					return HttpResponseBadRequest("<h1>Bad Request (400)</h1>User '%s' does not exist." % uname)
		send_league_mail(names, league_name)
		return HttpResponseRedirect(reverse('leaderboard', args=(l.league_name,)))
	else:
		return render(request, 'catansite/new_league.html')

def send_league_mail(names, league_name):
	emails = []
	for name in names:
		if name != '':
			u = User.objects.get(username=name)
			emails.append(u.email)
	message_body = "You've been added to the league '%s' with users:\n\n" % league_name
	for name in names:
		message_body += "%s\n" % name
	send_mail(
		"Catansite New League",
		message_body,
		'catansite@gmail.com',
		emails,
		fail_silently = False,
	)

def add_user_to_league(league, uname):
	u = User.objects.get(username=uname)
	uil = UserInLeague(league = league, user = u)
	uil.save()


def leagues(request):
	leagues = request.user.league_set.all()
	context = {'leagues': leagues}
	return render(request, 'catansite/leagues.html', context)

def league_home(request, league_name):
	return HttpResponseRedirect(reverse('leaderboard', args=(league_name,)))
