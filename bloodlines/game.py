#Set(Magnarus, Tenebris, Kotaris, Jakelli, Lorlea, Orwyn, Pineland, Snowholt, Wilderbush, Orwall, Lochton, Morlyn, Highmont)
"""

#TODO - when two players attack each other's respective adjacent territories
attacks:
things to consider:
        allies attack wild together - who wins? state of democracy after?
        allies attack other together - who wins? state of democracy after?
        allies attack ally - state of democracy after?
    right now: everyone against everyone else - everyone at war afterwards

todo
need to handle order of attacks b/c if A attacks B and B attacks A the order matters b/c of moving troops
#could do random ordering of attacks?
#probabilities don't add up to 1 :(

Game should be a subclass of gamemodel - is a state with extended functionality

add technology/research teching. 
lay seige to territory? 
assassination? incredibly low chance of kill?
religion?
sack cities?
raise taxes?

Add win/lose message strings to actions that get sent to each player at the beginning of each turn so they can read what happened. Also can write these to a log for a story.


for AI: write a way to output reasoning strings this because that because that. If/then explanations. 

to calculate AI generate all possible_states from starting actions store in db. 
Partial utility function calculated in parallel by massive parallel bfs search. 
Then in parallel calculate R[S] for each state. Then each edge is a set of actions from one state to another. R[s] is calculated for those states. 
can partially calculate U[s] for the first state. If we iterate over everything again it should back propigate from the terminal goal states. 
Parallel BFS search to generate utility functions. Then a dfs through the utility state/action tree to display series of actions. 

what if utility function only depended on # of territories that you own? more states have the same value? 

also add event objects: given a condition - this happens with probability p

are simultaneous actions necessary? harder to compute

"""

from territories import gamemap
from action import AttackAction, SendSpyAction
from actions import gameactions
from player import Player, PlayerModel
from diplomacy import Diplomacy
from itertools import *
from dictdiffer import DictDiffer
from bisect import bisect
import random
import pdb

#profiling
import time
import cProfile
import pstats

DEFAULT_PLAYERS = [Player("A"), Player("B"), Player("C"), Player("D"), Player("E"), Player("F")]

