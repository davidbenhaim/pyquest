from territory import Territory

#Name, Gold, Natural Force Bonus

#Main Kingdoms
Magnarus = Territory("Magnarus", 100, 1000)
Tenebris = Territory("Tenebris", 100, 1000)
Kotaris = Territory("Kotaris", 100, 1000)
Jakelli = Territory("Jakelli", 300, 1000)
Lorlea = Territory("Lorlea", 100, 1000)
Orwyn = Territory("Orwyn", 100, 1000)

#Middle Territories
Pineland = Territory("Pineland", 300, 100)
Snowholt = Territory("Snowholt", 300, 1000)
Wilderbush = Territory("Wilderbush", 300, 100)
Orwall = Territory("Orwall", 500, 1500)
Lochton = Territory("Lochton", 1000, 1500)
Morlyn = Territory("Morlyn", 100, 200)
Highmont = Territory("Highmont", 1000, 1500)

Magnarus.set_borders(set([Pineland, Snowholt]))
Tenebris.set_borders(set([Snowholt, Wilderbush]))
Kotaris.set_borders(set([Highmont, Wilderbush]))
Jakelli.set_borders(set([Highmont, Morlyn]))
Lorlea.set_borders(set([Lochton]))
Orwyn.set_borders(set([Pineland, Orwall]))

Pineland.set_borders(set([Magnarus, Orwyn, Snowholt, Orwall]))
Snowholt.set_borders(set([Magnarus, Tenebris, Orwall, Wilderbush]))
Wilderbush.set_borders(set([Kotaris, Tenebris, Orwall, Snowholt, Highmont]))
Orwall.set_borders(set([Orwyn, Pineland, Snowholt, Wilderbush, Highmont, Lochton]))
Lochton.set_borders(set([Lorlea, Morlyn, Highmont, Orwall]))
Morlyn.set_borders(set([Jakelli, Highmont, Lochton]))
Highmont.set_borders(set([Kotaris, Jakelli, Morlyn, Lochton, Orwall, Wilderbush]))

gamemap = set([Magnarus, Tenebris, Kotaris, Jakelli, Lorlea, Orwyn, Pineland, Snowholt, Wilderbush, Orwall, Lochton, Morlyn, Highmont])