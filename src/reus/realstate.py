#!/usr/bin/env python3
# This file is part of Reus, see <https://github.com/MestreLion/reus>
# Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
"""
Available irrigated land (for forests and swamps) based on oceans count and width
Draft WIP
"""
import logging

from . import util

log = logging.getLogger(__name__)

MIN_SIZE = 6
# WORLD = 103  # 2 mountains (5) and their deserts (2*14), 1 ocean (9), 2 forests (13), 2 tiles
WORLD = 100  # 6 * 13 patches, 2 oceans (9 each), 1 mountain (5), -1 desert patch

# def ocean(num, size):
#     return num * size
#
#
# def forest(num, size):
#     return 2 * num * (size + 4)
#
#
# def tiles(num, size):
#     return forest(num, size) + ocean(num, size)


def forest(num, size):
    return (size + 4) * 2 * num    # == 2 * ocean + 8 * num


def tiles(num, size):
    ocean = num * size
    return ocean + forest(num, size)  # == num * (3 * size + 8)


def main(total):
    def width(n):
        return ((total / n) - 8) / 3  # solving size for num

    max_num = int(total / (3 * MIN_SIZE + 8))  # solving num for size == MIN_SIZE
    for num in range(1, max_num + 1):
        s = width(num)
        for size in (s, int(s), int(s) + 1):
            log.info("%2d oceans size %4.1f take %5.1f tiles and yield %5.1f forest",
                     num, size, tiles(num, size), forest(num, size))


def cli(argv):
    logging.basicConfig(level=logging.INFO)
    try:
        main(int(argv[1]))
    except IndexError as e:
        raise util.ReusError("Usage: reus-realstate NUM") from e
