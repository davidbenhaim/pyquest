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

    territories = set([A,B,C,D,E,F])
    State = make_State(territories)
    A.status = "CONTROLLED"
    init_state = State(1000, 250, **{t.name:t.status for t in territories})
    # quest = QuestMDP(territories, init_state)
    # quest.generate_states()
    g = Game(False, territories, init_state)
    g.play()


if  __name__ =='__main__':main()