"""
borders might be references to territory original objects vs copies. Should use the name as a string instead of the object

add extra state variables for how healthy a territory is and how they view you. 
PvT relationships. -> rebellion, propaganda, famine, food, territory economy, loyalty, incite rebellion
"""
import operator

class Territory(object):
    __slots__ = ('name', 'gold', 'natural_force','player_forces','borders','status','relations','health','economy','loyalty')
    def __init__(self, name, gold, force, status="WILD", player_forces=0, health=1.0, economy=0.5, loyalty=0.5):
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

    def set_borders(self, borders):
        self.borders = self.borders | borders
        return self
        
    def get_borders(self):
        return {t for t in self.borders}

    def get_gold(self):
        return self.gold*self.health*self.economy

    def get_force(self):
        return self.force

    def print_borders(self):
        print str(self) + ": " + ", ".join([x for x in self.get_borders()])

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.gold, self.natural_force, self.status, self.player_forces))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.__slots__ == other.__slots__:
                for attr in self.__slots__:
                    if getattr(self,attr) != getattr(other,attr): return False
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self):
        t = Territory(self.name, self.gold, self.natural_force, self.status, self.player_forces, self.health, self.economy, self.loyalty)
        t.borders = self.borders
        return t

    def to_dict(self):
        t = self.__dict__.copy()
        del t['borders']
        return t

    def to_list(self):
        return [self.name, self.gold, self.natural_force, self.status, self.player_forces, self.health, self.economy, self.loyalty]


