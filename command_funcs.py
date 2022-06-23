
import discord
from functions import *


### General Commands ###

async def cmd_help(message:discord.Message):
    await message.channel.send(''' ----------

PYcebreaker 1.0 !

Valid Commands:

    !py help
    
    !py challenge <nickname> <game>
    
    !py resign
    
    !py move <move_notation>

    !py draw
    *(only works for chess)

Available Games:

    tictactoe

    battleship

    chess
    
----------''')
    return


async def cmd_challenge(message:discord.Message, guilds:dict):
    args = message.content.split(' ')[1:]
    try:
        guild = message.guild
        opponent = get_member_by_nick(args[1], guild.id, guilds)
        game_name = args[2]

        if opponent == message.author:
            await message.reply('You cannot challenge yourself to a game!')
            return

        if  (not is_ingame(message.author, guild, guilds)) \
        and (not is_ingame(opponent, guild, guilds) \
        and (not has_pending_challenge(message.author, guild, guilds)) \
        and (not has_pending_challenge(opponent, guild, guilds)) ):

            if game_name in games:
                challenge_body = f'Challenge!\n\n{message.author.display_name} has challenged {opponent.display_name} to {args[2]}!'

                guilds[guild.id]['pending_challenges'][f'{message.author.id} {opponent.id}'] = args[2].lower()
                
                await message.reply(challenge_body)
            else:
                await message.reply(f'{game_name} is not an available game!\nThe available games are:\ntictactoe')
            return
        
        elif has_pending_challenge(message.author, guild, guilds):
            await message.reply('You have a pending challenge!')
            return

        elif is_ingame(message.author, guild, guilds):
            await message.reply('You are already in a game!')
            return

        elif has_pending_challenge(opponent, guild, guilds):
            await message.reply(f'{opponent.display_name} has a pending challenge.')
            return

        elif is_ingame(opponent, guild, guilds):
            await message.reply(f'{opponent.display_name} is already in a game.')
            return

    except IndexError:
        await message.reply(f'Challenger {args[1]} not found!')
    return


async def cmd_cancel(message:discord.Message, guilds:dict):
    
    member = message.author
    guild = message.guild
    if not has_pending_challenge(member, guild, guilds):
        return

    challenge_key = get_challenge_key(member, guild, guilds)
    del guilds[guild.id]['pending_challenges'][challenge_key]
    del guilds[guild.id]['pending_challenge_messages'][challenge_key]
    
    await message.channel.send(f'{message.author.display_name} has cancelled their challenge!')

    return


async def cmd_resign(message:discord.Message, guilds:dict):
    guild = message.guild
    game = guilds[guild.id]['active_games'][get_game_key(message.author, guild, guilds)]
    if message.author == game.player1:
        winner = game.player2
    elif message.author == game.player2:
        winner = game.player1
    end_game(get_game_key(message.author, guild, guilds), guild, guilds)
    await message.channel.send(f'{message.author.display_name} has resigned! {winner.display_name} is the winner!')
    return



### Tic Tac Toe Commands ###

async def cmd_move_tictactoe(message:discord.Message, move:str, guilds:dict):
    author = message.author
    channel = message.channel
    guild = message.guild

    game: TicTacToe = guilds[guild.id]['active_games'][get_game_key(author, guild, guilds)]

    if author != game.player_turn:
        return

    if not move in game.valid_moves:
        await channel.send(f'Invalid move: {move}')
        return

    game.add_move(move, game.player_turn)
    game.change_turn()

    game_str = game.get_game_str()
    await channel.send(game_str)

    if game.is_over():
        if game.has_won(author):
            await message.channel.send(f'Game Over! {author.display_name} wins!')
        else:
            await channel.send(f'Game over! It is a draw!')
        end_game(get_game_key(author, guild, guilds), guild, guilds)

    return



### Battleship Commands ###

