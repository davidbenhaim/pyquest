import abc
import random
from itertools import *
from diplomacy import Diplomacy
import pdb
"""
Event - an event that a player can do
.condition(state): takes the game state and returns true if it can happen
.states(state): returns possible output states in (probability, state) tuples
"""
class Event(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self):
        """Instantiate an instance of the event"""
        return

    @abc.abstractmethod
    def condition(self, player, state):
        """Returns True if the event can happen in the state, false otherwise"""
        return

    @abc.abstractmethod
    def states(self, player, state):
        """returns possible states from the event happening in state in the form of [(probability, state)]"""
        return

    @abc.abstractmethod
    def message(self, player):
        """What to display to the players"""
        return