#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  22:02
import logging
from asyncio import AbstractEventLoop
from tkinter import Tk, Canvas, Button, Label, StringVar, messagebox

from common.multicast_delegate import MulticastDelegate
from game_config import GameConfig
from models.tile_event import TileEvent, TileSpawnEvent, TileMoveEvent, TileMoveAndMergeEvent
from .tile import Tile


class Board(object):
    def __init__(self, game, game_title, config: GameConfig, io_loop: AbstractEventLoop, board_size=4, **kw):
        """
        Initialize a new game board
        :param game_title: the title that will display on the window
        :param config:
        :param board_size: size of the board (square)
        :param kw: kwargs (reserved)
        """
        super().__init__(**kw)

        self.io_loop = io_loop
        self.cells = []
        self.tiles = []
        self.config = config
        self.board = None
        self.board_size = 4

        self.on_new_game_clicked = MulticastDelegate(None)
        self.on_undo_clicked = MulticastDelegate(None)
        self.on_key_event = MulticastDelegate(None)

        self.__tile_size = self.config.get_cell_size()
        self.__canvas_size = self.__get_board_wh(board_size)
        self.__tile_label_font = self.config.get_label_font()
        self.__score_var = None

        self.root = self.__initialize_window(game_title)
        self.__initialize(board_size)
        self.game = game
        game.tile_event += self.__tile_event_dispatcher
        game.score_event += self.__score_event_dispatcher
        game.undo_event += self.__undo_event_dispatcher
        game.game_over_event += self.__game_over_dispatcher

    def __game_over_dispatcher(self, won):
        message = _("Congratulations, YOU WON!") if won else _("Don't be sad, it always happens.")
        title = _("You WON") if won else _("Game Over")
        messagebox.showinfo(title, message)

    def __undo_event_dispatcher(self, score, matrix):
        self.clear_board()
        self.__score_var.set(score)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                tile = matrix[i][j]
                if not tile:
                    continue
                self.spawn_tile(i, j, tile)

    def __score_event_dispatcher(self, new_score):
        self.__score_var.set(new_score)

    def __tile_event_dispatcher(self, tile_event: TileEvent):
        logging.debug(tile_event)

        self.__process_spawn_event(tile_event)
        self.__process_move_event(tile_event)
        self.__process_move_and_merge_event(tile_event)

    def __process_spawn_event(self, tile_event: TileEvent):
        if not isinstance(tile_event, TileSpawnEvent):
            return
        self.spawn_tile(tile_event.x, tile_event.y, tile_event.value)

    def __process_move_event(self, tile_event: TileEvent):
        if not isinstance(tile_event, TileMoveEvent):
            return
        tile = self.tiles[tile_event.x][tile_event.y]
        x, y = self.cells[tile_event.dest_x][tile_event.dest_y]
        self.tiles[tile_event.x][tile_event.y] = None
        self.tiles[tile_event.dest_x][tile_event.dest_y] = tile
        tile.move_to(x, y)

    def __process_move_and_merge_event(self, tile_event: TileEvent):
        if not isinstance(tile_event, TileMoveAndMergeEvent):
            return
        tile = self.tiles[tile_event.x][tile_event.y]
        target_tile = self.tiles[tile_event.dest_x][tile_event.dest_y]
        x, y = self.cells[tile_event.dest_x][tile_event.dest_y]
        self.tiles[tile_event.x][tile_event.y] = None
        self.tiles[tile_event.dest_x][tile_event.dest_y] = tile
        tile.move_and_merge(target_tile.destroy, tile_event.value, x, y)

    def clear_board(self):
        self.__canvas_size = self.__get_board_wh(self.board_size)
        self.tiles = []
        self.__score_var.set(0)
        if self.board:
            self.board.place_forget()
            self.board.destroy()

        self.__initialize(self.board_size)

    def show(self):
        self.root.mainloop()

    def __on_new_game_clicked(self):
        self.on_new_game_clicked.invoke()

    def __on_undo_clicked(self):
        self.on_undo_clicked.invoke()

    def __on_key_event(self, event):
        self.on_key_event.invoke(event)

    def __initialize_window(self, game_title):
        root = Tk()
        root.title(game_title)
        root.resizable(False, False)
        root.bind("<Key>", self.__on_key_event)
        btn_new_game = Button(root, text=_('New Game'), width=10, command=self.__on_new_game_clicked)
        btn_new_game.grid(row=0, column=0, padx=20, pady=5)
        btn_undo = Button(root, text=_('Undo'), width=10, command=self.__on_undo_clicked)
        btn_undo.grid(row=1, column=0, padx=20, pady=5)
        lbl_score_title = Label(root, text=_('Score'), font=(_('Arial'), 14))
        lbl_score_title.grid(row=0, column=3, columnspan=2, padx=20)

        self.__score_var = StringVar()
        self.__score_var.set(0)
        lbl_score_value = Label(root, textvariable=self.__score_var, font=(_('Arial'), 12))
        lbl_score_value.grid(row=1, column=3, columnspan=2, padx=20)
        return root

    def __get_board_wh(self, board_size):
        return self.__tile_size * board_size + self.config.get_cell_padding() * (board_size + 1)

    def __initialize(self, board_size):
        board_width = board_height = self.__canvas_size
        board_fg, board_bg = self.config.get_board_colors()

        self.board = Canvas(self.root, bg=board_bg, width=board_width, height=board_height)
        self.board.grid(row=2, column=0, columnspan=4)
        cell_padding = self.config.get_cell_padding()
        for i in range(board_size):
            centers_column = []
            tile_column = []
            for j in range(board_size):
                cell_left = i * self.__tile_size + cell_padding * (1 + i)
                cell_top = j * self.__tile_size + cell_padding * (1 + j)
                self.board.create_rectangle(cell_left, cell_top, cell_left + self.__tile_size,
                                            cell_top + self.__tile_size,
                                            outline=board_bg, fill=board_fg)
                centers_column.append((cell_left + self.__tile_size / 2, cell_top + self.__tile_size / 2))
                tile_column.append(None)
            self.cells.append(centers_column)
            self.tiles.append(tile_column)
        pass

    def spawn_tile(self, x, y, value: int):
        center_x, center_y = self.cells[x][y]
        current_tile = self.tiles[x][y]
        if current_tile:
            current_tile.destroy()
            self.tiles[x][y] = None
        tile = Tile(self.__tile_size, value, self.config)
        self.tiles[x][y] = tile
        tile.spawn_at(self.board, center_x, center_y)
