from event import Event
from territories import gamemap
import abc

gameevents = []

"""
Event - an event that a player can do
.condition(state): takes the game state and returns true if it can happen
.states(state): returns possible output states in (probability, state) tuples
"""
# class Event(object):
#     __metaclass__ = abc.ABCMeta
    
#     @abc.abstractmethod
#     def __init__(self):
#         """Instantiate an instance of the event"""
#         return

#     @abc.abstractmethod
#     def condition(self, player, state):
#         """Returns True if the event can happen in the state, false otherwise"""
#         return

#     @abc.abstractmethod
#     def states(self, player, state):
#         """returns possible states from the event happening in state in the form of [(probability, state)]"""
#         return

#     @abc.abstractmethod
#     def message(self, player):
#         """What to display to the players"""
#         return

# for territory in gamemap:
# 	for border in territory.get_borders():
# 		attack_territory_from_other = type('Attack_%s_from_%s' % (territory.name, border.name),
# 			(AttackAction,),
# 			dict(territory=territory,
# 				 border=border,
# 				 name='Attack %s from %s' % (territory.name, border.name),
# 				 )
# 			)
# 		move_forces_from_other = type('Move_forces_from_%s_%s' % (border.name, territory.name),
# 			(MoveForceAction,),
# 			dict(territory=territory,
# 				 border=border,
# 				 name='Move forces from %s to %s' % (border.name, territory.name),
# 				 )
# 			)
# 		gameactions.append(attack_territory_from_other)
# 		gameactions.append(move_forces_from_other)