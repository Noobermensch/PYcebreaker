
import discord

import os, sys
sys.path.append(os.path.join(os.getcwd(), 'board_games'))

from tictactoe import TicTacToe
from battleship import Battleship


### Games ###

def init_tictactoe(player1:discord.Member, player2:discord.Member, game_chanel:discord.TextChannel):
    return TicTacToe(player1, player2, game_chanel)

def init_battleship(player1:discord.Member, player2:discord.Member, channel:discord.TextChannel):
    return Battleship(player1, player2, channel)

### Games Dict###

games = {
    'tictactoe': init_tictactoe,
    'battleship': init_battleship
}



### Functions ###

### Member Locator Functions ###

def get_member_by_id(id:int, guild_id:int, guilds:dict) -> discord.Member:
    return [m for m in guilds[guild_id]['members'] if m.id == id][0]

def get_member_by_nick(nick:str, guild_id:int, guilds:dict) -> discord.Member:
    return [m for m in guilds[guild_id]['members'] if m.display_name == nick][0]

def get_member_by_uname(uname:str, guild_id:int, guilds:dict) -> discord.Member:
    return [m for m in guilds[guild_id]['members'] if m.name == uname][0]


### Game Functions ###

#guilds[guild.id]['active_games'] and guilds[guild.id]['pending_challenges'] keys are in format 'userId1 userId2'

def start_game(member1:discord.Member, member2:discord.Member, guild:discord.Guild, game_name:str, game, guilds:dict):
    
    guild = guilds[guild.id]
    
    guild['active_games'][f'{member1.id} {member2.id}'] = game
    guild['ingame_members'].append(member1)
    guild['ingame_members'].append(member2)
    guild['member_contexts'][member1.id] = f'game_{game_name}'
    guild['member_contexts'][member2.id] = f'game_{game_name}'


def end_game(game_key:str, guild:discord.Guild, guilds: dict):
    
    guild_id = guild.id
    guild = guilds[guild.id]
    player1 = get_member_by_id(int(game_key.split(' ')[0]), guild_id, guilds)
    player2 = get_member_by_id(int(game_key.split(' ')[1]), guild_id, guilds)
    
    del guild['active_games'][game_key]
    guild['ingame_members'].remove(player1)
    guild['ingame_members'].remove(player2)
    guild['member_contexts'][player1.id] = ''
    guild['member_contexts'][player2.id] = ''


def new_challenge(member1:discord.Member, member2:discord.Member, message: discord.Message, game_name:str, guilds:dict):
    guild_id = message.guild.id
    guilds[guild_id]['pending_challenges'][f'{member1.id} {member2.id}'] = {
        'member1': member1, 'member2': member2, 'game_name': game_name
    }
    guilds[guild_id]['pending_challenge_messages'][f'{member1.id} {member2.id}'] = message
    return


def accept_challenge(challenge_key:str, game, guild:discord.Guild, guilds:dict) -> bool:
    player1 = guilds[guild.id]['pending_challenges'][challenge_key]['member1']
    player2 = guilds[guild.id]['pending_challenges'][challenge_key]['member2']
    game_name = guilds[guild.id]['pending_challenges'][challenge_key]['game_name']
    start_game(player1, player2, guild, game_name, game, guilds)
    del guilds[guild.id]['pending_challenges'][challenge_key]
    del guilds[guild.id]['pending_challenge_messages'][challenge_key]
    return True


def reject_challenge(challenge_key:str, guild: discord.Guild, guilds:dict) -> bool:
    del guilds[guild.id]['pending_challenges'][challenge_key]
    del guilds[guild.id]['pending_challenge_messages'][challenge_key]
    return True


def has_pending_challenge(member:discord.Member, guild: discord.Guild, guilds:dict) -> bool:
    for challenge_key in guilds[guild.id]['pending_challenges']:
        if str(member.id) in challenge_key:
            return True
    return False


def get_challenge_key(member:discord.Member, guild: discord.Guild, guilds:dict) -> str:
    for challenge_key in guilds[guild.id]['pending_challenges']:
        if str(member.id) in challenge_key:
            return challenge_key
    return None


