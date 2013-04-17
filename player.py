from hashdict import *

class Player:
	"""
	PlayerState = {"known":{"territories": [{"force","state", "gold"}],
							"total_gold":0},
				   "modeled":{"players":{models of other players}}
				  }

	ModelOfAPlayer = {"Trust":"High/Med/Low",
					  "Diplomacy": "Allies/Neutral/Angry/War",
					  for each player: p_v_otherplayer - how they feel about other players "Allies/Neutral/Angry/War",
					  "Territories":[] }
	"""
	def __init__(self):

	def process_info(self, info):
	"""
	Info is passed to players from the game update and from other players. Players blindly accept info from the game.
	But will only accept info from other players that they 'trust'. Players keep track of info from other players and if it later becomes true then
	the trust level increases. 
	info = {game, playery1:{}, player2:None, ...}
	"""
		pass

	def R(self, state):
		pass
