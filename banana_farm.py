# Let's assume we start with enough cash for a single banana farm. Assuming we
# take either the 4-2-0 or the 2-4-0 route, which ends up generating more money
# by round 100?

# Initially, a regular farm (0-0-0) produces 4 bunches per round worth $20
# each. Top path upgrades are as follows:
# 1-0-0 ($500): 6 bunches per round ($120)
# 2-0-0 ($600): 8 bunches per round ($160)
# 3-0-0 ($3,000): 16 bunches per round ($320)
# 4-0-0 ($19,000): 5 crates worth $300 each ($1500)
# 5-0-0 ($100,000): crates are worth $1200 each and all 4-0-0 crates are worth
#                   25% more. Generates $6000 per round.
#
# Middle path upgrades:
# 0-1-0 ($300): worthless, since it just makes bananas last longer
# 0-2-0 ($800): bananas worth 25% more, rounded down
# 0-3-0 ($3,500): store $230 per round and gain 15% interest at round end
# 0-4-0 ($10,000): increase storage to $10k and unlock IMF loan ability
# 0-5-0 ($100,000): free $10k up to twice a round (every 60s)
#
# Bottom path upgrades:
# 0-0-1 ($250): worthless
# 0-0-2 ($200): worthless
# 0-0-3 ($2,900): generates a flat $320 per round
# 0-0-4 ($15,000): generates a flat $1120 per round
# 0-0-5 ($60,000): generates a flat $5120 per round
BASE_COST = 1250
BASE_BPR = 4

UPGRADE_COSTS = [
    [0, 500, 600, 3000, 19000, 100000],
    [0, 300, 800, 3500, 10000, 100000],
    [0, 250, 200, 2900, 15000, 60000]
]

# For each upgrade, how many bananas on top of the base BPR are generated.
UPGRADE_BPR_MODIFIERS = [
    [0, 2, 4, 12, 1, 1],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 12, 12, 12]
]

# For each upgrade, the worth of a single banana:
UPGRADE_MPB = [
    [20, 20, 20, 20, 300, 1200],
    [20, 20, 20, 57.5, 57.5, 57.5],
    [20, 20, 20, 20, 70, 70]
]

# Order of tier upgrades (0 for 1st tier, 1 for 2nd tier, 2 for 3rd tier)
upgrade_order = [0, 0, 0, 0, 1, 1] # 4-0-0 -> 4-2-0


class Tower:

    def __init__(self, path1, path2, path3):
        self._upgrades = [path1, path2, path3]

    @property
    def Upgrades(self):
        return self._upgrades

    def get_path(self, path):
        return self._upgrades[path]

    def upgrade_path(self, path):
        """Attempt to upgrade a tower's path to the next tier. If the operation
        is not permitted, fail with an exception."""

        # If we're already at the maximum tier, fail.
        if self._upgrades[path] == 5:
            raise Exception(f"Path {path} is already at Tier 5")

        # If we're upgrading into Tier 3 and some other path is already Tier 3
        # or above, fail.
        if self._upgrades[path] + 1 == 3:
            for i in range(3):
                if i != path and _self.upgrades[i] > 2:
                    raise Exception(f"Tried to upgrade Path {path} to Tier 3 \
                            but Path {i} is Tier {_self.upgrades[i]}")

        self._upgrades[path] += 1


class BananaFarm(Tower):

    def __init__(self, path1=0, path2=0, path3=0):
        super().__init__(path1, path2, path3)

        # Money currently stored in the farm. Only relevant in middle-path
        # upgrades, since otherwise money_stored gets reset every tick.
        self.money_stored = 0

    def get_bpr(self):
        """Returns this farm's BPR (bananas per round)."""

        # Take base BPR, add all modifiers on top of it.
        bpr_mods = sum([UPGRADE_BPR_MODIFIERS[i][self.Upgrades[i]] \
                for i in range(3)])

        return BASE_BPR + bpr_mods

    def get_mpb(self):
        """Returns this farm's MPB (money per banana)."""

        # Only one upgrade path will ever have a non-20 MPB, so we can just
        # take the maximum MPB among all paths and return that.
        mpb = 20
        for i in range(3):
            mpb = max(UPGRADE_MPB[i][self.Upgrades[i]], mpb)

        # Check for special crosspaths with banks:
        if self.Upgrades[1] >= 3 and self.Upgrades[0] > 0:
            mpb = 45 if self.Upgrades[0] == 1 else 38.75

        return mpb

    def tick(self):
        """Simulates a round passing for this farm. Returns the total amount of
        money added to the total this round."""
        bpr = self.get_bpr()
        mpb = self.get_mpb()
        mpr = bpr*mpb

        # Check for x-2-x path:
        if self.Upgrades[1] == 2:
            mpr = int(mpr*1.25)

        # Are we a bank? If so, take MPR and apply interest. Also check for
        # limits.
        elif self.Upgrades[1] >= 3:
            limit = 7000 if self.Upgrades[1] == 3 else 10000
            self.money_stored = min((self.money_stored + mpr)*1.15, limit)

            # If the bank has reached its limit, collect immediately.
            if self.money_stored == limit:
                self.money_stored = 0
                return limit
            else:
                return 0

        # If we're not a bank, we just return MPR
        return mpr

    def __str__(self):
        bpr = self.get_bpr()
        mpb = self.get_mpb()
        mpr = bpr*mpb
        upgrades = '-'.join([str(i) for i in self.Upgrades])
        return f"Banana Farm ({upgrades}): BPR={bpr}, MPB=${mpb}, MPR=${mpr}"

