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

Magnarus.set_borders(set([Pineland.name, Snowholt.name]))
Tenebris.set_borders(set([Snowholt.name, Wilderbush.name]))
Kotaris.set_borders(set([Highmont.name, Wilderbush.name]))
Jakelli.set_borders(set([Highmont.name, Morlyn.name]))
Lorlea.set_borders(set([Lochton.name]))
Orwyn.set_borders(set([Pineland.name, Orwall.name]))

Pineland.set_borders(set([Magnarus.name, Orwyn.name, Snowholt.name, Orwall.name]))
Snowholt.set_borders(set([Magnarus.name, Tenebris.name, Orwall.name, Wilderbush.name]))
Wilderbush.set_borders(set([Kotaris.name, Tenebris.name, Orwall.name, Snowholt.name, Highmont.name]))
Orwall.set_borders(set([Orwyn.name, Pineland.name, Snowholt.name, Wilderbush.name, Highmont.name, Lochton.name]))
Lochton.set_borders(set([Lorlea.name, Morlyn.name, Highmont.name, Orwall.name]))
Morlyn.set_borders(set([Jakelli.name, Highmont.name, Lochton.name]))
Highmont.set_borders(set([Kotaris.name, Jakelli.name, Morlyn.name, Lochton.name, Orwall.name, Wilderbush.name]))

gamemap = {t.name:t for t in set([Magnarus, Tenebris, Kotaris, Jakelli, Lorlea, Orwyn, Pineland, Snowholt, Wilderbush, Orwall, Lochton, Morlyn, Highmont])}