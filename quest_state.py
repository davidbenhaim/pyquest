from collections import namedtuple

def make_State(territories):
	attrs = ["gold", "force"] + [k.name for k in territories]
	State = namedtuple("State", attrs)
	def state_hash(self):
		return hash(tuple([(f,getattr(self,f)) for f in self._fields]))
	State.__hash__ = state_hash
	return State

# class State:
# 	def __init__(self, gold, force, territories):
# 		self.gold = gold
# 		self.force = force
# 		self.territories = territories

# 	def copy(self):
# 		return State(self.gold, self.force, self.territories)

# 	def reenforce_territory(self, territory):
# 		self.change_territory_state(territory, "RE-ENFORCED")
# 		return self.territories

# 	def take_territory(self, territory):
# 		self.change_territory_state(territory, "CONTROLLED")
# 		return self.territories

# 	def rebel_territories(self, territories):
# 		for territory in territories:
# 			territory.status = "WILD"
# 		return territories

# 	def change_territory_state(self, territory, state):
# 		for t in self.territories:
# 			if t == territory:
# 				t.status = state

# 	def to_tuple_dict(self):
# 		d = {"gold": self.gold, "force": self.force}
# 		for t in self.territories:
# 			d[t.name] = t.status
# 		return frozenset([(k,v) for k,v in d.items()])

# 	def __hash__(self):
# 		d = self.to_tuple_dict()
# 		return hash(d)