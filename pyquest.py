from game import Game
from territories import Territory
from quest_state import make_State
from mdp import QuestMDP

def main():
    A = Territory("A", 50, 500)
    B = Territory("B", 25, 1000)
    C = Territory("C", 50, 1000)
    D = Territory("D", 100, 500)
    E = Territory("E", 50, 1000)
    F = Territory("F", 50, 1500)

    A.set_borders(set([B,F]))
    B.set_borders(set([A,C,E]))
    C.set_borders(set([B,D]))
    D.set_borders(set([C,E]))
    E.set_borders(set([B,D]))
    F.set_borders(set([A]))
    P1 = {'name':'P1', 'gold':1000, 'force': 500, 'is_human':True, 'A':'P1', 'D':'P2', 'P2':{'Trust':'Low', 'Diplomacy':'Neutral'}}
    P2 = {'name':'P2', 'gold':1000, 'force': 500, 'is_human':True, 'A':'P1', 'D':'P2', 'P1':{'Trust':'Low', 'Diplomacy':'Neutral'}}
    players = [P1, P2]
    territories = set([A,B,C,D,E,F])
    for player in players:
        player.update({t.name:"WILD" for t in territories if t.name not in player})
    State = make_State(territories)
    A.status = "CONTROLLED"
    init_state = {t.name:"WILD" for t in territories}
    init_state['A'] = "P1"
    init_state['D'] = "P2"
    init_state.update({p['name']: p for p in players})
    # State(1000, 250, **{t.name:t.status for t in territories})
    # quest = QuestMDP(territories, init_state)
    # quest.generate_states()
    g = Game([P1, P2], territories, init_state)
    g.play()


if  __name__ =='__main__':main()