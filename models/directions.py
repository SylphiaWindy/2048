#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  1:42
from enum import Enum, unique


@unique
class Directions(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3
