from territories import Territory
from quest_state import make_State
from bisect import bisect
from random import random
from itertools import product
import time
import mdp
import pdb

class Game:
    def __init__(self, player, territories, start_state):
        self.State = make_State(territories)
        self.player = player
        self.territories = {t.name:t for t in territories}
        self.state = start_state
        self.turn = 0
        init_state = self.state
        self.comp = mdp.QuestMDP(set(self.territories.values()), init_state)
        if not self.player:
            self.comp.generate_states()
            self.policy = mdp.best_policy(self.comp, mdp.value_iteration(self.comp))
            print self.state

    def check_game_over(self):
        state = self.state
        if not [x for x in self.territories if getattr(state, x) in ["CONTROLLED", "RE-ENFORCED"]]:
            self.print_state()
            return True
        if self.comp.R(self.state) == 999999999999:#len([x for x in self.territories if getattr(state, x) in ["CONTROLLED", "RE-ENFORCED"]]) == len(self.territories):
            self.print_state()
            return True
        return False

    def play(self):
        for territory in self.territories.values():
            print territory.name+" - Gold: %i Force: %i" % (territory.gold, territory.force)
        while not self.check_game_over():
            self.print_state()
            self.take_turn()

    def take_turn(self):
        if self.player:
            actions = self.actions(self.state)
            print "Actions available:"
            for i,action in enumerate(actions):
                print '%i: %s' % (i, action)
            usr_input = None
            while usr_input not in [i for i in range(len(actions))]:
                usr_input = input("Action: ")
            self.do_action(actions[usr_input])
            print action
            self.print_state()
        else:
            # time.sleep(3)
            if self.state not in self.policy:
                self.comp = mdp.QuestMDP(set(self.territories.values()), self.state)
                self.comp.generate_states()
                self.policy = mdp.best_policy(self.comp, mdp.value_iteration(self.comp))
            # pdb.set_trace()
            action = self.policy[self.state]
            self.do_action(action)
            print action



    def chance(self, states):
        P = [p for p,a in states]
        cdf = [P[0]]
        for i in xrange(1, len(P)):
            cdf.append(cdf[-1] + P[i])
        random_ind = bisect(cdf,random())
        return states[random_ind]

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        actions = []
        raise_forces = [("RAISE_FORCE", state.force*2.0)]
        reduce_forces = [] #[("REDUCE_FORCE", state.force/2.0)]
        controlled = [t for t in self.territories if getattr(state, t) == "CONTROLLED"]
        owned = set([t for t in self.territories if getattr(state, t) in ["CONTROLLED", "RE-ENFORCED"]])
        border_territories = set()
        for t in owned:
            border_territories |= self.territories[t].get_borders() - owned
        reenforce_territories = [("RE-ENFORCE", t) for t in controlled]
        take_territories = [("TAKE", t) for t in border_territories if state.force >= self.territories[t].force]
        return raise_forces + reduce_forces + reenforce_territories + take_territories + [("WAIT",None)]

    #incredibly innefficiant plant function
    def do_action(self, action):
        State = self.State
        state = self.state
        """Performs an action by the player and updates the state of the game to the next state"""
        new_state = State(**state._asdict())
        action, value = action
        states = []
        if action == "RAISE_FORCE":
            territories = {t: getattr(state, t) for t in self.territories}
            states += [(.75, State(state.gold, value, **territories)),
                       (.25, State(state.gold, value*.5, **territories))]
        elif action == "REDUCE_FORCE":
            territories = {t: getattr(state, t) for t in self.territories}
            states += [(1, State(state.gold, value, **territories))]
        elif action == "RE-ENFORCE":
            territories = {t: getattr(state, t) for t in self.territories}
            territories[value] = "RE-ENFORCED"
            states += [(1, State(state.gold - self.territories[value].gold*2, state.force, **territories))]
        elif action == "WAIT":
            states += [(1,new_state)]
        else: #TAKE
            territories = {t: getattr(state, t) for t in self.territories}
            territories[value] = "CONTROLLED"
            states += [(.9, State(state.gold, state.force, **territories)),
                       (.1, State(state.gold, state.force - self.territories[value].force*.5, **{t: getattr(state, t) for t in self.territories}))]
        all_states = []
        #calculate possible rebellions
        for prob, state in states:
            #rebellion
            controlled = [t for t in self.territories if getattr(state, t) == "CONTROLLED"]
            r = .2
            pastabilities = product((.2,.8),repeat=len(controlled))
            for pasta in pastabilities:
                p = mdp.prod(pasta)
                rebelled = [controlled[i] for i,s in enumerate(pasta) if s == r]
                territories = {t: getattr(state, t) for t in self.territories}
                for t in territories:
                    if t in rebelled:
                        territories[t] = "WILD"
                all_states += [(prob*p, State(state.gold, state.force, **territories))]
        final_states = []
        for p, state in all_states:
            dict_state = state._asdict()
            dict_state['gold'] += sum([self.territories[x].gold for x in self.territories if getattr(state, x) in ["CONTROLLED"]]) + sum([self.territories[x].gold*2 for x in self.territories if getattr(state, x) in ["RE-ENFORCED"]]) - state.force*.1
            state = State(**dict_state)
            final_states.append((p, state))
        self.state = self.chance(final_states)[1]
    
    def print_state(self):
        print self.state



