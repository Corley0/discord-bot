import discord
from discord.ext import commands, tasks
import db_manager
from datetime import datetime, timedelta
import util
import random

GW_CHANNEL = 1390391502210990241
CLAIM_CATAGORY = 1403584671123771422
HOST_ROLE = 1403592231566446693

class Giveaway(commands.Cog):
    def __init__(self, bot):
        db_manager.cursor.execute("CREATE TABLE IF NOT EXISTS giveaways(guild_id INTEGER, message_id INTEGER, host_id INTEGER, sponsor_id INTEGER, prize TEXT, timestamp INTEGER, duration INTEGER, expires INTEGER, claim_time INTEGER, ended INTEGER, winner INTEGER)")
        self.bot = bot
        if not self.check_active_gws.is_running():
            self.check_active_gws.start()
    
    def cog_unload(self):
        self.check_active_gws.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Giveaway Cog Ready")
    
    @tasks.loop(seconds=5)
    async def check_active_gws(self):
        now = int(datetime.now().timestamp())
        db_manager.cursor.execute("SELECT * FROM giveaways WHERE ended = 0 AND expires <= ?", (now,))
        data = db_manager.cursor.fetchall()

        for current_data in data:
            await self.end_giveaway(current_data)
            


    async def create_giveaway(self, ctx, sponsor, prize, duration, claim_time):
        message_json = util.config["messages"]["giveaway"]["entry"]
        emoji = util.config["giveaway"]["emoji"]
        duration_minutes = util.parse_time(duration)
        claim_minutes = util.parse_time(claim_time)
        expires = int((datetime.now() + timedelta(minutes=duration_minutes)).timestamp())
        
        gw_message = await ctx.guild.get_channel(GW_CHANNEL).send(embed=discord.Embed(title=message_json["title"].format(prize=prize),
                                            description=message_json["description"].format(sponsor = sponsor.mention, host = ctx.author.mention, expires = expires, claim_time = util.parse_time_str(claim_time), emoji = emoji)))
        await gw_message.add_reaction(emoji)

        db_manager.cursor.execute("INSERT INTO giveaways (guild_id, message_id, host_id, sponsor_id, prize, timestamp, duration, expires, claim_time, ended) VALUES (?,?,?,?,?,?,?,?,?,0)",
                                  (ctx.guild.id,
                                   gw_message.id,
                                   ctx.author.id,
                                   sponsor.id,
                                   prize,
                                   int(datetime.now().timestamp()),
                                   duration_minutes,
                                   expires,
                                   claim_minutes)
        )
        db_manager.db.commit()
    
    async def roll_giveaway(self, message):
        emoji = util.config["giveaway"]["emoji"]
        reactions = message.reactions
        for reaction in reactions:
            if str(reaction.emoji) == emoji:
                users = [user async for user in reaction.users()]
                users.remove(self.bot.user)
                break
        
        if not users:
            return None
            
        return random.choice(users)

    async def end_giveaway(self, data):
        message_json = util.config["messages"]["giveaway"]["interactions"]
        message_id = data[1]
        message = await self.bot.get_channel(GW_CHANNEL).fetch_message(message_id)
        guild = message.guild
        winner = await self.roll_giveaway(message)

        class RobloxInfo(discord.ui.Modal, title=message_json["modal"]["title"]):
            questions = message_json["modal"]["questions"]
            roblox_username = discord.ui.TextInput(label=questions["username"]["question"], placeholder=questions["username"]["placeholder"])
            timezone = discord.ui.TextInput(label=questions["timezone"]["question"], placeholder=questions["timezone"]["placeholder"])
            vip_accessible = discord.ui.TextInput(label=questions["links"]["question"], placeholder=questions["links"]["placeholder"])
            
            async def on_submit(self, interaction: discord.Interaction):
                ticket_message_json = util.config["messages"]["giveaway"]["ticket"]
                category = guild.get_channel(CLAIM_CATAGORY)
                channel = await guild.create_text_channel(f"{winner.name}-claim", category=category)

                await channel.send(ticket_message_json["welcome_message"].format(winner=winner.mention, host=HOST_ROLE, roblox_username = self.roblox_username.value, vip_accessible = self.vip_accessible.value, timezone = self.timezone.value))
                await interaction.response.send_message(ticket_message_json["notification"].format(channel = channel.id), ephemeral=True)

        class ClaimButton(discord.ui.View):
            @discord.ui.button(label=message_json["claim_button"]["text"], style=discord.ButtonStyle.primary, emoji=message_json["claim_button"]["emoji"])
            async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button):
                
                if interaction.user.id == winner.id:
                    modal = RobloxInfo()
                    await interaction.response.send_modal(modal)
                else:
                    await interaction.response.send_message(content=message_json["claim_button"]["false_claim"], ephemeral=True)

        gw_message_json = util.config["messages"]["giveaway"]["ended"]
        if winner != None:
            await message.reply(f"|| {winner.mention} ||", embed=discord.Embed(title=gw_message_json["title"],
                                                description=gw_message_json["description"].format(prize=data[4],claim_time=util.parse_time_str(util.convert_to_unparsed(data[8])),sponsor=data[3],host=data[2],winner=winner.mention)), view=ClaimButton())
            db_manager.cursor.execute('''UPDATE giveaways SET ended = 1, winner = ? WHERE message_id = ?''', (winner.id, message_id))
            db_manager.db.commit()
        else:
            await message.reply("No one joined the giveaway!")
            db_manager.cursor.execute('''UPDATE giveaways SET ended = 1 WHERE message_id = ?''', (message_id,))
            db_manager.db.commit()


    @commands.hybrid_command()
    async def create_gw(self, ctx, sponsor:discord.Member, prize, duration = "1d", claim_time = "6h"):
        await self.create_giveaway(ctx, sponsor, prize, duration, claim_time)

    @commands.hybrid_command()
    async def reroll_gw(self, ctx, message_id):
        message = await self.bot.get_channel(GW_CHANNEL).fetch_message(message_id)
        origin = message.reference
        winner = await self.roll_giveaway(origin)
        await message.reply(f"Giveaway Rerolled.\nNew Winner: {winner.mention}")

        db_manager.cursor.execute('''UPDATE giveaways SET winner = ? WHERE message_id = ?''', (winner.id, origin.message_id))
        db_manager.db.commit()


    #Reroll does not work
    
        


async def setup(bot):
    await bot.add_cog(Giveaway(bot))