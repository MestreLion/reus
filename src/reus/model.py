# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""
Ocean layout helper
"""
from __future__ import annotations

import dataclasses
import logging
import operator

import typing_extensions as t

from . import util as u

__all__ = [
    "Data",
    "Yields",
    "World",
    "Source",
    "Animal",
    "Mineral",
    "Plant",
    "Aspect",
]

log = logging.getLogger(__name__)

TSource: t.TypeAlias = t.Type["Source"]
SourceMatch: t.TypeAlias = t.Union[TSource, t.Tuple[TSource, ...]]
Data = u.Data


@dataclasses.dataclass
class Yields:
    food: int = 0
    gold: int = 0
    tech: int = 0
    awe: int = 0  # Comes before Danger and Natura since it's provided by all kinds of Sources.
    danger: int = 0  # Only provided by Animals, otherwise follow the same rules.
    # natura: int = 0  # Only provided by Plants and has unique rule, not a village resource.

    @property
    def prosperity(self) -> int:
        return self.food + self.gold + self.tech

    @classmethod
    def sum(cls, iterable: t.Iterable[t.Self]) -> t.Self:
        # Natura works very differently, using max instead of sum
        return cls(*map(sum, zip(*iterable)))

    # Intentionally has no __len__, for now. Has no use, and helps spot a misplaced len().
    # Has no __sub__ or __neg__ simply because they have no use yet.

    def __iter__(self) -> t.Iterator[t.Any]:
        return (getattr(self, field.name) for field in dataclasses.fields(self))

    def __add__(self, other: object) -> t.Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        # Alternatives:
        # 4.378: self.__class__(*(a + b for a, b in zip(self, other)))
        # 4.349: self.__class__.sum((self, other))
        # 3.874: current
        # noinspection PyArgumentList
        # Pycharm bug: https://youtrack.jetbrains.com/issue/PY-54359
        return self.__class__(*map(operator.add, self, other))

    def __radd__(self, other: object) -> t.Self:
        # Special-case zero so regular sum() works, as it will start with 0 + self.
        # It will, however, have return type of Union[Yields, Literal[0]],
        # as sum() returns 0 for an empty iterable.
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, other: object) -> t.Self:
        if not isinstance(other, (int, float)):
            return NotImplemented
        # noinspection PyArgumentList
        return self.__class__(*map(int, map(other.__mul__, self)))

    def __rmul__(self, other: object) -> t.Self:
        # For num * Yields
        return self.__mul__(other)

    def __truediv__(self, other: object) -> t.Self:
        return self.__floordiv__(other)

    def __floordiv__(self, other: object) -> t.Self:
        if not isinstance(other, (int, float)):
            return NotImplemented
        # noinspection PyArgumentList
        return self.__class__(*map(int, map(other.__rfloordiv__, self)))

    def __str__(self) -> str:
        # NamedTuple version: vars(self), defaults = self._asdict(), self._field_defaults
        defaults = {f.name: f.default for f in dataclasses.fields(self)}  # or assume all 0s
        diff = {k: v for k, v in vars(self).items() if not v == defaults[k]}  # if v
        return ", ".join("=".join(map("{:2}".format, _)) for _ in diff.items()) or "-"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self})>"


class World:
    def __init__(self, layout: t.Iterable[Source | TSource] = ()):
        self.sources: list[Source] = []
        for item in layout:
            source: Source = item if isinstance(item, Source) else item()
            source.world = self
            self.sources.append(source)

    def source(self, tile: int) -> Source:
        """The source in a tile (index)"""
        try:
            return self.sources[tile]
        except ValueError as e:
            raise u.ReusError("Tile not found: %s", tile) from e

    def tile(self, source: Source) -> int:
        """The tile (index) of a source"""
        try:
            return self.sources.index(source)
        except ValueError as e:
            raise u.ReusError("Natural Source not found: %s", source) from e

    def nearby_sources(
        self, source: Source, matching: SourceMatch | None = None, distance: int = 1
    ) -> list[Source]:
        """List of sources matching a type within a given distance from a source"""
        if distance <= 0:
            return []
        tile = self.tile(source)
        sources: list[Source] = self.sources[max(tile - distance, 0) : tile + distance + 1]
        # do not be tempted to remove by title, as source might not be in the middle position
        sources.remove(source)
        if matching is not None:
            sources = [s for s in sources if isinstance(s, matching)]
        return sources

    def nearby_yields(
        self, source: Source, matching: SourceMatch | None = None, distance: int = 1
    ) -> Yields:
        """Total Yields nearby a given source, regardless of provider"""
        all_yields = self.all_yields()
        return Yields.sum(
            all_yields[self.tile(src)]
            for src in self.nearby_sources(source, matching, distance)
        )

    def all_yields(self, until: int | None = None, start: int | None = 0) -> dict[int, Yields]:
        """Dictionary of tiles->yields, with optional start and stop (exclusive) tiles"""
        tiles: dict[int, list[Yields]] = {}
        for source in self.sources:
            for tile, yields in source.all_yields(relative=False).items():
                tiles.setdefault(tile, [])
                tiles[tile].append(yields)
        return {
            k: Yields.sum(v)
            for k, v in tiles.items()
            if (start is None or k >= start) and (until is None or k < until)
        }


class Source:
    """Base class for all Natural Sources"""

    BASE: t.ClassVar[Yields] = Yields()
    #    LEVEL: t.ClassVar[int] = 1
    SLOTS: t.ClassVar[int] = 1  # Default for Level 1, Tier 1 sources

    def __init__(self) -> None:
        self.world: World | None = None

    @property
    def name(self) -> str:
        # Too bad classmethod properties were deprecated in 3.11...
        return self.__class__.__name__

    @property
    def kind(self) -> str:
        # 2 options here: via string manipulation on name (easy but lame),
        # or diving into __mro__ for proper OOP, but good luck with that!
        # Guess the chosen approach?
        return self.name.lstrip("Great").lstrip("Superior")

    @property
    def tile(self) -> int:
        if self.world is None:
            # Don't use __str__ or __repr__, in subclasses they might require world set too
            raise u.ReusError("Tile not available for %s, World is not set", self.name)
        return self.world.tile(self)

    @property
    def natura(self) -> int:
        """Effective Natura on source, NOT the Natura provided by it"""
        return 0

    @property
    def yields(self) -> Yields:
        """Yields by itself on its own tile, usually just Base + Symbioses"""
        return self.BASE

    @property
    def total_yields(self) -> Yields:
        """Sum of yields on all affected titles"""
        return Yields.sum(self.all_yields().values())

    def all_yields(self, relative: bool = True) -> dict[int, Yields]:
        """Yields by itself per tile on all affected tiles"""
        return {0 if relative else self.tile: self.yields}

    def nearby(self, matching: SourceMatch | None = None, distance: int = 1) -> list[Source]:
        if self.world is None:
            return []
        return self.world.nearby_sources(self, matching=matching, distance=distance)

    def __repr__(self) -> str:
        return f"<{self.name}({self.yields})>"


class Animal(Source):
    """Base class for Animals"""

    RANGE: t.ClassVar[int] = 2
    ASPECTS: list[Aspect]  # Mandatory aspects

    def all_yields(self, relative: bool = True) -> dict[int, Yields]:
        return {
            idx + (0 if relative else self.tile): self.yields
            for idx in range(-self.range, self.range + 1)
        }

    @property
    def range(self) -> int:
        return self.RANGE

    def within_range(self, matching: SourceMatch) -> list[Source]:
        return super().nearby(matching=matching, distance=self.range)

    def __repr__(self) -> str:
        content = str(self.yields)
        if self.range != self.RANGE:
            content += f", range={self.range}"
        return f"<{self.name}({content})>"


class Mineral(Source):
    """Base class for Minerals"""


class Plant(Source):
    """Base class for Plant"""


# Unused, for now just a way to dump game data values
class Aspect:
    BONUS: Yields | tuple[Yields, int] | tuple[Yields, Yields, int] = Yields()

    def __init__(self) -> None:
        self.source: Source | None = None

    @property
    def natura(self) -> int:
        if self.source is None:
            return 0
        return self.source.natura

    def yields(self) -> Yields:
        return Yields() if self.natura else Yields()