"""
Game
    - players:
        p1
        -gold
            game_model
                -diplomacy
                -territories
                -spies
                player_model - estimated unless known
                    -name
                    -gold
                    game_model
                        -diplomacy
                        -territories
                        -spies
                        player_model
                            -name
                            -gold
                        player_model
                        player_model
                        player_model
                player_model
                    game_model
                player_model
                    game_model
                player_model
                    game_model

"""
class GameModel(object):
    def __init__(self, game=None, player=None):
        self.actions = gameactions
        self.player = player
        if game and player:
            self.territories = {t: game.territories[t].copy() for t in game.territories}
            self.diplomacy = game.diplomacy.copy()
            self.spies = game.spies.copy()
            self.messages = {k:game.messages[k][:] for k in game.messages}
            self.players = {p: PlayerModel(game.players[p] , self.limited(game, game.players[p])) for p in game.players if p != player.name}

    def to_dict(self):
        g = {}
        g['players'] = {p.name:p.to_dict() for p in self.players.values()}
        g['territories'] = {t.name:t.to_dict() for t in self.territories.values()}
        g['players'] = {p.name:p.to_dict() for p in self.players.values()}
        g['diplomacy'] = {str(k):v for k,v in self.diplomacy.items()}
        g['spies'] = {str(k):v for k,v in self.spies.items()}
        return g

    def to_list(self):
        g = []
        self.start_stop = {}
        for player in self.players:
            start = len(g)
            g += self.players[player].to_list()
            stop = len(g)
            self.start_stop[self.players[player].name] = (start, stop)
        for t in self.territories:
            start = len(g)
            g += self.territories[t].to_list()
            stop = len(g)
            self.start_stop[self.territories[t].name] = (start, stop)
        return g

    #returns a game model with diplomacy, territories, spies, and a limited player_model of each other player 
    def limited(self, game, player):
        g = GameModel()
        g.player = player
        g.territories = {t: game.territories[t].copy() for t in game.territories}
        g.diplomacy = game.diplomacy.copy()
        g.spies = game.spies.copy()
        g.players = {p: PlayerModel(game.players[p]) for p in game.players if p != player.name}
        g.messages = {x:[] for x in game.players}
        return g

    def copy(self):
        g = GameModel()
        g.player = self.player
        g.messages = {k:self.messages[k][:] for k in self.messages}
        g.territories = {t: self.territories[t].copy() for t in self.territories}
        g.diplomacy = self.diplomacy.copy()
        g.spies = self.spies.copy()
        g.players = {p: self.players[p].copy() for p in self.players}
        return g

    def set_diplomacy(self, p1, p2, diplomacy):
        self.diplomacy[frozenset(p1.name, p2.name)] = diplomacy

    #does it make sense to pass around the action classes or an instance of the action? currently passing around instance
    def actions_available(self, player):
        actions = []
        for action in self.actions:
            a = action()
            if a.condition(player,self): actions.append(a)
        return actions

    """
    Have to update each player's game_model based on the last round of actions
    update gold and force
    update the player's model of each other player and their model of each player according to the last move
    """
    def update_player(self, player):
        owned = {t for t in self.territories if self.territories[t].status == player.name}
        border_territories = set()
        for t in owned:
            border_territories |= self.territories[t].get_borders() - owned
        #use local references
        border_territories = [self.territories[t] for t in border_territories]
        player.gold += sum([self.territories[t].get_gold() for t in owned])
        if player.state:
            #update player's model of these territories b/c he can see them and the diplomacy of the players who control them
            for t in border_territories:
                player.state.territories[t.name] = self.territories[t.name]
                for key in self.diplomacy:
                    if t.status in key:
                        player.state.diplomacy[key] = self.diplomacy[key]
            #update player's model of the territories he owns
            for t in owned:
                player.state.territories[t] = self.territories[t]
                for key in self.diplomacy:
                    if self.territories[t].status in key:
                        player.state.diplomacy[key] = self.diplomacy[key]
            for other_player in player.state.players.values():
                player.state.update_player(other_player)

