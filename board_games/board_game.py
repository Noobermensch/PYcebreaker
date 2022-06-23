
import discord


class BoardGame:

    def __init__(self, player1:discord.Member, player2:discord.Member):
        self.player1 = player1
        self.player2 = player2
        self.player_moves: dict[list[str]] = {
            player1.id: [],
            player2.id: []
        }
        self.player_turn = player1


    def change_turn(self):
        if self.player_turn == self.player1:
            self.player_turn = self.player2
        elif self.player_turn == self.player2:
            self.player_turn = self.player1

    