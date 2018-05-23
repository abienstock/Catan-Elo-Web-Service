from django.db import models
from django.contrib.auth.models import User

class League(models.Model):
	league_name = models.CharField(max_length=200)
	users = models.ManyToManyField(User, through='UserInLeague')

class UserInLeague(models.Model):
	league = models.ForeignKey(League, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	elo = models.FloatField(default=1500.0)

class Game(models.Model):
	played_date = models.DateTimeField('date played')
	league = models.ForeignKey(League, on_delete=models.CASCADE)	
	uils = models.ManyToManyField(UserInLeague, through='UserInGame')

	def __str__(self):
		return "game" + str(self.played_date)

class UserInGame(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	uil = models.ForeignKey(UserInLeague, on_delete=models.CASCADE)
	score = models.IntegerField(default=0)
