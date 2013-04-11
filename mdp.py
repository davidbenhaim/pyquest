"""Markov Decision Processes (Chapter 17)

First we define an MDP, and the special case of a GridMDP, in which
states are laid out in a 2-dimensional grid.  We also represent a policy
as a dictionary of {state:action} pairs, and a Utility function as a
dictionary of {state:number} pairs.  We then define the value_iteration
and policy_iteration algorithms."""

from utils import *
from territories import Territory
from quest_state import make_State
from itertools import product
import operator, random
import pdb

def prod(factors):
    return reduce(operator.mul, factors, 1)

class MDP:
    """A Markov Decision Process, defined by an initial state, transition model,
    and reward function. We also keep track of a gamma value, for use by
    algorithms. The transition model is represented somewhat differently from
    the text.  Instead of P(s' | s, a) being a probability number for each
    state/state/action triplet, we instead have T(s, a) return a list of (p, s')
    pairs.  We also keep track of the possible states, terminal states, and
    actions for each state. [page 646]"""

    def __init__(self, init, actlist, terminals, gamma=.9):
        update(self, init=init, actlist=actlist, terminals=terminals,
               gamma=gamma, states=set(), reward={})

    def R(self, state):
        "Return a numeric reward for this state."
        return self.reward[state]

    def T(self, state, action):
        """Transition model.  From a state and an action, return a list
        of (probability, result-state) pairs."""
        abstract

    def actions(self, state):
        """Set of actions that can be performed in this state.  By default, a
        fixed list of actions, except for terminal states. Override this
        method if you need to specialize by state."""
        if state in self.terminals:
            return [None]
        else:
            return self.actlist

class GridMDP(MDP):
    """A two-dimensional grid MDP, as in [Figure 17.1].  All you have to do is
    specify the grid as a list of lists of rewards; use None for an obstacle
    (unreachable state).  Also, you should specify the terminal states.
    An action is an (x, y) unit vector; e.g. (1, 0) means move east."""
    def __init__(self, grid, terminals, init=(0, 0), gamma=.9):
        grid.reverse() ## because we want row 0 on bottom, not on top
        MDP.__init__(self, init, actlist=orientations,
                     terminals=terminals, gamma=gamma)
        update(self, grid=grid, rows=len(grid), cols=len(grid[0]))
        for x in range(self.cols):
            for y in range(self.rows):
                self.reward[x, y] = grid[y][x]
                if grid[y][x] is not None:
                    self.states.add((x, y))

    def T(self, state, action):
        if action is None:
            return [(0.0, state)]
        else:
            return [(0.8, self.go(state, action)),
                    (0.1, self.go(state, turn_right(action))),
                    (0.1, self.go(state, turn_left(action)))]

    def go(self, state, direction):
        "Return the state that results from going in this direction."
        state1 = vector_add(state, direction)
        return if_(state1 in self.states, state1, state)

    def to_grid(self, mapping):
        """Convert a mapping from (x, y) to v into a [[..., v, ...]] grid."""
        return list(reversed([[mapping.get((x,y), None)
                               for x in range(self.cols)]
                              for y in range(self.rows)]))

    def to_arrows(self, policy):
        chars = {(1, 0):'>', (0, 1):'^', (-1, 0):'<', (0, -1):'v', None: '.'}
        return self.to_grid(dict([(s, chars[a]) for (s, a) in policy.items()]))
#______________________________________________________________________________

Fig[17,1] = GridMDP([[-0.04, -0.04, -0.04, +1],
                     [-0.04, None,  -0.04, -1],
                     [-0.04, -0.04, -0.04, -0.04]],
                    terminals=[(3, 2), (3, 1)])
#______________________________________________________________________________

