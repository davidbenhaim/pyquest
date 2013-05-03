from territory import Territory
from territories import gamemap
import cProfile


class Territory(object):
    __slots__ = ('name', 'gold', 'natural_force','player_forces','borders','status','relations','health','economy','loyalty')
    def __init__(self, name="", gold=0, force=0, status="WILD", player_forces=0, health=1.0, economy=0.5, loyalty=0.5):
        self.name = name
        self.gold = gold
        self.natural_force = force
        self.player_forces = player_forces
        self.borders = set()
        self.status = status
        self.relations = {}
        self.health = health
        self.economy = economy
        self.loyalty = loyalty

    def copy(self):
        o = object.__new__(Territory)
        o.name = self.name
        o.gold = self.gold
        o.natural_force = self.natural_force
        o.player_forces = self.player_forces
        o.borders = self.borders
        o.status = self.status
        o.relations = self.relations
        o.health = self.health
        o.economy = self.economy
        o.loyalty = self.loyalty
        return o


def j():
    t=Territory('s',100,100,"WILD",1,1.0,.5,.5)
    for i in range(3900):
        t.copy()

cProfile.run('j()')