
import discord
from commands import cmds
from functions import get_challenge_key, handle_bot_challenge_message, handle_challenge_acceptance, handle_challenge_rejection
#from functions import *



### Client ###

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.guild_reactions = True
intents.presences = True

client = discord.Client(intents=intents)



### Global ###

guilds: dict[dict] = {}



### Event Handlers ###

#initialize bot
@client.event
async def on_ready():
    
    global guilds
    
    print('Client is ready!')

    loc_guilds = []
    async for guild in client.fetch_guilds():
        loc_guilds.append(guild)
    
    for guild in loc_guilds:
        guilds[guild.id] = {}
        guilds[guild.id]['member_contexts'] = {}
        guilds[guild.id]['active_games'] = {}
        guilds[guild.id]['pending_challenge_messages'] = {}
        guilds[guild.id]['pending_challenges'] = {}
        guilds[guild.id]['ingame_members'] = []
        guilds[guild.id]['members'] = []
        async for member in guild.fetch_members():
            guilds[guild.id]['members'].append(member)
            guilds[guild.id]['member_contexts'][member.id] = ''



#message event handler
@client.event 
async def on_message(message):
    
    global guilds


    #ignore own messages except challenge messages
    if (message.author == client.user):

        if(message.content.startswith('Challenge!')):
            await handle_bot_challenge_message(message, guilds)       
            return


    #ignore non-command messages    
    if not message.content.startswith('!py '):
        return


    args = message.content.split(' ')[1:]


    ## General Commands ##

    if args[0] == 'help':
        await cmds['general'][args[0]](message)
        return

    
    if args[0] == 'challenge' and len(args) == 3:
        await cmds['general'][args[0]](message, guilds)
        return


    if args[0] == 'cancel':
            await cmds['general'][args[0]](message, guilds)
            return


    ## Context-specific Commands ##

    if isinstance(message.channel, discord.TextChannel):
        guild = guilds[message.guild.id]

    # Game Commands #

    if isinstance(message.channel, discord.TextChannel) and guild['member_contexts'][message.author.id].startswith('game'):

        context: str = guild['member_contexts'][message.author.id]

        if args[0] == 'resign':
            await cmds['general'][args[0]](message, guilds)
            return


        # Tic Tac Toe Commands #

        if context == 'game_tictactoe':
            
            if args[0] == 'move':
                await cmds[context][args[0]](message, args[1], guilds)
                return


        # Battleship Commands #

        if context == 'game_battleship':

            if args[0] == 'move' and len(args) == 2:
                await cmds[context][args[0]](message, args[1], guilds)
                return

    
    if isinstance(message.channel, discord.DMChannel):
        # ^ fix when another dm game is added

        if not isinstance(message.reference, discord.MessageReference):            
            return

        fetched_message: discord.Message = await message.channel.fetch_message(message.reference.message_id)
        if fetched_message.author != client.user:
            return


        if args[0] == 'set' and len(args) == 4:
            await cmds['game_battleship'][args[0]](message, args[1], args[2], args[3], guilds)
            return

        if args[0] == 'rm' and len(args) == 2:
            await cmds['game_battleship'][args[0]](message, args[1], guilds)
            return

        if args[0] == 'confirm':
            await cmds['game_battleship'][args[0]](message, guilds)
            return


### Reaction Event Handler ###

@client.event
async def on_reaction_add(reaction:discord.Reaction, user:discord.Member):

    if user == client.user:
        return


    guild = reaction.message.guild

    if reaction.message in guilds[guild.id]['pending_challenge_messages'].values():

        challenge_key = get_challenge_key(user, reaction.message.guild, guilds)
        game_name = guilds[guild.id]['pending_challenges'][challenge_key]['game_name']

        if  str(user.id) == challenge_key.split(' ')[1] \
        and guilds[guild.id]['pending_challenge_messages'][challenge_key] \
        == reaction.message:

            check_emoji = '✅' #:white_check_mark:
            x_emoji = '❌' #:x:

            if str(reaction.emoji) == check_emoji:
                await handle_challenge_acceptance(reaction, challenge_key, game_name, guilds)
                return
            
            elif str(reaction.emoji) == x_emoji:
                await handle_challenge_rejection(reaction, challenge_key, game_name, guilds)
                return



### Running the Bot ###

with open('token.txt', 'r') as f:
    BOT_TOKEN = f.read()


client.run(BOT_TOKEN)

