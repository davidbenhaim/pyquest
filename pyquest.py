from game import Game
from territories import Territory
from quest_state import make_State
from mdp import QuestMDP

def main():
    A = Territory("A", 100, 1000)
    B = Territory("B", 100, 1000)
    C = Territory("C", 100, 1000)
    D = Territory("D", 300, 1000)
    E = Territory("E", 50, 1000)
    F = Territory("F", 50, 1500)

    A.set_borders(set([D]))
    B.set_borders(set([D]))
    C.set_borders(set([D]))
    D.set_borders(set([A,B,C]))
    E.set_borders(set([B,D]))
    F.set_borders(set([A]))
    P1 = {'name':'P1', 'gold':1000, 'force': 500, 'is_human':True, 'A':'P1', 'B':'P2', 'C':'P3', 'D':'WILD', 'P2':{'name':'P2', 'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500, 'P1': {'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}, 'P3': {'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}},'P3':{'name':'P3', 'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500, 'P1':{'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500},'P2':{'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}}}
    P2 = {'name':'P2', 'gold':1000, 'force': 500, 'is_human':True, 'A':'P1', 'B':'P2', 'C':'P3', 'D':'WILD', 'P1':{'name':'P1', 'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500, 'P2': {'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}, 'P3': {'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}},'P3':{'name':'P3', 'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500, 'P1':{'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500},'P2':{'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}}}
    P3 = {'name':'P3', 'gold':1000, 'force': 500, 'is_human':False, 'A':'P1', 'B':'P2', 'C':'P3', 'D':'WILD', 'P1':{'name':'P1', 'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500, 'P2': {'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}, 'P3': {'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}},'P2':{'name':'P2', 'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500, 'P1':{'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500},'P3':{'Trust':'Low', 'Diplomacy':'Neutral', 'gold':1000, 'force': 500}}}
    players = [P1, P2, P3]
    territories = set([A,B,C,D])
    for player in players:
        player.update({t.name:"WILD" for t in territories if t.name not in player})
    State = make_State(territories)
    A.status = "CONTROLLED"
    init_state = {t.name:"WILD" for t in territories}
    init_state['A'] = "P1"
    init_state['B'] = "P2"
    init_state['C'] = "P3"
    init_state.update({p['name']: p for p in players})
    # init_state = {'A': 'P1-REINFORCED', 'P2': {'A': 'P1', 'C': 'P1-REINFORCED', 'P1': {'Trust': 'Low', 'Diplomacy': 'War'}, 'force': 1000, 'name': 'P2', 'is_human': True, 'F': 'WILD', 'B': 'WILD', 'E': 'WILD', 'gold': 750.0, 'D': 'P2'}, 'C': 'P1-REINFORCED', 'B': 'P1-REINFORCED', 'E': 'WILD', 'D': 'P2', 'F': 'WILD', 'P1': {'A': 'P1-REINFORCED', 'P2': {'Trust': 'Low', 'Diplomacy': 'Neutral'}, 'C': 'P1-REINFORCED', 'B': 'P1-REINFORCED', 'force': 500.0, 'name': 'P1', 'is_human': True, 'F': 'WILD', 'E': 'WILD', 'gold': 425.0, 'D': 'P2'}}
    # State(1000, 250, **{t.name:t.status for t in territories})
    # quest = QuestMDP(territories, init_state)
    # quest.generate_states()
    g = Game(players, territories, init_state)
    g.play()


if  __name__ =='__main__':main()