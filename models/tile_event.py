#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  14:53
from enum import Enum


class TileEventTypes(Enum):
    Unknown = 0
    Spawn = 1
    Move = 2
    MoveAndMerge = 3


class TileEvent(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = 0
        self.event_type = TileEventTypes.Unknown
        pass


class TileSpawnEvent(TileEvent):
    def __init__(self, x, y, value):
        super().__init__(x, y)
        self.event_type = TileEventTypes.Spawn
        self.value = value

    def __repr__(self):
        return 'Spawn tile {} at ({}, {})'.format(self.value, self.x + 1, self.y + 1)


class TileMoveEvent(TileEvent):
    def __init__(self, x, y, dest_x, dest_y):
        super().__init__(x, y)
        self.event_type = TileEventTypes.Move
        self.dest_x = dest_x
        self.dest_y = dest_y

    def __repr__(self):
        return 'Moving tile ({}, {}) to ({}, {})'.format(self.x + 1, self.y + 1, self.dest_x + 1, self.dest_y + 1)


class TileMoveAndMergeEvent(TileEvent):
    def __init__(self, x, y, dest_x, dest_y, value):
        super().__init__(x, y)
        self.event_type = TileEventTypes.Move
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.value = value

    def __repr__(self):
        return 'Merge tile {} from ({}, {}) to ({}, {})'.format(self.value, self.x + 1, self.y + 1, self.dest_x + 1,
                                                                self.dest_y + 1)