class QuestMDP(MDP):
    def __init__(self, territories, init=None, gamma=.001):
        self.territories = {t.name:t for t in territories}
        self.State = make_State(territories)
        init = init or self.random_init()
        MDP.__init__(self, init, actlist=None, terminals=None, gamma=gamma)

    def random_init(self):
        pass

    def R(self, state):
        "Return a numeric reward for this state."
        reward = state.gold + sum([self.territories[x].gold for x in self.territories if getattr(state, x) in ["CONTROLLED"]]) + sum([self.territories[x].gold*2 for x in self.territories if getattr(state, x) in ["RE-ENFORCED"]]) - 3000*sum([1 for x in self.territories if getattr(state, x) == "WILD"])
        if not [x for x in self.territories if getattr(state, x) in ["CONTROLLED", "RE-ENFORCED"]]:
            return -1.0*999999999999
        if state.gold > 10000: #not [x for x in self.territories if getattr(state, x) == "WILD"]:
            return 999999999999
        return reward

    def T(self, state, action):
        """Transition model.  From a state and an action, return a list
        of (probability, result-state) pairs."""
        new_state = self.State(**state._asdict())
        action, value = action
        states = []
        if action == "RAISE_FORCE":
            territories = {t: getattr(state, t) for t in self.territories}
            states += [(.75, self.State(state.gold, value, **territories)),
                       (.25, self.State(state.gold, value*.5, **territories))]
        elif action == "REDUCE_FORCE":
            territories = {t: getattr(state, t) for t in self.territories}
            states += [(1, self.State(state.gold, value, **territories))]
        elif action == "RE-ENFORCE":
            territories = {t: getattr(state, t) for t in self.territories}
            territories[value] = "RE-ENFORCED"
            states += [(1, self.State(state.gold - self.territories[value].gold*2, state.force, **territories))]
        elif action == "WAIT":
            states += [(1,new_state)]
        else: #TAKE
            territories = {t: getattr(state, t) for t in self.territories}
            territories[value] = "CONTROLLED"
            states += [(.9, self.State(state.gold, state.force, **territories)),
                       (.1, self.State(state.gold, state.force - self.territories[value].force*.5, **{t: getattr(state, t) for t in self.territories}))]
        all_states = []
        #calculate possible rebellions
        for prob, _state in states:
            #rebellion
            controlled = [t for t in self.territories if getattr(_state, t) == "CONTROLLED"]
            r = .2
            pastabilities = product((.2,.8),repeat=len(controlled))
            for pasta in pastabilities:
                p = prod(pasta)
                rebelled = [controlled[i] for i,s in enumerate(pasta) if s == r]
                territories = {t: getattr(_state, t) for t in self.territories}
                for t in territories:
                    if t in rebelled:
                        territories[t] = "WILD"
                all_states += [(prob*p, self.State(_state.gold, _state.force, **territories))]
        for p, _state in all_states:
            dict_state = _state._asdict()
            dict_state['gold'] += sum([self.territories[x].gold for x in self.territories if getattr(_state, x) in ["CONTROLLED"]]) + sum([self.territories[x].gold*2 for x in self.territories if getattr(_state, x) in ["RE-ENFORCED"]]) - _state.force*0.5
            _state = self.State(**dict_state)
        return all_states

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
        return raise_forces + reduce_forces + reenforce_territories + take_territories+[("WAIT",None)]

    def generate_states(self):
        if not self.states:
            self.states = set([self.init])
        for action in self.actions(self.init):
            self.states |= set([x[1] for x in self.T(self.init, action)])
        for state in self.states.copy():
            for action in self.actions(state):
                self.states |= set([x[1] for x in self.T(state, action)])


#______________________________________________________________________________

# A = Territory("A", 50, 500)
# B = Territory("B", 25, 250)
# A.set_borders(set([B]))
# B.set_borders(set([A]))

# territories = set([A,B])
# self.State = make_State(territories)
# A.status = "CONTROLLED"
# init_state = self.State(1000, 250, **{t.name:t.status for t in territories})
# quest = QuestMDP({t.name:t for t in territories}, init_state)
# quest.generate_states()

#______________________________________________________________________________

def bellman_equation(mdp, state, U, iterations=10):
    if U.get(state):
        return U.get(state)
    if not iterations:
        return 0
    U[state] = mdp.R(state) + mdp.gamma*max([sum([p * bellman_equation(mdp, s1, U, iterations-1) for (p, s1) in mdp.T(state, a)]) for a in mdp.actions(state)])
    return U[state]

