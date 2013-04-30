import abc
import random
from itertools import *
from diplomacy import Diplomacy
import pdb
"""
Action - an action that a player can do
.condition(player, state): takes the game state and the player and returns true if that player can take the action
.states(player, state): returns possible output states in (probability, state) tuples
.type = "BATTLE" or other - determines order in which actions are carried out

"""
class Action(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self):
        """Instantiate an instance of the action"""
        return

    @abc.abstractmethod
    def condition(self, player, state):
        """Returns True if the player can take the action in the state, false otherwise"""
        return

    @abc.abstractmethod
    def states(self, player, state):
        """returns possible states from taking this action in state in the form of [(probability, state)]"""
        return

    @abc.abstractproperty
    def type(self):
        """What type of action is this? This defines in what order actions are taken"""
        return

    @abc.abstractmethod
    def win_message(self, player):
        """What to display to the player who wins?"""
        return

    @abc.abstractmethod
    def lose_message(self, player):
        """What to display to the player(s) who lose?"""
        return

class DefendAction(Action):
    def __init__(self):
        self.type = "WAR"

    def condition(self, player, state):
        return False #state.territories[self.border.name].status == player.name

    def states(self, player, state):
        # loss = state.copy()
        # win = state.copy()
        # if state.territories[self.territory.name].status != 'WILD':
        #     win.set_diplomacy(player, state.players[state.territories[self.territory.name].status], Diplomacy.War)
        #     loss.set_diplomacy(player, state.players[state.territories[self.territory.name].status], Diplomacy.War)
        # #loss
        # loss.territories[self.border.name].player_forces *= .5
        # #win
        # win.territories[self.territory.name].player_forces = win.territories[self.border.name].player_forces
        # win.territories[self.border.name].player_forces = 0
        # win.territories[self.territory.name].status = player.name
        # #probability
        # total_forces = state.territories[self.territory.name].natural_force + state.territories[self.border.name].player_forces + state.territories[self.territory.name].player_forces
        # p = (state.territories[self.border.name].player_forces*1.0)/total_forces
        return [(1.0, state.copy())]
    def type(self):
        return self.type

    def win_message(self, player):
        return "Your forces were victorius defending %s during the battle of %s." % (self.territory.name, self.territory.name)

    def lose_message(self, player):
        return "Your forces were defeated defending %s during the battle of %s." % (self.territory.name, self.territory.name)

