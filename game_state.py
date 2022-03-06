from banana_farm import BananaFarm

BASE_COST = 1250

UPGRADE_COSTS = [
    [0, 500, 600, 3000, 19000, 100000],
    [0, 300, 800, 3500, 10000, 100000],
    [0, 250, 200, 2900, 15000, 60000]
]

class GameState:

    def __init__(self, start_money=0):
        self._money = start_money
        self._farms = []

    @property
    def Money(self):
        """Current amount of money in the GameState."""

        return self._money

    @property
    def Farms(self):
        """A list of all farms currently in the game."""

        return self._farms

    def collect_from_farms(self):
        """Optimally collects money from all farms in the GameState. For
        regular farms, this just means collecting all money generated in a
        single round; for banks, money will only be collected when the bank is
        at its limit."""

        total = 0

        for farm in self.Farms:
            total += farm.tick()

        return total

    def get_upgradable_paths(self, farm):
        """Given a BananaFarm object, returns a list of all upgradable paths
        given the current game state (accounting for, for example, being able
        to afford the upgrade).

        params:
            farm: a BananaFarm object
        """

        upgradable = set()

        for i in range(len(farm.Upgrades)):
            if farm.Upgrades[i] == 0:
                upgradable.add((i + 1) % len(farm.Upgrades))
                upgradable.add((i - 1) % len(farm.Upgrades))

        l = []
        for i in upgradable:
            tier = farm.Upgrades[i]

            if (2 < tier < 5 or tier < 2) \
            and self.Money >= UPGRADE_COSTS[i][tier + 1]:
                l.append(i)

        return l

    def upgrade_path_for_farm(self, farm, path):
        """Given a BananaFarm object and a desired path to upgrade, attempts to
        upgrade said path given the current game state.

        params:
            farm: a BananaFarm object
            path: the index of an upgrade path (one of 0, 1, 2)
        """

        assert path in self.get_upgradable_paths(farm), f"Path {path} cannot \
                be upgraded for {farm}"

        farm.upgrade_path(path)

    def can_buy_farm(self):
        """Returns True if GameState contains enough money to purchase a
        Banana Farm, False otherwise."""

        return self.Money >= BASE_COST

    def buy_farm(self):
        """Attempts to purchase a farm; on success, a new BananaFarm is added
        to the GameState's farm list."""

        assert self.can_buy_farm(), f"Not enough money to buy Banana Farm: \
                have ${self.Money:,}, but costs ${BASE_COST:,}"

        self._farms.append(BananaFarm())
        self._money -= BASE_COST