def value_iteration(mdp, epsilon=0.001):
    "Solving an MDP by value iteration. [Fig. 17.4]"
    U1 = dict([(s, 0) for s in mdp.states])
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    while True:
        U = U1.copy()
        delta = 0
        for s in mdp.states:
            # U1[s] = R(s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)])
            #                             for a in mdp.actions(s)])
            U1[s] = bellman_equation(mdp, s, U)
            delta = max(delta, abs(U1[s] - U[s]))
        if delta < epsilon * (1 - gamma) / gamma:
             return U

def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. (Equation 17.4)"""
    pi = {}
    for s in mdp.states:
        pi[s] = argmax(mdp.actions(s), lambda a:expected_utility(a, s, U, mdp))
    return pi

def expected_utility(a, s, U, mdp):
    "The expected utility of doing a in state s, according to the MDP and U."
    # utils = []
    # for p,s1 in mdp.T(s, a):
    #     if s1 in U:
    #         utils.append(p*U[s1])
    #     else:
    #         utils.append(p*bellman_equation(mdp, s1, U))
    # return sum(utils) #sum([p * U[s1] for (p, s1) in mdp.T(s, a)])
    return sum([p * U.get(s1,0) for (p, s1) in mdp.T(s, a)])

#______________________________________________________________________________

def policy_iteration(mdp):
    "Solve an MDP by policy iteration [Fig. 17.7]"
    U = dict([(s, 0) for s in mdp.states])
    pi = dict([(s, random.choice(mdp.actions(s))) for s in mdp.states])
    while True:
        U = policy_evaluation(pi, U, mdp)
        unchanged = True
        for s in mdp.states:
            a = argmax(mdp.actions(s), lambda a: expected_utility(a,s,U,mdp))
            if a != pi[s]:
                pi[s] = a
                unchanged = False
        if unchanged:
            return pi

def policy_evaluation(pi, U, mdp, k=20):
    """Return an updated utility mapping U from each state in the MDP to its
    utility, using an approximation (modified policy iteration)."""
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    for i in range(k):
        for s in mdp.states:
            U[s] = bellman_equation(mdp, s, U)#R(s) + gamma * sum([p * U[s1] for (p, s1) in T(s, pi[s])])
    return U

# pi = best_policy(quest, value_iteration(quest))
# for s in pi:
#     print s, pi[s]
# pdb.set_trace()
__doc__ += """
>>> pi = best_policy(Fig[17,1], value_iteration(Fig[17,1], .01))

>>> Fig[17,1].to_arrows(pi)
[['>', '>', '>', '.'], ['^', None, '^', '.'], ['^', '>', '^', '<']]

>>> print_table(Fig[17,1].to_arrows(pi))
>   >      >   .
^   None   ^   .
^   >      ^   <

>>> print_table(Fig[17,1].to_arrows(policy_iteration(Fig[17,1])))
>   >      >   .
^   None   ^   .
^   >      ^   <
"""

__doc__ += random_tests("""
>>> pi
{(3, 2): None, (3, 1): None, (3, 0): (-1, 0), (2, 1): (0, 1), (0, 2): (1, 0), (1, 0): (1, 0), (0, 0): (0, 1), (1, 2): (1, 0), (2, 0): (0, 1), (0, 1): (0, 1), (2, 2): (1, 0)}

>>> value_iteration(Fig[17,1], .01)
{(3, 2): 1.0, (3, 1): -1.0, (3, 0): 0.12958868267972745, (0, 1): 0.39810203830605462, (0, 2): 0.50928545646220924, (1, 0): 0.25348746162470537, (0, 0): 0.29543540628363629, (1, 2): 0.64958064617168676, (2, 0): 0.34461306281476806, (2, 1): 0.48643676237737926, (2, 2): 0.79536093684710951}

>>> policy_iteration(Fig[17,1])
{(3, 2): None, (3, 1): None, (3, 0): (0, -1), (2, 1): (-1, 0), (0, 2): (1, 0), (1, 0): (1, 0), (0, 0): (1, 0), (1, 2): (1, 0), (2, 0): (1, 0), (0, 1): (1, 0), (2, 2): (1, 0)}

""")

