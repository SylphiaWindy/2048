#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  21:55
import asyncio
import logging
import threading
import gettext
import os

from controllers.game_controller import GameController
from game_config import GameConfig

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
translate = gettext.translation('2048', localedir, languages=['en-US', 'zh_CN'], fallback=True)
translate.install()


def io_loop_thread(loop):
    loop.run_forever()


def stop_loop():
    loop = asyncio.get_event_loop()
    loop.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    io_loop = asyncio.get_event_loop()
    threading.Thread(target=io_loop_thread, args=(io_loop,)).start()
    config = GameConfig('config.json')
    GameController.initialize(config)
    GameController.new_game()
    GameController.run()
    io_loop.call_soon_threadsafe(stop_loop)
