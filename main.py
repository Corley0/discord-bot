import asyncio, json, os, logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import db_manager, util

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
enabled_cogs = ['gag']
config = {}

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

async def load_cogs():
    if 'all' in enabled_cogs:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f"cogs.{filename[:-3]}")
    else:
        for filename in os.listdir('./cogs'):
            if (filename[:-3] in enabled_cogs) and (filename.endswith('.py')):
                await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    await load_cogs()
    util.load_json()

    print(f"{bot.user.name} ({bot.user.id}) Online")
    server_list = "\n\n"
    for guild in bot.guilds:
        server_list += "-"*30 + f"\n{guild.name}, {guild.id}\n"
    server_list += "-"*30
    print(server_list)

@bot.hybrid_command()
#@commands.has_permissions()
async def load_cog(ctx, cog_name):
    await bot.load_extension(f"cogs.{cog_name}")
    await ctx.send(f"{cog_name.capitalize()} Cog Loaded")

@bot.hybrid_command()
#@commands.has_permissions()
async def unload_cog(ctx, cog_name):
    await bot.unload_extension(f"cogs.{cog_name}")
    await ctx.send(f"{cog_name.capitalize()} Cog Unloaded")

@bot.hybrid_command()
#@commands.has_permissions()
async def reload_cog(ctx, cog_name):
    await bot.reload_extension(f"cogs.{cog_name}")
    await ctx.send(f"{cog_name.capitalize()} Cog Reloaded")

@bot.hybrid_command()
async def reload_json(ctx):
    await util.load_json(ctx)



bot.run(token=TOKEN, log_handler=handler, log_level=logging.DEBUG)