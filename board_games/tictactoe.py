
import discord
from board_game import BoardGame


class TicTacToe(BoardGame):

    win_conds: list[list] = [
        ['a1', 'a2', 'a3'],
        ['a1', 'b1', 'c1'],
        ['a1', 'b2', 'c3'],
        ['a2', 'b2', 'c2'],
        ['a3', 'b2', 'c1'],
        ['a3', 'b3', 'c3'],
        ['b1', 'b2', 'b3'],
        ['c1', 'c2', 'c3']
    ]


    def __init__(self, player1:discord.Member, player2:discord.Member):
        super().__init__(player1, player2)
        self.valid_moves: list[str] = [
            'a1', 'a2', 'a3',
            'b1', 'b2', 'b3',
            'c1', 'c2', 'c3'
        ]


    def get_game_str(self):
        d = {
            'a1': '', 'a2': '', 'a3': '',
            'b1': '', 'b2': '', 'b3': '',
            'c1': '', 'c2': '', 'c3': ''
        }
        for move in self.valid_moves:
            d[move] = '⬛'
        for move in self.player_moves[self.player1.id]:
            d[move] = '❌'
        for move in self.player_moves[self.player2.id]:
            d[move] = '⭕'
        return f"----------\n{self.player1.display_name} vs {self.player2.display_name}\n\n{d['a1']}{d['b1']}{d['c1']}\n{d['a2']}{d['b2']}{d['c2']}\n{d['a3']}{d['b3']}{d['c3']}\n\nTurn: {self.player_turn.display_name}\n----------"


    def add_move(self, move:str, player:discord.Member):
        if move not in self.valid_moves:
            return False
        else:
            self.player_moves[player.id].append(move)
            self.valid_moves.remove(move)
            return True


    def has_won(self, player:discord.Member):
        for cond in TicTacToe.win_conds:
            winning_moves = 0
            for move in cond:
                if move in self.player_moves[player.id]:
                    winning_moves += 1
            if winning_moves == 3:
                return True
        return False


    def is_over(self) -> bool:
        if self.has_won(self.player1) \
        or self.has_won(self.player2) \
        or len(self.valid_moves) == 0:
            return True
        return False



