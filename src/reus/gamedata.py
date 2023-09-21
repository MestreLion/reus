# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""
Game Data, taken from Wiki and converted to model classes
"""
from __future__ import annotations

import logging

from .model import *  # '*' also re-exports symbols

log = logging.getLogger(__name__)


# fmt: off
class LesserHerd(Aspect):      BONUS = Yields(food=1), 3
class PotentHerd(Aspect):      BONUS = Yields(food=1), Yields(food=2), 7
class GreaterHerd(Aspect):     BONUS = Yields(food=2), Yields(food=3), 14
class SublimeHerd(Aspect):     BONUS = Yields(food=3), Yields(food=4), 30
class LesserHunt(Aspect):      BONUS = Yields(food=1), 3
class PotentHunt(Aspect):      BONUS = Yields(food=1, danger=1), Yields(food=2, danger=1), 7
class GreaterHunt(Aspect):     BONUS = Yields(food=2, danger=2), Yields(food=3, danger=2), 14
class SublimeHunt(Aspect):     BONUS = Yields(food=3, danger=2), Yields(food=4, danger=2), 30
class LesserPredator(Aspect):  BONUS = Yields(gold=1), 3
class PotentPredator(Aspect):  BONUS = Yields(gold=1, danger=1), Yields(gold=2, danger=1), 7
class GreaterPredator(Aspect): BONUS = Yields(gold=2, danger=2), Yields(gold=3, danger=2), 14
class SublimePredator(Aspect): BONUS = Yields(gold=3, danger=2), Yields(gold=4, danger=2), 30
# fmt: on


class Fish(Animal):
    """Base class for level 1, tier 1 fish"""


class Mackerel(Fish):
    SLOTS = 1
    BASE = Yields(food=2)
    SYMB = Data(bonus=1, max=2)

    @property
    def range(self) -> int:
        return super().range + self.massive_school()

    def massive_school(self) -> int:
        """
        Massive School: +1 Range for each other Mackerel within Animal Range.
        Boosts up to 2 times.
        """
        # NOTE: "up to 2 times" could be interpreted differently if the bonus per each
        # other Mackerel was more than +1
        bonus = 0
        for _ in range(self.SYMB.max):
            bonus = min(
                self.SYMB.max, self.SYMB.bonus * len(self.nearby(Mackerel, self.RANGE + bonus))
            )
            if bonus in (0, self.SYMB.max):
                return bonus
        return bonus


class GreatMackerel(Mackerel):
    SLOTS = 1  # Simple: reduced number of slots
    BASE = Yields(food=4)


class SuperiorMackerel(GreatMackerel):
    SLOTS = 2  # Simple: reduced number of slots
    BASE = Yields(food=8)


class Clownfish(Fish):
    SLOTS = 1
    BASE = Yields(gold=2)
    SYMB = Yields(gold=2)

    @property
    def yields(self) -> Yields:
        return super().yields + self.coral_dweller()

    def coral_dweller(self) -> Yields:
        """Coral Dweller: +2 Wealth if next to another Clownfish or Parrotfish."""
        return self.SYMB if self.nearby((Clownfish, Parrotfish)) else Yields()


class GreatClownfish(Clownfish):
    SLOTS = 2
    BASE = Yields(gold=4)
    SYMB = Yields(gold=4)


class SuperiorClownfish(GreatClownfish):
    SLOTS = 3
    BASE = Yields(gold=8)
    SYMB = Yields(gold=6)


class Parrotfish(Fish):
    SLOTS = 2
    BASE = Yields(gold=2)
    SYMB = Yields(gold=1, tech=1)

    @property
    def yields(self) -> Yields:
        return super().yields + self.barrier_dweller()

    def barrier_dweller(self) -> Yields:
        """
        Barrier Dweller: +1 Wealth and +1 Technology
        for each other different fish type within Animal Range.
        """
        return self.SYMB * len(set(fish.kind for fish in self.within_range(Fish)))


class GreatParrotfish(Parrotfish):
    SLOTS = 3
    BASE = Yields(gold=3)
    SYMB = Yields(gold=2, tech=2)


class SuperiorParrotfish(GreatParrotfish):
    SLOTS = 4
    BASE = Yields(gold=6)
    SYMB = Yields(gold=3, tech=3)


class Seabass(Fish):
    SLOTS = 2
    BASE = Yields(food=2)
    SYMB = Yields(food=3)

    @property
    def yields(self) -> Yields:
        return super().yields + self.predator()

    def predator(self) -> Yields:
        """Predator: +3 Food if there is a Mackerel or Clownfish within Animal Range."""
        return self.SYMB if self.within_range((Mackerel, Clownfish)) else Yields()


class GreatSeabass(Seabass):
    SLOTS = 3
    BASE = Yields(food=4)
    SYMB = Yields(food=6)


class SuperiorSeabass(GreatSeabass):
    SLOTS = 4
    BASE = Yields(food=8)
    SYMB = Yields(food=12)


class Tuna(Fish):
    SLOTS = 4
    BASE = Yields(food=4)
    GROWING_HUNTERS = Data(food_factor=0.5, per_gold=1)
    TERRITORIAL = Yields(food=3)

    @property
    def yields(self) -> Yields:
        return super().yields + self.growing_hunters() + self.territorial()

    def growing_hunters(self) -> Yields:
        """
        Growing Hunters: +0.5 Food for each 1 Wealth in neighboring
        Clownfish, Parrotfish, or Marlin.
        """
        factor: float = (
            Yields.sum(
                fish.yields for fish in self.nearby((Clownfish, Parrotfish, Marlin))
            ).gold
            // self.GROWING_HUNTERS.per_gold
        ) * self.GROWING_HUNTERS.food_factor
        log.info("tuna factor: %s", factor)
        return factor * Yields(food=1)

    def territorial(self) -> Yields:
        """Territorial: +3 Food if there is no other Tuna within Animal-Range."""
        return self.TERRITORIAL if not self.within_range(Tuna) else Yields()


class GreatTuna(Tuna):
    SLOTS = 5
    BASE = Yields(food=8)
    GROWING_HUNTERS = Data(food_factor=0.75, per_gold=1)
    TERRITORIAL = Yields(food=6)


class Marlin(Fish):
    SLOTS = 4
    BASE = Yields(food=2)
    VIGOROUS_SPECIMEN = Yields(food=4, tech=2)
    HUGE_SPECIMEN = Yields(gold=4, tech=2)

    @property
    def yields(self) -> Yields:
        return super().yields + self.vigorous_specimen() + self.huge_specimen()

    def vigorous_specimen(self) -> Yields:
        """
        Vigorous Specimen: +4 Food and +2 Technology
        for each Seabass within Animal Range.
        """
        return self.VIGOROUS_SPECIMEN * len(self.within_range(Seabass))

    def huge_specimen(self) -> Yields:
        """
        Huge Specimen: +4 Wealth and +2 Technology
        for each Parrotfish within Animal-Range.
        """
        return self.HUGE_SPECIMEN * len(self.within_range(Parrotfish))


class GreatMarlin(Marlin):
    SLOTS = 5
    BASE = Yields(food=4)
    VIGOROUS_SPECIMEN = Yields(food=6, tech=3)
    HUGE_SPECIMEN = Yields(gold=6, tech=3)


class Anglerfish(Fish):
    SLOTS = 4
    BASE = Yields(gold=6)
    WEIRD_DEEPS = Data(tech_factor=0.75, per_food=1)
    LEGENDARY_PROPORTIONS = Data(bonus=Yields(awe=5), min_tech=10)

    @property
    def yields(self) -> Yields:
        return super().yields + self.weird_deeps() + self.legendary_proportions()

    def weird_deeps(self) -> Yields:
        """
        Weird Deeps: +0.75 Technology for each 1 Food
        in neighboring Mackerel, Seabass or Marlin.
        """
        # Careful with Precedence! (yields.food // per_food) must be evaluated before to make
        # sure it is truncated as in the game. This is regardless of Yields truncation.
        factor: float = self.WEIRD_DEEPS.tech_factor * (
            Yields.sum(fish.yields for fish in self.nearby((Mackerel, Seabass, Marlin))).food
            // self.WEIRD_DEEPS.per_food
        )
        return factor * Yields(tech=1)

    def legendary_proportions(self) -> Yields:
        """Legendary Proportions: +5 Awe if this Anglerfish has at least 10 Technology."""
        bonus: Yields = (
            self.LEGENDARY_PROPORTIONS.bonus
            if self.yields.tech >= self.LEGENDARY_PROPORTIONS.min_tech
            else Yields()
        )
        return bonus


class GreatAnglerfish(Fish):
    SLOTS = 5
    BASE = Yields(gold=12)
    WEIRD_DEEPS = Data(tech_factor=1.5, per_food=2)
    LEGENDARY_PROPORTIONS = Data(bonus=Yields(awe=8), min_tech=10)
