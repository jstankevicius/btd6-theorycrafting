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

        self._money += total
        return total

    def get_upgradable_paths(self, farm):
        """Given a BananaFarm object, returns a list of all upgradable paths
        given the current game state (accounting for, for example, being able
        to afford the upgrade).

        params:
            farm: a BananaFarm object
        """

        # Sort indices by tier. If middle upgrade is > 0, we know the last tier
        # should be excluded.
        paths = sorted([(path, tier) \
                for path, tier in enumerate(farm.Upgrades)], key=lambda x:-x[1])

        # Check for x-y-0, where x >= y > 0. In this case, we cannot upgrade
        # the third path, so remove it.
        l = []

        if paths[1][1] > 0:
            del paths[2]
        else:
            l.append(paths[2][0])

        # 1st path (being highest tier) can always be considered upgradable so
        # long as it is below tier 5.
        if paths[0][1] < 5:
            l.append(paths[0][0])

        # 2nd path can be upgraded in two cases:
        # 1st path is tier 2 or below
        # 1st path is tier 3 or above and 2nd path is below tier 2
        if paths[0][1] < 3:
            l.append(paths[1][0])
        elif paths[1][1] < 2:
            l.append(paths[1][0])

        # Now filter by whether we can actually afford the upgrades:
        upgradable = [i for i in l \
                if self.Money >= UPGRADE_COSTS[i][farm.Upgrades[i] + 1]]

        return sorted(upgradable)

    def upgrade_path_for_farm(self, farm, path):
        """Given a BananaFarm object and a desired path to upgrade, attempts to
        upgrade said path given the current game state.

        params:
            farm: a BananaFarm object
            path: the index of an upgrade path (one of 0, 1, 2)
        """

        assert path in self.get_upgradable_paths(farm), f"Path {path} cannot be upgraded for {farm}"
        upgrade_cost = UPGRADE_COSTS[path][farm.Upgrades[path] + 1]
        self._money -= upgrade_cost
        farm.upgrade_path(path)

    def can_buy_farm(self):
        """Returns True if GameState contains enough money to purchase a
        Banana Farm, False otherwise."""

        return self.Money >= BASE_COST

    def buy_farm(self):
        """Attempts to purchase a farm; on success, a new BananaFarm is added
        to the GameState's farm list."""

        assert self.can_buy_farm(), "Not enough money to buy Banana Farm: have ${self.Money:,}, but costs ${BASE_COST:,}"

        self._farms.append(BananaFarm())
        self._money -= BASE_COST
