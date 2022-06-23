
from command_funcs import *

### Commands Dict ###

cmds = {
    'general': {
        'help': cmd_help,
        'challenge': cmd_challenge,
        'cancel': cmd_cancel,
        'resign': cmd_resign
    },
    'game_tictactoe': {
        'move': cmd_move_tictactoe,
    },
    'game_battleship': {
        'move': cmd_move_battleship,
        'set': cmd_set_battleship,
        'rm': cmd_rm_battleship,
        'confirm': cmd_confirm_battleship 
    }
}