async def cmd_move_battleship(message:discord.Message, move:str, guilds:dict):
    
    channel = message.channel
    
    if not isinstance(channel, discord.TextChannel):
        await channel.send('Please use the group text channel!') 
        return

    author = message.author
    guild = message.guild

    game: Battleship = guilds[guild.id]['active_games'][get_game_key(author, guild, guilds)]

    if game.game_phase == 'setup':
        return

    if author != game.player_turn:
        return

    if not game.is_valid(move, author):
        await channel.send(f'Invalid move: {move}')
        return

    game.add_move(move, author)

    if game.is_hit(move, author):

        await channel.send(f'{author.display_name} HIT a ship on {move} !')

        game.add_hit(move, author)

        opponent_id: int = [p for p in game.player_moves if p != author.id][0]
        
        #remove the square from opponent's ship <list>
        for ship_name in game.player_ships[opponent_id].keys():
            if move in game.player_ships[opponent_id][ship_name]:
                game.player_ships[opponent_id][ship_name].remove(move)
                break

        if game.is_sink(author):
            
            ships: dict = game.player_ships[opponent_id]
            sunk_name: list[str] = [ship_name for ship_name in ships.keys() if len(ships[ship_name]) == 0][0]
            del game.player_ships[opponent_id][sunk_name]
            opponent = game.player1 if author != game.player1 else game.player2
            await channel.send(f'{author.display_name} sunk the {sunk_name.capitalize()} of {opponent.display_name} !')
            await channel.send(game.get_move_aftermath(game.player_turn))
            game.change_turn()
    else:
        await channel.send(f'{author.display_name} missed on {move} .')
        await channel.send(game.get_move_aftermath(game.player_turn))
        game.change_turn()

    if game.is_over():
        #game ALWAYS ends on winner's turn
        await channel.send(f'Game over! {author.display_name} wins!')
        end_game(get_game_key(message.author, guild, guilds), guild, guilds)
        return

    await channel.send(game.get_game_str(game.player_turn))

    return


    ## Battleship DM Setup Commands ##
        # guild param is passed to tie guild to dm channel ops

async def cmd_set_battleship(message:discord.Message, ship_name:str, square:str, orientation:str, guilds:dict):


    if not isinstance(message.channel, discord.DMChannel):
        return

    bot_msg: discord.Message = await message.channel.fetch_message(message.reference.message_id)

    guild_id: int = int(bot_msg.content.split('\n')[0])

    game: Battleship = guilds[guild_id]['active_games'][get_game_key_with_guild_id(message.author, guild_id, guilds)]

    if game.is_player_ready[message.author.id] == True:
        # make sure players can't change placements after confirming setup
        return

    if not game.is_valid_placement(ship_name, square, orientation, message.author):
        await message.author.send(f'{guild_id}\n\nCannot place {ship_name} on {square} in {orientation} orientation.')
        return

    game.set(ship_name, square, orientation, message.author)

    await message.author.send(f'{guild_id}\n\n{game.get_setup_str(message.author)}')


    return


async def cmd_rm_battleship(message:discord.Message, ship_name:str, guilds:dict):
    
    if not isinstance(message.channel, discord.DMChannel):
        return

    bot_msg: discord.Message = await message.channel.fetch_message(message.reference.message_id)

    guild_id: int = int(bot_msg.content.split('\n')[0])

    game: Battleship = guilds[guild_id]['active_games'][get_game_key_with_guild_id(message.author, guild_id, guilds)]

    if game.is_player_ready[message.author.id] == True:
        # make sure players can't change placements after confirming setup
        return

    if len(game.player_ships[message.author.id][ship_name]) == 0:
        # can't remove ship that hasn't been placed
        return

    game.rmv(ship_name, message.author)

    await message.author.send(f'{guild_id}\n\n{game.get_setup_str(message.author)}')

    return


async def cmd_confirm_battleship(message:discord.Message, guilds:dict):

    if not isinstance(message.channel, discord.DMChannel):
        return

    bot_msg: discord.Message = await message.channel.fetch_message(message.reference.message_id)

    guild_id: int = int(bot_msg.content.split('\n')[0])

    game: Battleship = guilds[guild_id]['active_games'][get_game_key_with_guild_id(message.author, guild_id, guilds)]

    if game.is_player_ready[message.author.id] == True:
        return

    for ship_name in game.player_ships[message.author.id].keys():
        if len(game.player_ships[message.author.id][ship_name]) == 0:
            await message.channel.send('{guild_id}\n\nPlease set all of your ships first.')
            return

    game.is_player_ready[message.author.id] = True

    await message.channel.send(f'{guild_id}\n\nYou have completed your setup! Please return to the GC and wait for the other player to finish.')

    if game.is_player_ready[game.player1.id] \
    and game.is_player_ready[game.player2.id]:
        game.game_phase = 'play'
        await game.channel.send(game.get_game_str(game.player1))

    return






