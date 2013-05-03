from action import Action, AttackAction, DefendAction, RaiseForceAction, SendSpyAction, MoveForceAction, PropagandaAction, InciteRebellionAction
from territories import gamemap
import abc

gameactions = []

for territory in gamemap.values():
	for b in territory.get_borders():
		border = gamemap.get(b)
		attack_territory_from_other = type('Attack_%s_from_%s' % (territory.name, border.name),
			(AttackAction,),
			dict(territory=territory,
				 border=border,
				 name='Attack %s from %s' % (territory.name, border.name),
				 )
			)
		move_forces_from_other = type('Move_forces_from_%s_%s' % (border.name, territory.name),
			(MoveForceAction,),
			dict(territory=territory,
				 border=border,
				 name='Move forces from %s to %s' % (border.name, territory.name),
				 )
			)
		gameactions += [attack_territory_from_other, move_forces_from_other]

for territory in gamemap.values():
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
	propaganda = type('Propaganda_in_%s' % territory.name,
		(PropagandaAction,),
		dict(territory=territory,
			 name='Distribute propaganda in %s' % territory.name,
			 )
		)
	incite_rebellion = type('Incite_rebellion_in_%s' % territory.name,
		(InciteRebellionAction,),
		dict(territory=territory,
			 name='Incite a rebellion in %s' % territory.name,
			 )
		)
	gameactions += [defend_territory, raise_force, propaganda, incite_rebellion]

class WaitAction(Action):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.type = "WAIT"
        self.name = "Wait"

    def condition(self, player, state):
        return True

    def states(self, player, state):
        return [(1, state)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Player %s waited succesfully" % player.name

    def lose_message(self, player):
        return "Player %s waited succesfully" % player.name

for action in Action.__subclasses__():
	if action not in gameactions and action not in [AttackAction, RaiseForceAction, SendSpyAction, MoveForceAction, PropagandaAction, InciteRebellionAction]:
		gameactions.append(action)