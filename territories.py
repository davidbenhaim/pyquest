class Territory:
	def __init__(self, name, gold, force):
		self.name = name
		self.gold = gold
		self.force = force
		self.borders = set()
		self.status = "WILD"

	def set_borders(self, borders):
		self.borders = self.borders | borders
		
	def get_borders(self):
		return set([t.name for t in self.borders])

	def get_gold(self):
		return self.gold

	def get_force(self):
		return self.force

	def print_borders(self):
		print str(self) + ": " + ", ".join([str(x) for x in self.get_borders()])

	def __str__(self):
		return self.name

	def __hash__(self):
		return hash((self.name, self.gold, self.force, self.status))

	def copy(self):
		t = Territory(self.name, self.gold, self.force)
		t.borders = self.borders
		return t


