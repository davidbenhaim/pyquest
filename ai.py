from mdp import MDP
from copy import deepcopy
from hashdict import hashdict
from itertools import product
from utils import *
import pdb

class MultiMDP(MDP):
    def __init__(self, player, players, territories, init=None, gamma=.1):
        self.territories = territories#{t.name:t for t in territories}
        self.state = player
        self.players = players
        self.pi = {}
        MDP.__init__(self, init, actlist=None, terminals=None, gamma=gamma)

    def R(self, state):
        "Return a numeric reward for this state."
        rewards = {}
        for player in self.players.values():
            if player['name'] == self.state['name']:
                reward = state['gold'] + sum([self.territories[x].gold for x in self.territories if state[x] in [state['name']]]) + sum([self.territories[x].gold*2 for x in self.territories if state[x] in [state['name']+"-REINFORCED"]]) - 3000*sum([1 for x in self.territories if state[x] not in [state['name'], state['name']+"-REINFORCED"]])
                if not [x for x in self.territories if state[x] in [state['name'], state['name']+"-REINFORCED"]]:
                    reward = -1.0*999999999999
                if not [x for x in self.territories if state[x] not in [state['name'], state['name']+"-REINFORCED"]]:
                    reward = 999999999999
            else:
                reward = state[player['name']]['gold'] + sum([self.territories[x].gold for x in self.territories if state[x] in [player['name']]]) + sum([self.territories[x].gold*2 for x in self.territories if state[x] in [player['name']+"-REINFORCED"]]) - 3000*sum([1 for x in self.territories if state[x] not in [player['name'], player['name']+"-REINFORCED"]])
                if not [x for x in self.territories if state[x] in [player['name'], player['name']+"-REINFORCED"]]:
                    reward = -1.0*999999999999
                if not [x for x in self.territories if state[x] not in [player['name'], player['name']+"-REINFORCED"]]:
                    reward = 999999999999
            rewards[player['name']] = reward
        return rewards

    def T(self, input_state, actions):
        #actions[turn #][player] = action
        #actions is {player: action, player: action, player: action etc}
        base_state = deepcopy(input_state)
        for player in self.players.values():
            if player['name'] == input_state['name']:
                base_state['gold'] += sum([self.territories[t].gold for t in self.territories if input_state[t] == player['name']])
                base_state['gold'] += sum([self.territories[t].gold*2 for t in self.territories if input_state[t] == player['name']+"-REINFORCED"])
                base_state['gold'] -= base_state["force"]*0.1
            else:
                base_state[player["name"]]['gold'] += sum([self.territories[t].gold for t in self.territories if input_state[t] == player['name']])
                base_state[player["name"]]['gold'] += sum([self.territories[t].gold*2 for t in self.territories if input_state[t] == player['name']+"-REINFORCED"])
                base_state[player["name"]]['gold'] -= base_state[player["name"]]["force"]*0.1
        states = [(1.0, base_state)]
        
        #all of the non-conflicting actions
        #reinforce
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "REINFORCE"]:
            # new_states = []
            for state in states:
                # cstate = deepcopy(state[1])
                if player == input_state['name']:
                    state[1][action[1]] = player+"-REINFORCED"
                    state[1][action[1]] = player+"-REINFORCED"
                else:
                    state[1][action[1]] = player+"-REINFORCED"
                    state[1][player][action[1]] = player+"-REINFORCED"
                # new_states += self.chain_actions(state, cstate, 1)
            # states = new_states
        #raise_force
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "RAISE_FORCE"]:
            new_states = []
            for state in states[:]:
                if player == input_state['name']:
                    cstate = deepcopy(state[1])
                    cstate['force'] *= 2
                    cstate['gold'] -= 1000
                    new_states += self.chain_actions(state, cstate, .75)
                else:
                    cstate = deepcopy(state[1])
                    cstate[player]['force'] *= 2
                    cstate[player]['gold'] -= 1000
                    new_states += self.chain_actions(state, cstate, .75)
            states = new_states
        #raise_trust
        #(p,(action, t_p))
        for player, action in [(p,action) for p,action in actions.items() if action[0] == "RAISE_TRUST"]:
            action, t_p = action
            new_states = []
            for state in states:
                if t_p == input_state['name']:
                    cstate = deepcopy(state[1])
                    trust_dict = {"Low":"Med", "Med":"High", "High":"High"}
                    diplomacy_dict = {"Angry":"Neutral", "Neutral":"Allies", "Allies":"Allies"}
                    cstate[player]['Trust'] = trust_dict[cstate[player]['Trust']]
                    if cstate[player]['Trust'] == "High" and cstate[player]['Diplomacy'] in ["Allies","Neutral","Angry"]:
                        cstate[player]['Diplomacy'] = diplomacy_dict[cstate[player]['Diplomacy']]
                    new_states += self.chain_actions(state, cstate, .50)
                else:
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
                if t_p == input_state['name']:
                    cstate = deepcopy(state)
                    cstate.update(m_state)
                    if base_state[player] == "High":
                        new_states += self.chain_actions(state, cstate, .90)
                    elif base_state[player] == "Med":
                        new_states += self.chain_actions(state, cstate, .30)
                    else:
                        new_states += self.chain_actions(state, cstate, 0)
                else:
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
            attacked = [action[1] for p,action in actions.items() if action[0] == "TAKE"]
            territory_takes = {t:[input_state.get(input_state[t].split('-')[0]) or input_state] for t in self.territories if input_state[t] != "WILD" and t in attacked}
            for p, action in takes:
                t, territory = action
                if territory_takes.get(territory):
                    territory_takes[territory].append(input_state.get(p) or input_state)
                else:
                    territory_takes[territory] = [input_state.get(p) or input_state]
            #produce the result of each battle
            for t, players in territory_takes.items():
                if input_state[t] == 'WILD':
                    new_states = []
                    total_force = total_force = sum([player['force'] for player in players]) + self.territories[t].force
                    if len(players) > 1:
                        for state in states[:]:
                            for player in players:
                                cstate = deepcopy(state[1])
                                cstate[t] = player['name']
                                if cstate.get(player['name']):
                                   cstate[player['name']][t] = player['name']
                                for other in players:
                                    if player != other and not (player[other['name']]['Diplomacy'] == "Allied" == other[player['name']]['Diplomacy']):
                                        if cstate.get(other['name']):
                                            cstate[other['name']]['force'] *= .5
                                            cstate[other['name']][t] = player['name']
                                        else:
                                            cstate['force'] *= .5
                                new_states += [(state[0]*player['force']*1.0/total_force, cstate)]
                            new_states.append((state[0]*self.territories[t].force*1.0/total_force, deepcopy(state[1])))
                        states = new_states
                    else:
                        #player on territory
                        player = players[0]
                        for state in states:
                            cstate = deepcopy(state[1])
                            cstate[t] = player['name']
                            if cstate.get(player['name']):
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
                            if cstate.get(player['name']):
                                cstate[player['name']][t] = player['name']
                            for other in players:
                                if player != other and not (player[other['name']]['Diplomacy'] == "Allied" == other[player['name']]['Diplomacy']):
                                    if cstate.get(other['name']):
                                        cstate[other['name']]['force'] *= .5
                                        cstate[other['name']][t] = player['name']
                                    else:
                                        cstate['force'] *= .5
                            new_states += [(state[0]*player['force']*1.0/total_force, cstate)] #self.chain_actions(state, cstate, player['force']*1.0/total_force)
                    states = new_states
        # print states
        # print sum([p for p,s in states])
        return states

    def chain_actions(self, state, state2, p):
        if p != 1 and p:
            prob, state = state
            return [(1.0 * prob * (1.0 - p), state),(1.0*prob*p, state2)]
        elif p == 0:
            return [state]
        else:
            return [(p, state2)]

    def actions(self, state, player=None):
        """Set of actions that can be performed by the player in his current state"""
        actions = []
        player_state = state[player] if player else state
        player = player or state['name']
        raise_forces = [("RAISE_FORCE", player_state['force']*2.0)] if player_state['gold'] >= 1000 else []
        controlled = [t for t in self.territories if state[t] == player]
        owned = set([t for t in self.territories if state[t] in [player, player+"-REINFORCED"]])
        border_territories = set()
        for t in owned:
            border_territories |= self.territories[t].get_borders() - owned
        reenforce_territories = [("REINFORCE", t) for t in controlled]
        take_territories = [("TAKE", t) for t in border_territories if player_state['force'] >= self.territories[t].force]
        raise_trust = [("RAISE_TRUST", other_player['name']) for other_player in self.players.values() if other_player['name'] != player and player_state[other_player['name']]['Trust'] != "High"]
        send_message = []
        return raise_forces + reenforce_territories + take_territories + raise_trust + send_message + [("WAIT",None)]

    def generate_states(self):
        if not self.states:
            self.states = set([self.init])
        for action in self.actions(self.init):
            self.states |= set([x[1] for x in self.T(self.init, action)])
        for state in self.states.copy():
            for action in self.actions(state):
                self.states |= set([x[1] for x in self.T(state, action)])

    def best_policy(self, U):
        """Given an MDP and a utility function U, determine the best policy,
        as a mapping from state to action. (Equation 17.4)"""
        pi = {}
        for s in U.keys():
            pi[s] = argmax(self.actions(s), lambda a:self.expected_utility(a, s, U))
        return pi

    def expected_utility(self, a, s, U):
        "The expected utility of doing a in state s, according to the MDP and U."
        # utils = []
        # for p,s1 in mdp.T(s, a):
        #     if s1 in U:
        #         utils.append(p*U[s1])
        #     else:
        #         utils.append(p*bellman_equation(mdp, s1, U))
        # return sum(utils) #sum([p * U[s1] for (p, s1) in mdp.T(s, a)])
        return sum([p * U.get(s1,0)[s.get('name')] for (p, s1) in self.T(dict(s), a)])

    def multi_bellman_equation(self, state, U, iterations=2):
        h_state = hashdict(state)
        if U.get(h_state):
            return U.get(h_state)
        if not iterations:
            return {p:0 for p in self.players}
        # [{player:action, player:action, player:action}...]
        sets_of_actions = [{self.players.keys()[i] : x for i,x in enumerate(actions)} for actions in product(*[self.actions(state, p) if p != state['name'] else self.actions(state) for p in self.players])]
        states_actions = {hashdict(x):self.T(state, x) for x in sets_of_actions}
        R = {hashdict(action):{p:0 for p in self.players} for action in sets_of_actions}
        for actions, states in states_actions.items():
            for prob, _state in states:
                for p in actions:
                    R[hashdict(actions)][p] += prob*self.multi_bellman_equation(_state, U, iterations-1)[p]
        max_actions = {}
        for actions in R:
            for p in self.players:
                if max_actions.get(p):
                    if max_actions[p][1] < R[actions][p]:
                        max_actions[p] = actions[p],R[actions][p]
                else:
                    max_actions[p] = actions[p], R[actions][p]
        max_actions = hashdict({k:v[0] for k,v in max_actions.items()})
        U[h_state] = {k:v+self.gamma*R[max_actions][k] for k,v in self.R(state).items()}
        self.pi[h_state] = max_actions[self.state['name']]
        # print len(U),iterations
        return U[h_state]
















