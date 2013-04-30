from action import Action, AttackAction, DefendAction, RaiseForceAction, SendSpyAction
from territories import gamemap
import abc

gameactions = []

for territory in gamemap:
	for border in territory.get_borders():
		attack_territory_from_other = type('Attack_%s_from_%s' % (territory.name, border.name),
			(AttackAction,),
			dict(territory=territory,
				 border=border,
				 name='Attack %s from %s' % (territory.name, border.name),
				 )
			)
		gameactions.append(attack_territory_from_other)

for territory in gamemap:
	defend_territory = type('Defend_%s' % territory.name,
		(DefendAction,),
		dict(territory=territory,
			 border=territory,
			 name='Defend %s' % territory.name,
			 )
		)
	raise_force = type('Raise_Forces_in_%s' % territory.name,
		(RaiseForceAction,),
		dict(territory=territory,
			 name='Raise Forces in %s' % territory.name,
			 )
		)
	gameactions.append(defend_territory)
	gameactions.append(raise_force)

class WaitAction(Action):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.type = "WAIT"
        self.name = "Wait"

    def condition(self, player, state):
        return True

    def states(self, player, state):
        return [(1, state.copy())]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Player %s waited succesfully" % player.name

    def lose_message(self, player):
        return "Player %s waited succesfully" % player.name

for action in Action.__subclasses__():
	if action not in gameactions and action not in [AttackAction, RaiseForceAction, SendSpyAction]:
		gameactions.append(action)