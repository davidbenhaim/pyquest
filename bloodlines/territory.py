"""
borders might be references to territory original objects vs copies. Should use the name as a string instead of the object

add extra state variables for how healthy a territory is and how they view you. 
PvT relationships. -> rebellion, propaganda, famine, food, territory economy, loyalty, incite rebellion
"""

class Territory:
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
        return set([t for t in self.borders])

    def get_gold(self):
        return self.gold*self.health*self.economy

    def get_force(self):
        return self.force

    def print_borders(self):
        print str(self) + ": " + ", ".join([x.name for x in self.get_borders()])

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.gold, self.natural_force, self.status, self.player_forces))

    def __eq__(self, other):
        s = self.__dict__.copy()
        o = other.__dict__.copy()
        del s['borders']
        del o['borders']
        return o == s

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self):
        return Territory(self.name, self.gold, self.natural_force, self.status, self.player_forces, self.health, self.economy, self.loyalty).set_borders(self.borders)


