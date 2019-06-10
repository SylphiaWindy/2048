#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  0:00
import json


class GameConfig(object):
    __defaults = {
        "controls": {
            "up": ["Up"],
            "down": ["Down"],
            "left": ["Left"],
            "right": ["Right"]
        },
        "dimensions": {
            "cellSize": 100,
            "cellPadding": 10
        },
        "font": {
            "face": "Arial",
            "size": 20
        },
        "colors": {
            "board": {
                "foreground": "#ac7e65",
                "background": "#d59f81"
            },
            "tiles": {
                "undefined": {
                    "foreground": "#635b53",
                    "background": "#efe3d7"
                }
            }
        }
    }

    def __init__(self, config_file):
        """
        Load game config from json file
        :param config_file: game config json file name
        """
        self.data = {}
        try:
            with open(config_file, 'r') as f:
                self.data = json.load(f)
        except:
            pass

    def get_up_keys(self):
        """
        Get key codes that defined as move up
        :return: array of keycodes
        """
        return self.__get_keys_for("up")

    def get_down_keys(self):
        """
        Get key codes that defined as move down
        :return: array of keycodes
        """
        return self.__get_keys_for("down")

    def get_left_keys(self):
        """
        Get key codes that defined as move left
        :return: array of keycodes
        """
        return self.__get_keys_for("left")

    def get_right_keys(self):
        """
        Get key codes that defined as move right
        :return: array of keycodes
        """
        return self.__get_keys_for("right")

    def get_cell_size(self):
        """
        Get cell size in pixels
        :return: cell size in pixels
        """
        return self.data.get("dimensions", {}).get("cellSize", 0) or self.__defaults["dimensions"]["cellSize"]

    def get_cell_padding(self):
        """
        Get cell padding pixels
        :return: cell padding in pixels
        """
        return self.data.get("dimensions", {}).get("cellPadding", 0) or self.__defaults["dimensions"]["cellPadding"]

    def get_board_colors(self):
        """
        Get board's foreground and background colors
        :return: Tuple of hex color string (foreground, background)
        """
        board_config = self.data.get("colors", {}).get("board", {})
        config_fg = board_config.get("foreground", '')
        config_bg = board_config.get("background", '')

        return config_fg or self.__defaults["colors"]["board"]["foreground"], config_bg or \
               self.__defaults["colors"]["board"]["background"]

    def get_label_font(self):
        """
        Get cell label font
        :return: Tuple of font attribute (face, size)
        """
        font_face = self.data.get("font", {}).get("face", '')
        font_size = self.data.get("font", {}).get("size", 0)
        return font_face or self.__defaults["font"]["face"], font_size or self.__defaults["font"]["size"]

    def get_tile_colors(self, tile_value):
        """
        Get tile's foreground and background colors
        :return: Tuple of hex color string (foreground, background)
        """
        tiles_config = self.data.get("colors", {}).get("tiles", {}).get(str(tile_value), {})
        config_fg = tiles_config.get("foreground", '')
        config_bg = tiles_config.get("background", '')
        return config_fg or self.__defaults["colors"]["tiles"]["undefined"]["foreground"], config_bg or \
               self.__defaults["colors"]["tiles"]["undefined"]["background"]

    def __get_keys_for(self, direction):
        return self.data.get("controls", {}).get(direction, []) or self.__defaults["controls"][direction]
