#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  11:36
import asyncio
from tkinter import Frame, CENTER, Label, BOTH

from game_config import GameConfig


class Tile(object):
    __spawn_anim_duration_ms = 100
    __anim_update_interval_ms = 10
    __move_speed = 5

    def __init__(self, size, value, config: GameConfig):
        """
        Create a tile
        :param size: tile size (squared width and height) in px
        :param value: tile value
        :param fg: tile foreground hex color string
        :param bg: tile background hex color string
        :param font: tile label font Tuple (face, size)
        """
        self.config = config
        self.size = size
        self.value = value
        self.fg, self.bg = config.get_tile_colors(value)
        self.font = config.get_label_font()
        self.__futures = []
        self.__current_move_future = None
        self.__current_position = None
        self.__merge_event = None
        self.__destination = None
        self.__tile = None
        self.__label = None

    def __update_value(self, new_value):
        """
        Update tile value to new one
        :param new_value: new value to set
        :return: None
        """
        self.__change_value(new_value)
        self.__update_label()

    def spawn_at(self, root, x, y):
        """
        Spawn the tile at specified position
        :param root: tile master widget
        :param x: x
        :param y: y
        :return: None
        """
        self.__tile = Frame(root, width=1, height=1)
        self.__current_position = (x, y)
        self.__tile.place(x=x, y=y, anchor=CENTER)
        self.__tile.pack_propagate(False)
        self.__update_label()

        self.__play_spawn_anim()
        pass

    def move_to(self, x=None, y=None):
        """
        Move the tile to specified position
        :param x: x
        :param y: y
        :return: None
        """
        if not self.__current_position: # do nothing if not been placed on board
            return
        if self.__current_move_future and not self.__current_move_future.done():
            self.__current_move_future.cancel()
            self.__current_position = self.__destination
            self.__tile.place(x=self.__current_position[0], y=self.__current_position[1], anchor=CENTER)
            self.__proceed_with_merge()
        if not x:
            x = self.__current_position[0]
        if not y:
            y = self.__current_position[1]
        dest = (x, y)
        if dest == self.__current_position:
            return
        self.__destination = dest
        self.__play_move_anim()

    def move_and_merge(self, merge_callback, new_value, x=None, y=None):
        self.__merge_event = (merge_callback, new_value)
        self.move_to(x, y)

    def __proceed_with_merge(self):
        if not self.__merge_event:
            return
        callback, new_value = self.__merge_event
        self.__merge_event = None
        if callback:
            callback()
        self.__update_value(new_value)

    def __change_value(self, new_value):
        self.value = new_value
        self.fg, self.bg = self.config.get_tile_colors(self.value)

    def __update_label(self):
        if self.__label:
            self.__label.config(text=self.value, bg=self.bg, fg=self.fg)
            return
        self.__label = Label(self.__tile, text=self.value, bg=self.bg, fg=self.fg, justify=CENTER, font=self.font)
        self.__label.pack(fill=BOTH, expand=True)

    @staticmethod
    def __get_direction(start, end):
        diff = end - start
        if not diff:
            return 0
        return diff / abs(diff)

    def __play_move_anim(self):
        destination_x, destination_y = self.__destination
        current_x, current_y = self.__current_position
        x_dir = self.__get_direction(current_x, destination_x)
        y_dir = self.__get_direction(current_y, destination_y)

        async def anim():
            x, y = self.__current_position
            new_x = x + x_dir * Tile.__move_speed * Tile.__anim_update_interval_ms
            new_y = y + y_dir * Tile.__move_speed * Tile.__anim_update_interval_ms
            new_x = min(destination_x, new_x) if x_dir > 0 else max(destination_x, new_x)
            new_y = min(destination_y, new_y) if y_dir > 0 else max(destination_y, new_y)
            self.__current_position = (new_x, new_y)
            self.__tile.place(x=new_x, y=new_y, anchor=CENTER)

            if (new_x, new_y) != self.__destination:
                await asyncio.sleep(Tile.__anim_update_interval_ms / 1000)   # update every 10ms
                await anim()
            else:
                self.__proceed_with_merge()

        def start_anim():
            f = asyncio.ensure_future(anim())
            self.__current_move_future = f
            f.add_done_callback(self.__remove_finished_futures)
            self.__futures.append(f)
        io_loop = asyncio.get_event_loop()
        io_loop.call_soon_threadsafe(start_anim)

    def __play_spawn_anim(self):
        step = (self.size - 1) / Tile.__spawn_anim_duration_ms

        async def anim(current_size):
            new_size = min(self.size, int(step * Tile.__anim_update_interval_ms + current_size))
            self.__tile.config(width=new_size, height=new_size)
            if new_size < self.size:
                await asyncio.sleep(Tile.__anim_update_interval_ms / 1000)   # update every 10ms
                await anim(new_size)

        def start_anim():
            f = asyncio.ensure_future(anim(1))
            f.add_done_callback(self.__remove_finished_futures)
            self.__futures.append(f)
        io_loop = asyncio.get_event_loop()
        io_loop.call_soon_threadsafe(start_anim)

    def __remove_finished_futures(self, f):
        self.__futures.remove(f)

    def destroy(self):
        for f in self.__futures:
            f.cancel()  # cancel any playing animations on destroy
        if self.__tile:
            self.__tile.pack_forget()
            self.__tile.destroy()
