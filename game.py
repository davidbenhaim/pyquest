from territories import Territory
from quest_state import make_State
from bisect import bisect
from random import random
from itertools import product
from copy import deepcopy
import time
import mdp
import pdb



class Game:
    def __init__(self, players, territories, start_state):
        # self.State = make_State(territories)
        self.players = {p['name']:p for p in players}
        self.territories = {t.name:t for t in territories}
        self.state = start_state
        self.turn = 0
        init_state = self.state
        self.actions = {}

    def check_game_over(self):
        return False

    def play(self):
        for territory in self.territories.values():
            print territory.name+" - Gold: %i Force: %i" % (territory.gold, territory.force)
        while not self.check_game_over():
            self.take_turn()

    def take_turn(self):
        self.actions[self.turn] = {}
        for player in self.players.values():
            if player.get('is_human'):
                actions = self.actions_available(self.state[player['name']])
                print "Player "+player.get('name')
                print "Actions available:"
                for i,action in enumerate(actions):
                    print '%i: %s' % (i, action)
                usr_input = None
                while usr_input not in [i for i in range(len(actions))]:
                    usr_input = input("Action: ")
                self.actions[self.turn][player['name']] = actions[usr_input]
            else:
                # time.sleep(3)
                if self.state[player['name']] not in self.policies[player['name']]:
                    self.comps[player['name']] = mdp.QuestMDP(set(self.territories.values()), self.state)
                    self.comps[player['name']].generate_states()
                    self.policies[player['name']] = mdp.best_policy(self.comps[player['name']], mdp.value_iteration(self.comps[player['name']]))
                # pdb.set_trace()
                action = self.policies[player['name']]
                self.actions[self.turn][player['name']] = actions[usr_input]
        states = self.possible_states_from_actions()
        self.turn += 1
        self.state = self.chance(states)[1]
        print self.state


    def chance(self, states):
        P = [p for p,a in states]
        cdf = [P[0]]
        for i in xrange(1, len(P)):
            cdf.append(cdf[-1] + P[i])
        random_ind = bisect(cdf,random())
        return states[random_ind]

    def actions_available(self, player):
        """Set of actions that can be performed by the player in his current state"""
        actions = []
        raise_forces = [("RAISE_FORCE", player['force']*2.0)] if player['gold'] > 0 else []
        controlled = [t for t in self.territories if player[t] == player['name']]
        owned = set([t for t in self.territories if player[t] in [player["name"], player["name"]+"-REINFORCED"]])
        border_territories = set()
        for t in owned:
            border_territories |= self.territories[t].get_borders() - owned
        reenforce_territories = [("REINFORCE", t) for t in controlled]
        take_territories = [("TAKE", t) for t in border_territories if player['force'] >= self.territories[t].force]
        raise_trust = [("RAISE_TRUST", other_player['name']) for other_player in self.players.values() if other_player['name'] != player['name'] and player[other_player['name']]['Trust'] != "High"]
        send_message = []
        return raise_forces + reenforce_territories + take_territories + raise_trust + send_message + [("WAIT",None)]

    #incredibly innefficiant plant function
    #returns a list of (p, state) tuples
    def possible_states_from_actions(self):
        base_state = deepcopy(self.state)
        for player in self.players.values():
            base_state[player['name']]['gold'] += sum([self.territories[t].gold for t in self.territories if self.state[t] == player['name']])
            base_state[player["name"]]['gold'] += sum([self.territories[t].gold*2 for t in self.territories if self.state[t] == player['name']+"-REINFORCED"])
        states = [(1.0, base_state)]
        #actions[turn #][player] = action
        #actions is {player: action, player: action, player: action etc}
        actions = self.actions[self.turn] 
        #all of the non-conflicting actions
        #reinforce
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "REINFORCE"]:
            # new_states = []
            for state in states:
                # cstate = deepcopy(state[1])
                state[1][action[1]] = player+"-REINFORCED"
                state[1][player][action[1]] = player+"-REINFORCED"
                # new_states += self.chain_actions(state, cstate, 1)
            # states = new_states
        #raise_force
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "RAISE_FORCE"]:
            new_states = []
            for state in states[:]:
                cstate = deepcopy(state[1])
                cstate[player]['force'] *= 2
                new_states += self.chain_actions(state, cstate, .75)
            states = new_states
        #raise_trust
        #(p,(action, t_p))
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "RAISE_TRUST"]:
            action, t_p = action
            new_states = []
            for state in states:
                cstate = deepcopy(state[1])
                trust_dict = {"Low":"Med", "Med":"High", "High":"High"}
                diplomacy_dict = {"Angry":"Neutral", "Neutral":"Allies", "Allies":"Allies"}
                cstate[t_p][player]['Trust'] = trust_dict[cstate[t_p][player]['Trust']]
                if cstate[t_p][player]['Trust'] == "High" and cstate[t_p][player]['Diplomacy'] in ["Allies","Neutral","Angry"]:
                    cstate[t_p][player]['Diplomacy'] = diplomacy_dict[cstate[t_p][player]['Diplomacy']]
                new_states += self.chain_actions(state, cstate, .50)
            states = new_states
        #send_message
        #(p,(action, t_p, m_state))
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "SEND_MESSAGE"]:
            action, t_p, m_state = action
            for state in states:
                cstate = deepcopy(state)
                cstate[t_p].update(m_state)
                if base_state[t_p][player] == "High":
                    new_states += self.chain_actions(state, cstate, .90)
                elif base_state[t_p][player] == "Med":
                    new_states += self.chain_actions(state, cstate, .30)
                else:
                    new_states += self.chain_actions(state, cstate, 0)
            states = new_states
        #all of the potential conflicting actions
        #only takes conflict
        takes = [(p,action) for p,action in actions.items() if action[0] == "TAKE"]
        #{territory: [players taking]}
        if takes:
            attacked = [action[1] for p,action in actions.items()]
            territory_takes = {t:[self.state[self.state[t].split('-')[0]]] for t in self.territories if self.state[t] != "WILD" and t in attacked}
            for p, action in takes:
                t, territory = action
                if territory_takes.get(territory):
                    territory_takes[territory].append(self.state[p])
                else:
                    territory_takes[territory] = [self.state[p]]
            #produce the result of each battle
            for t, players in territory_takes.items():
                if self.state[t] == 'WILD':
                    new_states = []
                    total_force = total_force = sum([player['force'] for player in players]) + self.territories[t].force
                    if len(players) > 1:
                        for state in states[:]:
                            for player in players:
                                cstate = deepcopy(state[1])
                                cstate[t] = player['name']
                                cstate[player['name']][t] = player['name']
                                for other in players:
                                    if player != other and not (player[other['name']]['Diplomacy'] == "Allied" == other[player['name']]['Diplomacy']):
                                        cstate[other['name']]['force'] *= .5
                                new_states += [(state[0]*player['force']*1.0/total_force, cstate)]
                            new_states.append((state[0]*self.territories[t].force*1.0/total_force, deepcopy(state[1])))
                        states = new_states
                    else:
                        player = players[0]
                        for state in states:
                            cstate = deepcopy(state[1])
                            cstate[t] = player['name']
                            cstate[player['name']][t] = player['name']
                            new_states += self.chain_actions(state, cstate, player['force']*1.0/total_force)
                        states = new_states
                else:
                    new_states = []
                    total_force = sum([player['force'] for player in players])
                    for state in states:
                        for player in players:
                            cstate = deepcopy(state[1])
                            cstate[t] = player['name']
                            cstate[player['name']][t] = player['name']
                            for other in players:
                                if player != other and not (player[other['name']]['Diplomacy'] == "Allied" == other[player['name']]['Diplomacy']):
                                    cstate[other['name']]['force'] *= .5
                            new_states += [(state[0]*player['force']*1.0/total_force, cstate)] #self.chain_actions(state, cstate, player['force']*1.0/total_force)
                    states = new_states
        print states
        print sum([p for p,s in states])
        return states

    def chain_actions(self, state, state2, p):
        if p != 1 and p:
            prob, state = state
            return [(1.0 * prob * (1.0 - p), state),(1.0*prob*p, state2)]
        elif p == 0:
            return [state]
        else:
            return [(p, state2)]

        # State = self.State
        # state = self.state
        # """Performs an action by the player and updates the state of the game to the next state"""
        # new_state = State(**state._asdict())
        # action, value = action
        # states = []
        # if action == "RAISE_FORCE":
        #     territories = {t: getattr(state, t) for t in self.territories}
        #     states += [(.75, State(state.gold, value, **territories)),
        #                (.25, State(state.gold, value*.5, **territories))]
        # elif action == "REDUCE_FORCE":
        #     territories = {t: getattr(state, t) for t in self.territories}
        #     states += [(1, State(state.gold, value, **territories))]
        # elif action == "RE-ENFORCE":
        #     territories = {t: getattr(state, t) for t in self.territories}
        #     territories[value] = "RE-ENFORCED"
        #     states += [(1, State(state.gold - self.territories[value].gold*2, state.force, **territories))]
        # elif action == "WAIT":
        #     states += [(1,new_state)]
        # else: #TAKE
        #     territories = {t: getattr(state, t) for t in self.territories}
        #     territories[value] = "CONTROLLED"
        #     states += [(.9, State(state.gold, state.force, **territories)),
        #                (.1, State(state.gold, state.force - self.territories[value].force*.5, **{t: getattr(state, t) for t in self.territories}))]
        # all_states = []
        # #calculate possible rebellions
        # for prob, state in states:
        #     #rebellion
        #     controlled = [t for t in self.territories if getattr(state, t) == "CONTROLLED"]
        #     r = .2
        #     pastabilities = product((.2,.8),repeat=len(controlled))
        #     for pasta in pastabilities:
        #         p = mdp.prod(pasta)
        #         rebelled = [controlled[i] for i,s in enumerate(pasta) if s == r]
        #         territories = {t: getattr(state, t) for t in self.territories}
        #         for t in territories:
        #             if t in rebelled:
        #                 territories[t] = "WILD"
        #         all_states += [(prob*p, State(state.gold, state.force, **territories))]
        # final_states = []
        # for p, state in all_states:
        #     dict_state = state._asdict()
        #     dict_state['gold'] += sum([self.territories[x].gold for x in self.territories if getattr(state, x) in ["CONTROLLED"]]) + sum([self.territories[x].gold*2 for x in self.territories if getattr(state, x) in ["RE-ENFORCED"]]) - state.force*.1
        #     state = State(**dict_state)
        #     final_states.append((p, state))
        # self.state = self.chance(final_states)[1]
    
    def print_state(self):
        print self.state



