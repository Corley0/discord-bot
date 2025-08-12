import discord
from discord.ext import commands
import db_manager
from datetime import datetime, timedelta
import util

class Moderation(commands.Cog):
    def __init__(self, bot):
        db_manager.cursor.execute("CREATE TABLE IF NOT EXISTS warnings(guild_id INTEGER, user_id INTEGER, mod_id INTEGER, reason TEXT, timestamp INTEGER)")
        db_manager.cursor.execute("CREATE TABLE IF NOT EXISTS mutes(guild_id INTEGER, user_id INTEGER, mod_id INTEGER, reason TEXT, timestamp INTEGER, duration INTEGER, expires INTEGER)")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation Cog Ready")


    async def add_warning(self, ctx, user, reason):
        message_json = util.config["messages"]["moderation"]["warning"]
        db_manager.cursor.execute("INSERT INTO warnings (guild_id, user_id, mod_id, reason, timestamp) VALUES (?,?,?,?,?)",
                                  (ctx.guild.id,
                                   user.id,
                                   ctx.author.id,
                                   reason,
                                   int(datetime.now().timestamp()))
        )
        db_manager.db.commit()

        await user.send(embed=discord.Embed(title=message_json["dm"]["title"], description=message_json["dm"]["description"].format(guild = ctx.guild.name, reason = reason, mod = ctx.author.mention)))
        await ctx.send(embed=discord.Embed(title=message_json["server"]["title"].format(user=user.name), description=message_json["server"]["description"].format(reason = reason, mod = ctx.author.mention)))
        
    async def get_warnings(self, ctx, user):
        guild = ctx.guild.id
        db_manager.cursor.execute("SELECT reason FROM warnings WHERE user = ? AND guild = ?", (user.id, guild))
        data = db_manager.cursor.fetchall()
        if data:
            ctx.send(data)

    async def add_mute(self, ctx, user, duration, reason):
        message_json = util.config["messages"]["moderation"]["mute"]["muted"]
        duration_minutes = util.parse_time(duration)
        expires = int((datetime.now() + timedelta(minutes=duration_minutes)).timestamp())
        db_manager.cursor.execute("INSERT INTO mutes (guild_id, user_id, mod_id, reason, timestamp, duration, expires) VALUES (?,?,?,?,?,?,?)",
                                  (ctx.guild.id,
                                   user.id,
                                   ctx.author.id,
                                   reason,
                                   int(datetime.now().timestamp()),
                                   duration_minutes,
                                   expires
                                   )
        )
        db_manager.db.commit()

        await user.timeout(timedelta(minutes=duration_minutes))
        
        await user.send(embed=discord.Embed(title=message_json["dm"]["title"], description=message_json["dm"]["description"].format(guild = ctx.guild.name, duration = util.parse_time_str(duration), expires = expires, reason = reason, mod = ctx.author.mention)))
        await ctx.send(embed=discord.Embed(title=message_json["server"]["title"].format(user=user.name), description=message_json["server"]["description"].format(duration = util.parse_time_str(duration), reason = reason)))


    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, user:discord.Member, *, reason:str = "Undefined"):
        await self.add_warning(ctx, user, reason)
    
    
    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, user:discord.Member, *, duration:str, reason:str = "Undefined"):
        await self.add_mute(ctx, user, duration, reason)
    
    @commands.hybrid_command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, user:discord.Member, *, reason:str = "Undefined"):
        message_json = util.config["messages"]["moderation"]["mute"]["unmuted"]
        await user.timeout(None)
        
        await user.send(embed=discord.Embed(title=message_json["dm"]["title"], description=message_json["dm"]["description"].format(guild = ctx.guild.name, reason = reason, mod = ctx.author.mention)))
        await ctx.send(embed=discord.Embed(title=message_json["server"]["title"].format(user=user.name), description=message_json["server"]["description"].format(reason = reason)))
    
    @commands.group()
    async def purge(self, ctx):
        await ctx.send("Please use sub-command user/any\ne.g. ?purge any 10")

    @purge.command()
    async def user(self, ctx, user: discord.Member, count: int):
        message_json = util.config["messages"]["moderation"]["purge"]["user"]
        def is_user(msg):
            return msg.author == user
        deleted = await ctx.channel.purge(limit=count+1,check=is_user)

        await ctx.send(message_json["success"].format(count=len(deleted)-1, user=user.name))

    @purge.command()
    async def any(self, ctx, count: int):
        message_json = util.config["messages"]["moderation"]["purge"]["generic"]
        deleted = await ctx.channel.purge(limit=count+1)

        await ctx.send(f"{len(deleted)} messages deleted")
        await ctx.send(message_json["success"].format(count=len(deleted)-1))


async def setup(bot):
    await bot.add_cog(Moderation(bot))