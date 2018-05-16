from django.db import models

class Player(models.Model):
	player_name = models.CharField(max_length=200)
	elo = models.IntegerField(default=1500)

	def __str__(self):
		return self.player_name

class Game(models.Model):
	played_date = models.DateTimeField('date played')
	players = models.ManyToManyField(Player, through='PlayerInGame')	

	def __str__(self):
		return "game" + str(self.played_date)

class PlayerInGame(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	score = models.IntegerField(default=0)
