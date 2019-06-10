#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  15:03
import asyncio
import logging

from controllers.controller_base import ControllerBase
from models.directions import Directions
from models.game import Game
from views.board import Board


class GameController(ControllerBase):
    @classmethod
    def initialize(cls, config):
        cls.Config = config
        cls.Game = Game(4, 16)
        cls.Board = Board(cls.Game, _("2048"), config, asyncio.get_event_loop())
        cls.Board.on_new_game_clicked += cls.new_game
        cls.Board.on_undo_clicked += cls.undo
        cls.Board.on_key_event += cls.dispatch

    @classmethod
    def new_game(cls):
        game = cls.Game
        board = cls.Board
        board.clear_board()
        game.new_game()

    @classmethod
    def undo(cls):
        logging.debug('undo')
        cls.Game.undo()

    @classmethod
    def move(cls, direction: Directions):
        logging.debug('Moving {}'.format(direction.name))
        cls.Game.move(direction)

    @classmethod
    def dispatch(cls, event, *args, **kwargs):
        if event.keycode in cls.Config.get_up_keycodes():
            cls.move(Directions.Up)
        elif event.keycode in cls.Config.get_down_keycodes():
            cls.move(Directions.Down)
        elif event.keycode in cls.Config.get_left_keycodes():
            cls.move(Directions.Left)
        elif event.keycode in cls.Config.get_right_keycodes():
            cls.move(Directions.Right)

    @classmethod
    def run(cls):
        cls.Board.show()