class Game(object):
    def __init__(self, players, main=False):
        # self.State = make_State(territories)
        self.players = {p.name: p for p in players}
        self.territories = {t:gamemap[t] for t in gamemap}
        self.diplomacy = {frozenset(x):Diplomacy.Neutral for x in combinations(self.players.keys(), 2)}
        self.spies = {x:0 for x in permutations(self.players.keys(), 2)}
        self.messages = {x:[] for x in self.players.keys()}
        self.gamemap = gamemap
        self.actions = gameactions
        self.actions_this_turn = {p: None for p in self.players}
        for player in self.players.values():
            send_spy = type('Send_spy_to_%s' % player.name,
                (SendSpyAction,),
                dict(player=player,
                     name='Send spy to %s' % player.name,
                     )
                )
            self.actions.append(send_spy)

    def to_dict(self):
        g = {}
        g['players'] = {p.name:p.to_dict() for p in self.players.values()}
        g['territories'] = {t.name:t.to_dict() for t in self.territories.values()}
        g['players'] = {p.name:p.to_dict() for p in self.players.values()}
        g['diplomacy'] = {str(k):v for k,v in self.diplomacy.items()}
        g['spies'] = {str(k):v for k,v in self.spies.items()}
        return g

    def to_list(self):
        g = []
        self.start_stop = {}
        for player in self.players:
            start = len(g)
            g += self.players[player].to_list()
            stop = len(g)
            self.start_stop[self.players[player].name] = (start, stop)
        for t in self.territories:
            start = len(g)
            g += self.territories[t].to_list()
            stop = len(g)
            self.start_stop[self.territories[t].name] = (start, stop)
        return g

    """
    init the game
    set up each player with a model of the game and models of the other players
    """
    def setup(self):
        territories = ["Magnarus", "Tenebris", "Kotaris", "Jakelli", "Lorlea", "Orwyn"]
        for i, player in enumerate(self.players.values()):
            self.territories[territories[i]].status = player.name
            self.territories[territories[i]].player_forces = 1000
        for i, player in enumerate(self.players.values()):
            player.state = self.get_game_model(player)


    #return a copy of this current game w/ main=False
    def get_game_model(self, player):
        return GameModel(self, player)

    def get_diplomacy(self, p1, p2):
        return self.diplomacy[frozenset(p1.name, p2.name)]

    def set_diplomacy(self, p1, p2, diplomacy):
        self.diplomacy[frozenset(p1.name, p2.name)] = diplomacy


    #does it make sense to pass around the action classes or an instance of the action? currently passing around instance
    def actions_available(self, player):
        actions = []
        for action in self.actions:
            a = action()
            if a.condition(player,self): actions.append(a)
        return actions

    def copy(self):
        g = GameModel()
        g.territories = {t: self.territories[t].copy() for t in self.territories}
        g.diplomacy = self.diplomacy.copy()
        g.spies = self.spies.copy()
        g.messages = {k:self.messages[k][:] for k in self.messages}
        g.players = {p: self.players[p].copy() for p in self.players}
        return g

    #TODO
    #need to handle order of attacks b/c if A attacks B and B attacks A the order matters b/c of moving troops
    #could do random ordering of attacks?
    #probabilities don't add up to 1 :(
    def get_next_states(self, actions_this_turn):
        war_actions = {k:actions_this_turn[k] for k in actions_this_turn if actions_this_turn[k].type == "WAR"}
        other = {k:actions_this_turn[k] for k in actions_this_turn if actions_this_turn[k].type != "WAR"}
        territories_under_attack = {war_actions[p].territory.name:{} for p in war_actions}
        possible_states = [(1, self.copy())]
        #nonconflicting actions
        for player in other:
            action = other[player]
            new_states = []
            for p, state in possible_states:
                new_states += [(p*np, a) for np,a in action.states(player, state)]
            possible_states = new_states
        #conflicting actions
        for player in war_actions:
            action = war_actions[player]
            territories_under_attack[action.territory.name][player] = action
        #deal with cases of A attacking B and B attacking A and C attacking A etc by randomly stopping players from attacking to defend
        attackers = []
        for territory, players in territories_under_attack.items():
            defender = self.territories[territory].status
            if defender != "WILD" and defender not in attackers:
                if war_actions.get(defender) and territories_under_attack.get(war_actions[defender].territory.name) and territories_under_attack[war_actions[defender].territory.name].get(defender):
                    attackers += players
                    del territories_under_attack[war_actions[defender].territory.name][defender]
                    if not len(territories_under_attack[war_actions[defender].territory.name]):
                        del territories_under_attack[war_actions[defender].territory.name]
        for territory in territories_under_attack:
            new_states = []
            for p, state in possible_states:
                new_states += [(p*np, a) for np,a in AttackAction.conflicting_states(territories_under_attack[territory], state)]
            possible_states = new_states
        return possible_states

    def get_next_state(self, actions_this_turn):
        possible_states = self.get_next_states(actions_this_turn)
        print len(possible_states)
        next_state = self.chance(possible_states)
        print next_state
        self.merge_game_and_gamemodel(next_state[1])
        for player in self.players.values():
            self.update_player(player)

    """
    Have to update each player's game_model based on the last round of actions from their perspective
    update gold and force
    update the player's model of each other player and their model of each player according to the last move
    """
    def update_player(self, player):
        owned = {t for t in self.territories if self.territories[t].status == player.name}
        #player is dead
        if not owned:
            del self.players[player.name]
            return
        border_territories = set()
        for t in owned:
            border_territories |= self.territories[t].get_borders() - owned
        #use local references
        border_territories = [self.territories[t] for t in border_territories]
        #update player's model of these territories b/c he can see them and the diplomacy of the players who control them
        for t in border_territories:
            player.state.territories[t.name] = self.territories[t.name]
            for key in self.diplomacy:
                if t.status in key:
                    player.state.diplomacy[key] = self.diplomacy[key]
        #update player's model of the territories he owns
        for t in owned:
            player.state.territories[t] = self.territories[t]
            for key in self.diplomacy:
                if self.territories[t].status in key:
                    player.state.diplomacy[key] = self.diplomacy[key]
        player.gold += sum([self.territories[t].get_gold() for t in owned])
        for other_player in player.state.players.values():
            if self.spies[(player.name, other_player.name)]:
                player.state.other_player = other_player.state.copy()
            else:
                player.state.update_player(other_player)

    def chance(self, states):
        P = [p for p,a in states]
        if sum(P) != 1 and abs(1.0-sum(P)) > 0.001:
            pdb.set_trace()
        cdf = [P[0]]
        for i in xrange(1, len(P)):
            cdf.append(cdf[-1] + P[i])
        random_ind = bisect(cdf,random.random())
        return states[random_ind]

    def merge_game_and_gamemodel(self, game_model):
        diffs = 0
        #territories
        for t in self.territories:
            if self.territories[t] != game_model.territories[t]:
                diffs += 1
                self.territories[t] = game_model.territories[t]
        for p in self.players:
            if self.players[p] != (game_model.players.get(p) or game_model.player):
                diffs += 1
                #other changes to a player besides gold?
                if game_model.players.get(p):
                    self.players[p].gold = game_model.players.get(p).gold
                else:
                    self.players[p].gold = game_model.player.gold
        for d in self.diplomacy:
            if self.diplomacy[d] != game_model.diplomacy[d]:
                diffs += 1
                self.diplomacy[d] = game_model.diplomacy[d]
        for s in self.spies:
            if self.spies[s] != game_model.spies[s]:
                diffs += 1
                self.spies[s] = game_model.spies[s]
        for m in self.messages:
            if self.messages[m] != game_model.messages[m]:
                diffs += 1
                self.messages[m] = game_model.messages[m]
        return diffs

    #has the game over condition been met?
    def game_over(self):
        territories = [self.territories[t].status for t in self.territories]
        return territories[1:] == territories[:-1]

    #only to be called by main game object
    def play(self):
        i = 0
        while not self.game_over():
            self.actions_this_turn = {p: None for p in self.players}
            #profiling information
            pr = cProfile.Profile()
            pr.enable()
            possible_states = 0
            player_actions = {}
            for player in self.players.values():
                player_actions[player.name] = self.actions_available(player)
            sets_of_actions = [{player_actions.keys()[i] : x for i,x in enumerate(actions)} for actions in product(*player_actions.values())]
            print {k:len(v) for k,v in player_actions.items()}
            print "Number of possible action combos: %s" % len(sets_of_actions)
            for actions in sets_of_actions:
                    self.get_next_states(actions)
            pr.disable()
            pr.print_stats('cumulative')
            print "Number of possible following states: %i" % possible_states
            print "Turn #%i" % i
            i += 1
            for player in self.players.values():
                if False:#player.is_human:
                    actions = self.actions_available(player)
                    print "Player: %s" % player.name
                    print "Gold: %i" % player.gold
                    owned = set([self.territories[t] for t in self.territories if self.territories[t].status == player.name])
                    for i in owned:
                        print "%s : %i" % (i.name, i.player_forces)
                    for m in self.messages[player.name]:
                        print m
                    print "Actions available:"
                    for i,action in enumerate(actions):
                        if action.type == "WAR":
                            print '%i: %s - owned by %s' % (i, action.name, self.territories[action.territory.name].status)
                        else:
                            print '%i: %s' % (i, action.name)
                    usr_input = None
                    while usr_input not in [i for i in range(len(actions))]:
                        usr_input = input("Action: ")
                    self.actions_this_turn[player.name] = actions[usr_input]
                else:
                    self.actions_this_turn[player.name] = random.choice(self.actions_available(player))
            self.messages = {x:[] for x in self.players.keys()}
            pdb.set_trace()
            cProfile.runctx('self.get_next_state(self.actions_this_turn)',globals(),{'self':self}, 'profile.stats')
            stats = pstats.Stats('profile.stats')
            #next update player states from the new state
        return False

