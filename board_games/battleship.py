
import discord 
from board_game import BoardGame


class Battleship(BoardGame):


    number_emojis = '1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟'.split(' ')

    ship_names = ['carrier', 'battleship', 'cruiser', 'submarine', 'destroyer']


    def __init__(self, player1: discord.Member, player2:discord.Member, channel:discord.TextChannel, guild=discord.Guild):
        super().__init__(player1, player2)
        self.channel = channel
        self.guild = guild
        self.game_phase: str = 'setup'
        # game_phase can be 'setup' or 'play'
        self.player_ships: dict[dict[list[str]]] = {
            player1.id: {
                'carrier': [],
                'battleship': [],
                'cruiser': [],
                'submarine': [],
                'destroyer': []
            },
            player2.id: {
                'carrier': [],
                'battleship': [],
                'cruiser': [],
                'submarine': [],
                'destroyer': []
            }
        }
        self.player_hits: dict[list[str]] = {
            player1.id: [],
            player2.id: []
        }
        self.is_player_ready: dict[bool] = {
            player1.id: False,
            player2.id: False
        }


    ## Setup Methods ##

    def is_valid_placement(self, ship_name:str, square:str, orientation:str, player:discord.Member):
        
        col = square[0]
        row = int(square[1:])

        player_ship_squares = [sq for ship in self.player_ships[player.id].values() for sq in ship]

        if ship_name not in Battleship.ship_names:
            return False

        if len(self.player_ships[player.id][ship_name]) > 0:
            return False

        if not ((row >= 1 and row <= 10) and col in 'abcdefghij'):
            return False

        ship_lengths = {
            'carrier':      5,
            'battleship':   4,
            'cruiser':      3,
            'submarine':    3,
            'destroyer':   2
        }

        if orientation == 'h':
  
            if 'abcdefghij'.index(col)\
            + ship_lengths[ship_name] - 1 > 9:
                return False

            for i in range(ship_lengths[ship_name]):
                if f'{"abcdefghij"["abcdefghij".index(col)+i]}{row}' in player_ship_squares:
                    return False
  
        elif orientation == 'v':

            if row + ship_lengths[ship_name] - 1 > 10:
                return False

            for i in range(ship_lengths[ship_name]):
                if f'{col}{row+i}' in player_ship_squares:
                    return False

        return True


    def get_setup_str(self, player:discord.Member):

        board = '⬛🇦\u200b🇧\u200b🇨\u200b🇩\u200b🇪\u200b🇫\u200b🇬\u200b🇭\u200b🇮\u200b🇯'

        player_ship_squares = [sq for ship in self.player_ships[player.id].values() for sq in ship]

        rows = []
        for row in range(10):
            row_squares = []
            for col in range(10):
                if f'{"abcdefghij"[col]}{row+1}' in player_ship_squares:
                    row_squares.append('\u200b⬛')
                else:
                    row_squares.append('\u200b🟦')
            rows.append(row_squares)

        for i, row in enumerate(rows):
            board += f'\n{Battleship.number_emojis[i]}{"".join(row)}'

        return board


    def set(self, ship_name:str, square:str, orientation:str, player:discord.Member):
        
        ship_lengths = {
            'carrier':      5,
            'battleship':   4,
            'cruiser':      3,
            'submarine':    3,
            'destroyer':   2
        }

        col: str = square[0]
        row: int = int(square[1:])

        if orientation == 'h':
            idx = 'abcdefghij'.index(col)
            for i in range(ship_lengths[ship_name]):
                self.player_ships[player.id][ship_name].append(f'{"abcdefghij"[idx+i]}{row}')
       
        elif orientation == 'v':
            for i in range(ship_lengths[ship_name]):
                self.player_ships[player.id][ship_name].append(f'{col}{row+i}')

        return


    def rmv(self, ship_name:str, player:discord.Member):
        
        if ship_name not in Battleship.ship_names:
            return

        self.player_ships[player.id][ship_name] = []
        
        return


    ## Gameplay Methods ##

    ''' all methods that involve the player_turn will automatically refer to the player being ATTACKED by the one with the current turn'''

    def is_valid(self, move:str, player_turn:discord.Member) -> bool:
        try:
            col: str = move[0]
            row: int = int(move[1:])
            if row >= 1 and row <= 10 and col in 'abcdefghij':
                if f'{col}{row}' not in self.player_moves[player_turn.id]:
                    return True
            return False
        except ValueError:
            return False


    def is_hit(self, move:str, player_turn:discord.Member) -> bool:
        other_player_id: int = [p for p in self.player_moves if p != player_turn.id][0]
        for ship in self.player_ships[other_player_id].values():
            if move in ship:
                return True
        return False


    def is_sink(self, player_turn:discord.Member) -> bool:
        opponent_id: int = [p for p in self.player_moves if p != player_turn.id][0]
        if [] in self.player_ships[opponent_id].values():
            # returns True when an empty list remains in opponent's ships array
            # must be used AFTER a successful hit and removal of square, but BEFORE a new turn
            return True
        return False


    def add_move(self, move:str, player:discord.Member):
        if not self.is_valid(move, player):
            return False
        else:
            self.player_moves[player.id].append(move)
            return True


    def add_hit(self, move:str, player:discord.Member):
        if not self.is_hit(move, player):
            return False
        else:
            self.player_hits[player.id].append(move)
            return True


    def get_game_str(self, player_turn:discord.Member) -> str:
        #opponent_id: int = [player_id for player_id in self.player_moves if player_id != player_turn.id][0]
        game_array = []
        for row in range(1, 11):
            row_array = []
            for col in 'abcdefghij':
                if f'{col}{row}' in self.player_moves[player_turn.id]:
                    if f'{col}{row}' in self.player_hits[player_turn.id]:
                        row_array.append('🔥')
                    else:
                        row_array.append('🟦')
                else:
                    row_array.append('🌫️')
            game_array.append("".join(row_array))
        game_str = '⬛🇦\u200b🇧\u200b🇨\u200b🇩\u200b🇪\u200b🇫\u200b🇬\u200b🇭\u200b🇮\u200b🇯'
        for i, row in enumerate(game_array):
            game_str += f'\n{Battleship.number_emojis[i]}{row}'
        return f'----------\n{self.player1.display_name} vs {self.player2.display_name}\n\n{game_str}\n\nTurn: {self.player_turn.display_name}\n----------'


    def get_move_aftermath(self, player_turn:discord.Member) -> str:
        game_array = []
        for row in range(1, 11):
            row_array = []
            for col in 'abcdefghij':
                if f'{col}{row}' in self.player_moves[player_turn.id]:
                    if f'{col}{row}' in self.player_hits[player_turn.id]:
                        row_array.append('🔥')
                    else:
                        row_array.append('🟦')
                else:
                    row_array.append('🌫️')
            game_array.append("".join(row_array))
        game_str = '⬛🇦\u200b🇧\u200b🇨\u200b🇩\u200b🇪\u200b🇫\u200b🇬\u200b🇭\u200b🇮\u200b🇯'
        for i, row in enumerate(game_array):
            game_str += f'\n{Battleship.number_emojis[i]}{row}'
        return game_str


    def has_won(self, player:discord.Member) -> bool:
        if len(self.player_hits[player.id]) == 17:
            return True
        return False


    def is_over(self) -> bool:
        if self.has_won(self.player1) \
        or self.has_won(self.player2):
            return True
        return False