class SendSpyAction(Action):
    def __init__(self):
        self.type = "DIPLOMACY"

    def condition(self, player, state):
        return state.spies.get((player.name,self.player.name)) == 0 and player.gold >= 500

    def states(self, player, state):
        loss = state.copy()
        win = state.copy()
        #loss - modify gold
        loss.players[player].gold -= 500
        loss.messages[player].append(self.lose_message(player))
        #win
        win.players[player].gold -= 500
        win.spies[(player,self.player.name)] += 1
        win.messages[player].append(self.win_message(player))
        #probability
        return [(.8, win),(.2, loss)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Your spy has infiltrated %s" % self.player.name

    def lose_message(self, player):
        return "You we're unable to send a spy to %s." % self.player.name

class RaiseForceAction(Action):
    def __init__(self):
        self.type = "RESOURCES"

    def condition(self, player, state):
        return state.territories[self.territory.name].status == player.name and player.gold >= 500

    def states(self, player, state):
        loss = state.copy()
        win = state.copy()
        #loss - modify gold
        loss.players[player].gold -= 500
        loss.messages[player].append(self.lose_message(player))
        win.players[player].gold -= 500
        #win
        win.territories[self.territory.name].player_forces += 1000
        win.messages[player].append(self.win_message(player))
        #probability
        return [(.9, win),(.1, loss)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Your raised forces in %s." % self.territory.name

    def lose_message(self, player):
        return "Your failed to raise forces in %s." % self.territory.name

class MoveForceAction(Action):
    def __init__(self):
        self.type = "RESOURCES"

    def condition(self, player, state):
        return state.territories[self.territory.name].status == player.name and \
               state.territories[self.border.name].status == player.name and \
               state.territories[self.border.name].player_forces > 0

    def states(self, player, state):
        win = state.copy()
        #win
        win.territories[self.territory.name].player_forces += win.territories[self.border.name].player_forces
        win.territories[self.border.name].player_forces = 0
        win.messages[player].append(self.win_message(player))
        #probability
        return [(1.0, win)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Your forces moved safely from %s to %s" % (self.border.name, self.territory.name)

    def lose_message(self, player):
        return "Your failed to raise forces in %s." % self.territory.name

class PropagandaAction(Action):
    def __init__(self):
        self.type = "DIPLOMACY"

    def condition(self, player, state):
        return (state.territories[self.territory.name].status == player.name and \
                state.players[player.name].gold >= 250)                      or \
               (state.territories[self.territory.name].status != player.name and \
                state.territories[self.territory.name].status != "WILD"     and \
                state.spies[(player.name, state.territories[self.territory.name].status)] and \
                state.players[player.name].gold >= 250)

    def states(self, player, state):
        win = state.copy()
        #win
        win.players[player].gold -= 250
        if state.territories[self.territory.name].status == player:
            win.territories[self.territory.name].loyalty = min(win.territories[self.territory.name].loyalty*2, 1.0)
            win.messages[player].append(self.win_message(player))
        else:
            win.territories[self.territory.name].loyalty *= .5
            win.messages[player].append(self.lose_message(player))
        #probability
        return [(1.0, win)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Your propaganda raised state loyalty in %s" % self.territory.name

    def lose_message(self, player):
        return "Your propaganda has lowered state loyalty in %s" % self.territory.name

class InciteRebellionAction(Action):
    def __init__(self):
        self.type = "DIPLOMACY"

    def condition(self, player, state):
        return state.territories[self.territory.name].status != player.name and \
               state.territories[self.territory.name].status != "WILD" and \
               state.spies[(player.name, state.territories[self.territory.name].status)] and \
               state.territories[self.territory.name].loyalty <= .25 and \
               state.players[player.name].gold >= 500

    def states(self, player, state):
        if not self.condition(state.players[player], state):
            return [(1, state.copy())]
        loss = state.copy()
        win = state.copy()
        #win
        win.players[player].gold -= 500
        loss.players[player].gold -= 500
        win.territories[self.territory.name].status = "WILD"
        win.territories[self.territory.name].loyalty = .5
        win.messages[player].append(self.win_message(player))
        win.messages[state.territories[self.territory.name].status].append(self.lose_message(None))
        loss.messages[player].append("You failed to incite a rebellion.")
        #probability
        return [(.5, win),(.5, loss)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "The rebellion in %s was successful!" % self.territory.name

    def lose_message(self, player):
        return "There was a rebellion in %s" % self.territory.name

class AttackAction(Action):
    def __init__(self):
        self.type = "WAR"

    def condition(self, player, state):
        return state.territories[self.border.name].status == player.name and \
               state.territories[self.territory.name].status != player.name and \
               state.territories[self.border.name].player_forces != 0

    """
    takes a {player:action} dict for all players attacking a territory and returns the possible outcomes
    things to consider:
        allies attack wild together - who wins? state of democracy after?
        allies attack other together - who wins? state of democracy after?
        allies attack ally - state of democracy after?
    right now: everyone against everyone else - everyone at war afterwards
    """
    @staticmethod
    def conflicting_states(player_actions, state):
        territory = set([action.territory for action in player_actions.values()])
        if len(territory) != 1:
            pdb.set_trace()
        else:
            territory = territory.pop()
        defender = state.territories[territory.name].status
        resulting_states = []
        #if wild
        if defender == "WILD":
            total_forces = sum([state.territories[action.border.name].player_forces for action in player_actions.values()])
            diplomacy = {frozenset((p1,p2)):Diplomacy.War for p1,p2 in combinations(player_actions.keys(), 2)}
            for player, action in player_actions.items():
                s = state.copy()
                s.diplomacy.update(diplomacy)
                # s.players[player].state.diplomacy.update(diplomacy)
                s.territories[territory.name].status = player
                s.territories[territory.name].player_forces = s.territories[action.border.name].player_forces
                s.territories[action.border.name].player_forces = 0
                s.messages[player].append(action.win_message(player))
                for other_player, other_action in player_actions.items():
                    if other_player != player:
                        s.territories[other_action.border.name].player_forces *=  .5
                        s.messages[other_player].append(player_actions[other_player].lose_message(other_player))
                p = (state.territories[action.border.name].player_forces*1.0)/total_forces
                resulting_states.append((p,s))
        else:
            if defender not in player_actions:
                for defend in DefendAction.__subclasses__():
                    if defend().border == territory:
                        player_actions[defender] = defend()
            total_forces = sum([state.territories[action.border.name].player_forces for action in player_actions.values()]) + territory.natural_force
            diplomacy = {frozenset((p1,p2)):Diplomacy.War for p1,p2 in combinations(player_actions.keys(), 2)}
            for player, action in player_actions.items():
                s = state.copy()
                s.diplomacy.update(diplomacy)
                # s.players[player].state.diplomacy.update(diplomacy)
                s.territories[territory.name].status = player
                s.territories[territory.name].player_forces = s.territories[action.border.name].player_forces
                s.messages[player].append(action.win_message(player))
                if player != defender:
                    s.territories[action.border.name].player_forces = 0
                for other_player, other_action in player_actions.items():
                    if other_player != player and other_player != defender:
                        s.territories[other_action.border.name].player_forces *=  .5
                        s.messages[other_player].append(action.lose_message(other_player))
                if player == defender:
                    p = (territory.natural_force + state.territories[action.border.name].player_forces*1.0)/total_forces
                else:
                    p = (state.territories[action.border.name].player_forces*1.0)/total_forces
                resulting_states.append((p,s))
        # print sum([p for p,s in resulting_states]), [p for p,s in resulting_states]
        if sum([p for p,s in resulting_states]) != 1:
            pdb.set_trace()
        return resulting_states


    def states(self, player, state):
        loss = state.copy()
        win = state.copy()
        if state.territories[self.territory.name].status != 'WILD':
            win.set_diplomacy(player, state.players[state.territories[self.territory.name].status], Diplomacy.War)
            loss.set_diplomacy(player, state.players[state.territories[self.territory.name].status], Diplomacy.War)
        #loss
        loss.territories[self.border.name].player_forces *= .5
        #win
        win.territories[self.territory.name].player_forces = win.territories[self.border.name].player_forces
        win.territories[self.border.name].player_forces = 0
        win.territories[self.territory.name].status = player.name
        #probability
        total_forces = state.territories[self.territory.name].natural_force + state.territories[self.border.name].player_forces + state.territories[self.territory.name].player_forces
        p = (state.territories[self.border.name].player_forces*1.0)/total_forces
        return [(p, win), (1-p, loss)]

    def type(self):
        return self.type

    def win_message(self, player):
        return "Your forces were victorius during the battle of %s." % self.territory.name

    def lose_message(self, player):
        return "Your forces were defeated during the battle of %s." % self.territory.name

