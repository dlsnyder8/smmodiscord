import discord
from discord.ext import commands
from discord import Embed
from util import checks
import api
import logging
import database as db

logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Wars(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @checks.in_fly_guild()
    @commands.group(aliases = ['war','w'], hidden=True)
    async def wars(self,ctx):
        if ctx.invoked_subcommand is None:
            pass

    @wars.command()
    async def friendly(self,ctx):
        wars = api.get_guild_wars(408,1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Friendly",description="There are no active wars. They may be on hold or may have all ended."))
            return
        


        warstring = ""
        for war in wars[:35]:
            friendly = war['guild_1']
            guild = war['guild_2']
            warstring += f"**{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members)\n"

            if len(warstring) > 1900:
                embed = Embed(title="Friendly Wars", description=warstring)
                await ctx.send(embed=embed)
                warstring =""
        
        embed = Embed(title="Friendly Wars", description=warstring)
        await ctx.send(embed=embed)

    @wars.command()
    async def too(self,ctx):
        wars = api.get_guild_wars(455,1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for Friendly Too",description="There are no active wars. They may be on hold or may have all ended."))
            return
        
        warstring = ""
        for war in wars:
            friendly = war['guild_1']
            guild = war['guild_2']
            warstring += f"**{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members)\n"

        await ctx.send(embed=Embed(title="Friendly Too Wars",description=warstring))

    @wars.command()
    async def nsf(self,ctx):
        wars = api.get_guild_wars(541,1)
        if len(wars) == 0:
            await ctx.send(embed=Embed(title="No Active Wars for NSF",description="There are no active wars. They may be on hold or may have all ended."))
            return
        
        warstring = ""
        for war in wars:
            friendly = war['guild_1']
            guild = war['guild_2']
            warstring += f"**{guild['name']}:** {friendly['kills']} kills. [Attack](https://web.simple-mmo.com/guilds/view/{guild['id']}/members)\n"

        await ctx.send(embed=Embed(title="NSF Wars",description=warstring))

    
    
    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.is_verified()
    async def setup(self,ctx, guildid : int):
        if db.warinfo_isadded(ctx.author.id):
            await ctx.send(f"You already did this. If you need a list of customization options, run `{ctx.prefix}war options`")
            return
        
        if guildid not in (408, 455, 541, 482):
            await ctx.send("It appears you did not enter a valid Friendly guild id. The options are:\n**408**\n**455**\n**541**\n")
            return

        smmoid = db.get_smmoid(ctx.author.id)
        db.warinfo_setup(ctx.author.id,smmoid,guildid)

        await ctx.send(f"Success! Please run `{ctx.prefix}war options` for a list of customization options, or run `{ctx.prefix}war profile` to see your current profile")
    

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def options(self,ctx):
        embed = Embed(title="Customization Options")
        string = f"`{ctx.prefix}war guild <int>` - change which guild you're currently in (needs to be a Fly guild)\n"
        string+= f"`{ctx.prefix}war minlevel <int>` - sets the min level of your targets (default 200)\n"
        string+= f"`{ctx.prefix}war maxlevel <int>` - sets the max level of your targets (default 10,000)\n"
        string+= f"`{ctx.prefix}war goldping <bool>` - get pinged if out of safemode and gold is above your threshold\n"
        string+= f"`{ctx.prefix}war gold <int>` - threshold amount to get pinged for (default 5,000,000)\n"

        embed.description = string
        await ctx.send(embed=embed)

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def profile(self,ctx):

        info = db.warinfo_profile(ctx.author.id)

        embed = Embed(title="Your War Profile")
        string = f"**SMMO ID:** {info[0]}\n"
        string += f"**Guild ID:** {info[1]}\n"
        string += f"**Min Level:** {info[2]}\n"
        string += f"**Max Level:** {info[3]}\n"
        string += f"**Gold Ping:** {'Active' if info[4] else 'Inactive'}\n"
        string += f"**Gold Ping Amount:** {info[5]}"

        embed.description = string
        await ctx.send(embed=embed)


    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def guild(self,ctx,guildid : int):
        if guildid not in (408, 455, 541, 482):
            await ctx.send("It appears you did not enter a valid Friendly guild id. The options are:\n**408**\n**455**\n**541**\n")
            return
        
        db.warinfo_guild(ctx.author.id,guildid)
        await ctx.send(f"You have changed your active guild to {guildid}")

    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def minlevel(self,ctx,level : int):
        db.warinfo_minlevel(ctx.author.id,level)
        await ctx.send(f"Min level updated to: {level}")
        return


    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def maxlevel(self,ctx,level : int):
        db.warinfo_maxlevel(ctx.author.id,level)
        await ctx.send(f"Max level updated to: {level}")
        return
    


    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def goldping(self,ctx,ping : bool):
        db.warinfo_goldping(ctx.author.id,ping)
        await ctx.send(f"Gold ping set to: {'Active' if ping else 'Inactive'}")
        return


    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def gold(self,ctx,amount : int):
        db.warinfo_goldamount(ctx.author.id,amount)
        await ctx.send(f"You will be pinged if your gold is above {amount}")
        return


    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def targets(self,ctx):
        profile = db.warinfo_profile(ctx.author.id)
        targets = api.get_guild_wars(profile[1],1)
        async with ctx.typing():
            embed = Embed(title="Targets",description=f"{ctx.author.mention}'s Targets")
            attacklist = ""
            for i in range(5):
                members = api.guild_members(targets[i]['guild_2']['id'])
                members = [x for x in members if x['level'] >= profile[2] and x['level'] <= profile[3] and member['current_hp']/member['max_hp'] > 0.5]
                
                for member in members:
                    attacklist += f"[{member['name']} - Level {member['level']}](https://web.simple-mmo.com/user/attack/{member['user_id']})\n"

                    if len(attacklist) > 300:
                        embed.add_field(name="\u200b",value=attacklist)
                        attacklist = ""
                    if len(embed) > 5900:
                        await ctx.send(embed=embed)
                        embed = Embed(title="Targets",description=f"{ctx.author.mention}'s Targets")
                    
            
        await ctx.send(embed=embed)


    
    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def top15(self,ctx):
        profile = db.warinfo_profile(ctx.author.id)
        targets = api.get_guild_wars(profile[1],1)
        async with ctx.typing():
            embed = Embed(title="Targets",description=f"{ctx.author.mention}'s Targets")
            attacklist = ""
            for i in range(15):
                members = api.guild_members(targets[i]['guild_2']['id'])
                members = [x for x in members if x['level'] >= profile[2] and x['level'] <= profile[3] and member['current_hp']/member['max_hp'] > 0.5]
                
                for member in members:
                    attacklist += f"[{member['name']} - Level {member['level']}](https://web.simple-mmo.com/user/attack/{member['user_id']})\n"

                    if len(attacklist) > 300:
                        embed.add_field(name="\u200b",value=attacklist)
                        attacklist = ""
                    if len(embed) > 5900:
                        await ctx.send(embed=embed)
                        embed = Embed(title="Targets",description=f"{ctx.author.mention}'s Targets")
                    
            
            

        await ctx.send(embed=embed)


    @wars.command()
    @checks.in_fly()
    @checks.in_fly_guild()
    @checks.warinfo_linked()
    async def status(self,ctx,target : int):
        profile = db.warinfo_profile(ctx.author.id)

        guilds = api.get_guild_wars(profile[1],1)
        print(guilds)

        guild = [x for x in guilds if x['guild_2']['id'] == target]
        
        if len(guild) == 0:
            await ctx.send("That guild either doesn't exist or is not actively at war with you")
            return
        else:
            guild = guild[0]
            embed = Embed(title="War Status",description=f"**{guild['guild_1']['name']}**\n{guild['guild_1']['kills']}\n\n**{guild['guild_2']['name']}**\n{guild['guild_2']['kills']}")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Wars(bot))
    print("Wars Cog Loaded")