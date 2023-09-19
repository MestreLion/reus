# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""
Ocean layout helper
"""
from __future__ import annotations

import dataclasses
import logging
import typing_extensions as t

from . import util  # Just for Data, to export to gamedata

__all__ = [
    "Data",
    "Yields",
    "World",
    "Source",
    "Animal",
    "Aspect",
]

log = logging.getLogger(__name__)

TSource: t.TypeAlias = t.Type["Source"]
SourceMatch: t.TypeAlias = t.Union[TSource, t.Tuple[TSource, ...]]
Data = util.Data


@dataclasses.dataclass
class Yields:
    food: int = 0
    gold: int = 0
    tech: int = 0
    danger: int = 0
    #   natura: int = 0
    #   awe: int = 0

    @property
    def prosperity(self) -> int:
        return self.food + self.gold + self.tech

    @classmethod
    def sum(cls, yields_iterable: t.Iterable[t.Self]) -> t.Self:
        # Natura works very differently, using max instead of sum
        # Awe is also different, it does not work per-tile
        return cls(*map(sum, zip(*yields_iterable)))

    def scale(self, factor: int | float) -> t.Self:
        # Pycharm bug, works fine and mypy agrees
        # noinspection PyArgumentList
        return self.__class__(*map(int, map(factor.__mul__, self)))

    def __iter__(self) -> t.Iterator[t.Any]:
        return (getattr(self, field.name) for field in dataclasses.fields(self))

    def __add__(self, other: object) -> t.Self:
        if not isinstance(other, self.__class__):
            return NotImplemented
        # Pycharm bug, works fine and mypy agrees
        # noinspection PyArgumentList
        return self.__class__(*(a + b for a, b in zip(self, other)))  # .sum((self, other))

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
        return self.scale(other)

    def __rmul__(self, other: object) -> t.Self:
        # For int * Yields
        return self.__mul__(other)

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

    def source_tile(self, source: Source) -> int:
        return self.sources.index(source)

    def near_source(
        self, source: Source | int, matching: SourceMatch | None = None, distance: int = 1
    ) -> list[Source]:
        """List of sources near a source or tile matching a type in a given radius"""
        if distance <= 0:
            return []
        try:
            if isinstance(source, int):
                idx, src = source, self.sources[source]
            else:
                idx, src = self.source_tile(source), source
        except (ValueError, IndexError):
            log.warning("Natural Source not found: %s", source)
            return []
        sources: list[Source] = self.sources[max(idx - distance, 0) : idx + distance + 1]
        sources.remove(src)
        if matching is not None:
            sources = [s for s in sources if isinstance(s, matching)]
        return sources

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
        return self.__class__.__name__

    @property
    def tile(self) -> int:
        if self.world is None:
            return 0
        return self.world.source_tile(self)

    @property
    def natura(self) -> int:
        """Effective Natura on source, NOT the Natura produced by it"""
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
        """Yields per tile on all affected tiles"""
        return {0 if relative else self.tile: self.yields}

    def near(self, matching: SourceMatch | None = None, distance: int = 1) -> list[Source]:
        if self.world is None:
            return []
        return self.world.near_source(self, matching=matching, distance=distance)

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

    def near_range(self, matching: SourceMatch) -> list[Source]:
        return super().near(matching=matching, distance=self.range)

    def __repr__(self) -> str:
        content = str(self.yields)
        if self.range != self.RANGE:
            content += f", range={self.range}"
        return f"<{self.name}({content})>"


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
