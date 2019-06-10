#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  0:40
import os
import unittest

from game_config import GameConfig


class GameConfigTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.default_values = GameConfig._GameConfig__defaults
        self.default_board_color = (self.default_values['colors']['board']['foreground'],
                               self.default_values['colors']['board']['background'])
        self.default_cell_color = (self.default_values['colors']['tiles']['undefined']['foreground'],
                              self.default_values['colors']['tiles']['undefined']['background'])


class TestGameConfigDefaults(GameConfigTestBase):
    def testDefaultValues(self):
        cfg = GameConfig('__dummy__')
        self.assertEqual(cfg.get_cell_size(), self.default_values['dimensions']['cellSize'])
        self.assertEqual(cfg.get_cell_padding(), self.default_values['dimensions']['cellPadding'])
        self.assertEqual(cfg.get_label_font(),
                         (self.default_values['font']['face'], self.default_values['font']['size']))

        self.assertEqual(cfg.get_board_colors(), self.default_board_color)

        self.assertEqual(cfg.get_up_keys(), self.default_values['controls']['up'])
        self.assertEqual(cfg.get_down_keys(), self.default_values['controls']['down'])
        self.assertEqual(cfg.get_left_keys(), self.default_values['controls']['left'])
        self.assertEqual(cfg.get_right_keys(), self.default_values['controls']['right'])

        self.assertEqual(cfg.get_tile_colors(2), self.default_cell_color)
        self.assertEqual(cfg.get_tile_colors(8), self.default_cell_color)
        self.assertEqual(cfg.get_tile_colors(4096), self.default_cell_color)


class TestGameConfigWithJsonFile(GameConfigTestBase):
    def setUp(self) -> None:
        super().setUp()
        self.temp_file = 'test.json'
        config_json = '''
{
  "controls": {
    "down": [83, 40],
    "left": [65],
    "right": [68]
  },
  "font": {
    "face": "SimSun",
    "size": 22
  },
  "dimensions": {
    "cellSize": 150,
    "cellPadding": 5
  },
  "colors": {
    "board": {
      "foreground": "#111111",
      "background": "#888888"
    },
    "tiles": {
      "2": {
        "foreground": "#222222",
        "background": "#000000"
      },
      "8": {
        "foreground": "#888888",
        "background": "#444444"
      }
    }
  }
}        
        '''
        with open(self.temp_file, 'w') as f:
            f.write(config_json)

        pass

    def tearDown(self) -> None:
        os.remove(self.temp_file)

    def testFileValues(self):
        cfg = GameConfig(self.temp_file)
        self.assertEqual(cfg.get_cell_size(), 150)
        self.assertEqual(cfg.get_cell_padding(), 5)
        self.assertEqual(cfg.get_label_font(), ("SimSun", 22))
        self.assertEqual(cfg.get_board_colors(), ("#111111", "#888888"))

        self.assertEqual(cfg.get_up_keys(), self.default_values['controls']['up'])
        self.assertEqual(cfg.get_down_keys(), [83, 40])
        self.assertEqual(cfg.get_left_keys(), [65])
        self.assertEqual(cfg.get_right_keys(), [68])

        self.assertEqual(cfg.get_tile_colors(2), ("#222222", "#000000"))
        self.assertEqual(cfg.get_tile_colors(8), ("#888888", "#444444"))
        self.assertEqual(cfg.get_tile_colors(4096), self.default_cell_color)
