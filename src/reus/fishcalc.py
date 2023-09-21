# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""
Fish layout and resources calculator
"""
from __future__ import annotations

import typing_extensions as t

from . import model as m
from .gamedata import *
from . import util as u

__all__ = ["cli"]


def cli(argv: t.Sequence[str]) -> None:
    try:
        village_range = int(argv[1]) if len(argv) > 1 else 6
    except ValueError as e:
        raise u.ReusError("Usage: reus-fish-calculator [CITY_RANGE=6]") from e
    world = m.World(
        layout=(
            Seabass,
            Clownfish,
            Parrotfish,
            Tuna,
            Parrotfish,
            Tuna,
            Seabass,
            Mackerel,
        )
    )
    resources = world.all_yields(until=village_range)
    total = m.Yields.sum(resources.values())

    print("Ocean Layout:")
    u.printf(world.sources)

    print(f"\nVillage resources, range = {village_range}:")
    u.printf(resources)

    print(f"\nTotal: {total}")
    print(f"Prosperity: {total.prosperity}")
