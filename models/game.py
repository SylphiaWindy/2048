#!/usr/bin/env python
# coding: UTF-8
# author: Sylphia
# created:  14:28
import logging
import random
from copy import deepcopy

from common.multicast_delegate import MulticastDelegate
from models.directions import Directions
from models.tile_event import TileSpawnEvent, TileMoveAndMergeEvent, TileMoveEvent


class Game(object):
    __direction_vectors = {
        Directions.Up: (0, -1),
        Directions.Down: (0, 1),
        Directions.Left: (-1, 0),
        Directions.Right: (1, 0),
    }

    def __init__(self, size=4, target=2048):
        """
        Initialize a game
        :param size: the size of the square board
        :param target: the target tile value to win a game
        """
        self.tile_event = MulticastDelegate(None)   # Tile state change event (Movement, Creation, Merge)
        self.score_event = MulticastDelegate(None)  # Score change event
        self.game_over_event = MulticastDelegate(None)  # Game over event, True for won, False for lost
        self.move_complete_event = MulticastDelegate(None)  # Fully completed a move, matrix is the final state
        self.undo_event = MulticastDelegate(None)   # Undo triggered event

        self.size = size
        self.target = target

        self.matrix = None
        self.empty_cell_count = 0
        self.score = 0
        self.undo_history = None
        self.game_over = False

        self.__clear_game_states()
        pass

    def __clear_game_states(self):
        self.matrix = [[0 for _ in range(self.size)] for __ in range(self.size)]
        self.empty_cell_count = self.size * self.size
        self.score = 0
        self.undo_history = []
        self.game_over = False

    def __create_random_tile(self, count, values):
        count = min(self.empty_cell_count, count)
        if not count:
            return
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if not self.matrix[i][j]:
                    empty_cells.append((i, j))
        for _ in range(count):
            empty_index = random.randint(0, len(empty_cells) - 1)
            x, y = empty_cells.pop(empty_index)
            value = random.choice(values)
            self.matrix[x][y] = value
            self.tile_event(TileSpawnEvent(x, y, value))
        self.empty_cell_count -= count

    def new_game(self):
        """
        Start a new game, clears old score and tiles, place two random tile of 2 or 4 on board
        :return:
        """
        self.__clear_game_states()
        self.__create_random_tile(2, [2, 4])

    def undo(self):
        """
        Undo a move, set the game to the state before last move, no effect if there's no movement yet
        :return:
        """
        if self.game_over:
            return
        if not self.undo_history:
            return
        last_score, last_empty_cell_count, last_matrix = self.undo_history.pop()
        self.score = last_score
        self.empty_cell_count = last_empty_cell_count
        self.matrix = deepcopy(last_matrix)
        self.undo_event(self.score, self.matrix)

    def move(self, direction: Directions):
        self.__move_with_vector(self.__direction_vectors[direction])

    def __get_traversal_range(self, direction):
        """
        Determines the traversal manner base on the movement direction
        :param direction:
        :return:
        """
        if direction < 0:
            return range(1, self.size)  # traversal from left or top moveable cell(skipped leftmost or topmost cells)
        if direction > 0:
            return range(self.size - 2, -1, -1)
        return range(0, self.size)

    def __get_farthest_available_cell(self, x, y, vector_x, vector_y):
        """
        Get the farthest cell that a tile from (x, y) can move towards to vector (vector_x, vector_y)
        :param x: the moving tile x
        :param y: the moving tile y
        :param vector_x: move vector x
        :param vector_y: move vector y
        :return: Tuple of (farthest cell x, y, the cell next to farthest cell x, y)
        """
        current = (x, y)
        while True:
            farthest_cell_x, farthest_cell_y = current
            next_cell_x, next_cell_y = current = (farthest_cell_x + vector_x, farthest_cell_y + vector_y)
            if not self.__within_board(next_cell_x, next_cell_y) or not self.__is_cell_empty(next_cell_x, next_cell_y):
                break
        return farthest_cell_x, farthest_cell_y, next_cell_x, next_cell_y

    def __within_board(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def __is_cell_empty(self, x, y):
        return not self.matrix[x][y]

    def __get_matrix_value_at(self, matrix, x, y):
        if not self.__within_board(x, y):
            return None
        return matrix[x][y]

    def __move_with_vector(self, vector):
        """
        Move the game with the direction vector
        :param vector: the vector represented for the move direction
        :return: None
        """
        if self.game_over:
            return

        vector_x, vector_y = vector
        moved = False  # Do not create new tile if nothing has been moved
        game_won = False
        merge_info = [[False for _ in range(self.size)] for __ in range(self.size)]  # saves which cell was merged
        last_state = self.score, self.empty_cell_count, deepcopy(self.matrix)  # save current state for undo
        for i in self.__get_traversal_range(vector_x):
            for j in self.__get_traversal_range(vector_y):
                tile = self.__get_matrix_value_at(self.matrix, i, j)
                if not tile:
                    continue
                farthest_cell_x, farthest_cell_y, next_cell_x, next_cell_y = self.__get_farthest_available_cell(
                    i, j, vector_x, vector_y
                )
                try_merge_with_tile = self.__get_matrix_value_at(self.matrix, next_cell_x, next_cell_y)
                if not self.__get_matrix_value_at(
                        merge_info, next_cell_x,
                        next_cell_y) and try_merge_with_tile and try_merge_with_tile == tile:
                    # can be merged with next cell
                    merge_info[next_cell_x][next_cell_y] = True
                    new_tile_value = tile * 2
                    self.empty_cell_count += 1
                    self.matrix[next_cell_x][next_cell_y] = new_tile_value
                    self.matrix[i][j] = 0
                    self.score += new_tile_value
                    self.tile_event(TileMoveAndMergeEvent(i, j, next_cell_x, next_cell_y, new_tile_value))
                    self.score_event(self.score)
                    game_won = new_tile_value == self.target
                    moved = True
                else:
                    if (farthest_cell_x, farthest_cell_y) == (i, j):
                        continue
                    self.matrix[farthest_cell_x][farthest_cell_y] = tile
                    self.matrix[i][j] = 0
                    self.tile_event(TileMoveEvent(i, j, farthest_cell_x, farthest_cell_y))
                    moved = True
        if moved:
            self.__create_random_tile(1, [2])
            self.undo_history.append(last_state)
            self.move_complete_event()
            logging.debug(self.matrix)
            if game_won:
                self.__trigger_game_over(True)
            elif self.__is_game_over():
                self.__trigger_game_over(False)

    def __trigger_game_over(self, won):
        self.game_over = True
        self.game_over_event(won)

    def __is_game_over(self):
        return self.empty_cell_count == 0 and not self.__has_mergeable_tile()

    def __has_mergeable_tile(self):
        for i in range(self.size):
            for j in range(self.size):
                tile = self.__get_matrix_value_at(self.matrix, i, j)
                if not tile:
                    continue
                for direction in list(Directions):
                    vector_x, vector_y = self.__direction_vectors[direction]
                    neighbor_tile = self.__get_matrix_value_at(self.matrix, i + vector_x, j + vector_y)
                    if neighbor_tile == tile:
                        return True
        return False
    pass