def get_game_key(member:discord.Member, guild:discord.Guild, guilds:dict) -> str:
    for game_key in guilds[guild.id]['active_games']:
        if str(member.id) in game_key:
            return game_key
    return None


def get_game_key_with_guild_id(member:discord.Member, guild_id:int, guilds:dict) -> str:
    for game_key in guilds[guild_id]['active_games']:
        if str(member.id) in game_key:
            return game_key
    return None


def is_ingame(member:discord.Member, guild:discord.Guild, guilds:dict) -> bool:
    challenge_key = get_game_key(member, guild, guilds)
    if type(challenge_key) == str:
        return True
    else:
        return False



### Challenge Reaction Handlers ###

async def handle_challenge_acceptance(reaction:discord.Reaction, challenge_key:str, game_name:str, guilds:dict):

    guild: discord.Guild = reaction.message.guild
    channel: discord.TextChannel = reaction.message.channel

    player1: discord.Member = get_member_by_id(int(challenge_key.split(' ')[0]), guild.id, guilds)
    player2: discord.Member = get_member_by_id(int(challenge_key.split(' ')[1]), guild.id, guilds)


    if game_name == 'tictacoe':
        game = games[game_name](player1, player2)
    elif game_name == 'battleship':
        game = games[game_name](player1, player2, channel)


    accept_challenge(challenge_key, game, guild, guilds)
 
    await reaction.message.channel.send(f'{player2.display_name} has ACCEPTED the challenge of {player1.display_name} to {game_name}!')

    if game_name == 'tictactoe':
        await reaction.message.channel.send(guilds[guild.id]['active_games'][challenge_key].get_game_str())

    elif game_name == 'battleship':
        help_str = f'''{guild.id}
----------

Here are the Commands to set up your Ships:

    (you must REPLY the command to a message of mine starting with numbers)
    (e.g. 887386831188819848)

    to place a ship:
    !py set <ship name> <square> <orientation>
    
    to remove a placed ship:
    !py rm <ship name>

    to finish your setup:
    !py confirm

Valid Ships and their lengths:
    carrier          (5 squares)
    battleship       (4 squares)
    cruiser          (3 squares)
    submarine        (3 squares)
    destroyer        (2 squares)

Valid Orientations:
    vertical:
    v
    horizontal:
    h

Examples:
!py set battleship a3 h
!py rm battleship
!py confirm

----------'''
        
        await player1.send(help_str)
        await player1.send(f'{guild.id}\n\n{game.get_setup_str(player1)}')
        
        await player2.send(help_str)
        await player2.send(f'{guild.id}\n\n{game.get_setup_str(player2)}')

    return


async def handle_challenge_rejection(reaction:discord.Reaction, challenge_key:str, game_name:str, guilds:dict):
    guild = reaction.message.guild
    player1 =  get_member_by_id(int(challenge_key.split(' ')[0]), guild.id, guilds)
    player2 = get_member_by_id(int(challenge_key.split(' ')[1]), guild.id, guilds)
    reject_challenge(challenge_key, guild, guilds)
    await reaction.message.channel.send(f'{player2.display_name} has REJECTED the challenge of {player1.display_name} to {game_name}!')
    return



### Challenge Message Handler ###

async def handle_bot_challenge_message(message:discord.Message, guilds:dict):
    orig_message = await message.channel.fetch_message(message.reference.message_id)
    guild = message.guild
    try:
        challenger = get_member_by_id(orig_message.author.id, guild.id, guilds)
        challengee = get_member_by_nick(orig_message.content.split(' ')[2], guild.id, guilds)

        game_name = orig_message.content.split(' ')[3].lower()

        new_challenge(challenger, challengee, message, game_name, guilds)
        await message.add_reaction('✅')
        await message.add_reaction('❌')
    except IndexError:
        print(f'\n\n{orig_message.content.split(" ")}\n\n') #dbg
        pass
    return

