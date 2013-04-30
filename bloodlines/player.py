# from hashdict import *

class Player:
    """
    PlayerState = {"known":{"territories": [{"force","state", "gold"}],
                            "total_gold":0},
                   "modeled":{"players":{models of other players}}
                  }

    ModelOfAPlayer = {"Trust":"High/Med/Low",
                      "Diplomacy": "Allies/Neutral/Angry/War",
                      for each player: p_v_otherplayer - how they feel about other players "Allies/Neutral/Angry/War",
                      "Territories":[] }
    """
    def __init__(self, name, game_model=None, is_human=True):
        self.name = name
        self.state = game_model
        self.is_human = is_human
        self.gold = 100

    def get_diplomacy(self, other_player):
        return self.state.get_diplomacy(self, other_player)

    def R(self, game):
        pass

    def set_gold(self, gold):
        self.gold = gold

    def get_gold(self):
        return self.gold

    def copy(self):
        p = Player(self.name, self.state.copy(), self.is_human)
        p.set_gold(self.get_gold())
        return p

    def to_dict(self):
        return dict((k, v) for (k, v) in self.__dict__.iteritems() if not k in ['state', 'is_human'])

    def __eq__(self, other):
        s = self.to_dict().copy()
        o = other.to_dict().copy()
        return o == s

    def __ne__(self, other):
        return not self.__eq__(other)

class PlayerModel:
    def __init__(self, player, game_model=None):
        self.name = player.name
        self.state = game_model
        self.gold = player.gold

    def get_diplomacy(self, other_player):
        if self.state:
            return self.state.get_diplomacy(self, other_player)
        return None

    def R(self, game):
        pass

    def set_gold(self, gold):
        self.gold = gold

    def get_gold(self):
        return self.gold

    def copy(self):
        p = PlayerModel(self, self.state.copy() if self.state else None)
        return p

    def to_dict(self):
        return dict((k, v) for (k, v) in self.__dict__.iteritems() if not k in ['state'])

    def __eq__(self, other):
        s = self.to_dict().copy()
        o = other.to_dict().copy()
        return o == s

    def __ne__(self, other):
        return not self.__eq__(other)