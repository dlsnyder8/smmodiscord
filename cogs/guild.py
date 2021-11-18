import discord
from discord.ext import commands, tasks
from discord.utils import get
from util import checks
import database as db
import random   
import string
import api
import logging

logger = logging.getLogger('discord')



class Guild(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @checks.is_verified()
    @checks.in_main()
    @commands.group(aliases = ['g'], hidden=True)
    async def guild(self,ctx):
        if ctx.invoked_subcommand is None:
            pass


    @guild.command(aliases=['frl'],hidden=True)
    @checks.is_owner()
    async def forceremoveleader(self,ctx,dmem: discord.Member):
        pass




    @guild.command(aliases=['fc'],hidden=True)
    @checks.is_owner()
    async def forceconnect(self,ctx, dmem: discord.Member):
        # get smmo id
        if(db.islinked(str(dmem.id))):
            smmoid = db.get_smmoid(str(dmem.id))
        else:
            await ctx.send("They are not linked")
            return

        #add to database
        if not db.is_added(str(dmem.id)):
            db.add_guild_person(str(dmem.id),smmoid)

        # get guild from profile (get_all())
        profile = api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("They are not in a guild")
            return
        # check if leader of guild
        members = api.guild_members(guildid)
        for member in members:
            
            
            if member["user_id"] == smmoid:
                if member["position"] == "Leader":
                # if leader, add role and add info to DB
                    leaderid = db.leader_id(ctx.guild.id)
                    await dmem.add_roles(ctx.guild.get_role(int(leaderid)))
                    await ctx.send("They have been verified as a leader")
                    db.guild_leader_update(str(dmem.id),True,guildid,smmoid)
                    return
                else:
                    await ctx.send(f"They are only a member of your guild. If they want the Ambassador role, their guild leader will need to connect and run `{ctx.prefix}g aa <ID/@mention>`")
                    return

    
    @guild.command(aliases = ['c'], usage="", description="Gives you the leader role if you're the leader of a guild. You must verify with the bot first.")
    @checks.is_verified()
    async def connect(self,ctx):
        # get smmo id
        smmoid = db.get_smmoid(str(ctx.author.id))

        #add to database
        if not db.is_added(ctx.author.id):
            db.add_guild_person(str(ctx.author.id),smmoid)

        # get guild from profile (get_all())
        profile = api.get_all(smmoid)
        try:
            guildid = profile["guild"]["id"]
        except KeyError as e:
            await ctx.send("You are not in a guild")
            return
        # check if leader of guild
        members = api.guild_members(guildid)
        for member in members:
            
            
            if member["user_id"] == smmoid:
                if member["position"] == "Leader":
                # if leader, add role and add info to DB
                    leaderid = db.leader_id(ctx.guild.id)
                    await ctx.author.add_roles(ctx.guild.get_role(int(leaderid)))
                    await ctx.send("You have been verified as a leader.")
                    db.guild_leader_update(str(ctx.author.id),True,guildid, smmoid)
                    channel = self.bot.get_channel(758175768496177183)
                    await channel.send(f"Welcome {ctx.author.mention}! Please be sure to read <#758154183164690483> before posting your first advertisement.")
                    return
                else:
                    await ctx.send(f"You are only a member of your guild. If you want the Ambassador role, your guild leader will need to connect and run `{ctx.prefix}g aa <ID/@mention>`")
                    return
        
    
    @checks.is_leader()
    @guild.command(aliases = ['aa'],usage="<ID/@Mention>",description="Adds a user as an ambassador for your guild. They must verify with the bot first.")
    async def addambassador(self,ctx,*,member: discord.Member):
        
        # get member smmoid and check if verified
        smmoid = db.get_smmoid(str(member.id))

        if smmoid is None:
            embed = discord.Embed(
                title="Not Verified", 
                description=f"{member.mention} is not verified. They need to run `{ctx.prefix}verify <smmoid>` to start the process", 
                color=0x00ff00)

            await ctx.send(
                embed=embed
            )
            return
        if not db.is_added(str(member.id)):
            db.add_guild_person(str(member.id),smmoid)
        

        guildid, c_smmoid = db.ret_guild_smmoid(str(ctx.author.id))

        # check if num of ambassadors is more than two
        ambassadors = db.ambassadors(guildid)

        if len(ambassadors) == 2:
            await ctx.send(embed=discord.Embed(
                title="Enough Ambassadors",
                description=f"You can only have 2 ambassadors. You can remove your ambassadors using `{ctx.prefix}g ra <ID/@mention>`. If you don't remember your ambassadors, you can use `{ctx.prefix}g ca` to list them all."
            ))
            return

        
        
        # check if member is in caller's guild
        
        members = api.guild_members(guildid)
        for mem in members:
            if mem["user_id"] == smmoid:
                # add ambassador role if all True
                # add player to db
                ambassadorid = db.ambassador_role(ctx.guild.id)
                await member.add_roles(ctx.guild.get_role(int(ambassadorid)))
                db.guild_ambassador_update(str(member.id),True,guildid)

                channel = self.bot.get_channel(758175768496177183)
                await channel.send(f"Welcome {member.mention}! Please be sure to read <#758154183164690483> and consult with your guild leader before posting an advertisement.")

                await ctx.send(f"{member.display_name} is now a Guild Ambassador for your guild")
                return

        await ctx.send(f"{member.display_name} must be in your guild to add them as an ambassador")
        return

        
        
    
    @checks.is_verified()
    @checks.is_leader()
    @guild.command(aliases = ['ra'],usage="<ID/@Mention>",description="Removes an ambassador for your guild.")
    async def removeambassador(self,ctx,*,member:discord.Member):
        # check if member is an ambassador 
        val,guildid =db.is_ambassador(str(member.id))

        if val:
            # check if member ambassador for guild leader
            lguildid,lsmmoid = db.ret_guild_smmoid(str(ctx.author.id))
            if lguildid == guildid:
                ambassadorid = db.ambassador_role(ctx.guild.id)
                await member.remove_roles(ctx.guild.get_role(int(ambassadorid)))
                db.guild_ambassador_update(str(member.id),False,guildid)
                await ctx.send(f"{member.mention} has been removed as an ambassador for your guild")
                return

            else:
                await ctx.send(f"{member.mention} is not an ambassador for your guild")
                return
        
        else:
            await ctx.send(f"{member.mention} is not an ambassador")
            return 


        

    @checks.is_verified()
    @checks.is_leader()
    @guild.command(aliases = ['ca', 'ambassadors'],usage="",description="Lists all current ambassadors for your guild.")
    async def currentambassadors(self,ctx):
        lguild, smmoid = db.ret_guild_smmoid(str(ctx.author.id))
        ambassadors = db.ambassadors(lguild)

        embed = discord.Embed(
            title="Ambassadors",
            color=0x0000FF
        )
        x = 1
        for ambassador in ambassadors:
            embed.add_field(name=f"Ambassador {x}:", value=f"<@{ambassador[0]}>")
            x += 1
        
        await ctx.send(embed=embed)



    @checks.is_owner()
    @guild.command(hidden=True)
    async def leaderrole(self,ctx, *args):
        if not db.server_added(ctx.guild.id):
            await ctx.send("Please run `^a init` before you run this command!")
            return

        # args should only have len of 1
        if(len(args) != 1):
            await ctx.send("Incorrect Number of Arguments! \n Correct usage: ^ap [role id]")
            return
        roles = ctx.guild.roles
        roleid = args[0]

        #cleanse roleid

        if '@' in roleid:
            roleid = roleid.replace('<', '')
            roleid = roleid.replace('@', '')
            roleid = roleid.replace('>', '')
            roleid = roleid.replace('&', '')

        roleid = int(roleid)
        for role in roles:
            
            if role.id == roleid:
                db.add_leader_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return
        
        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return

    @checks.is_owner()
    @guild.command(hidden=True)
    async def ambrole(self,ctx, *args):
        if not db.server_added(ctx.guild.id):
            await ctx.send("Please run `^a init` before you run this command!")
            return

        # args should only have len of 1
        if(len(args) != 1):
            await ctx.send("Incorrect Number of Arguments! \n Correct usage: ^ap [role id]")
            return
        roles = ctx.guild.roles
        roleid = args[0]

        #cleanse roleid

        if '@' in roleid:
            roleid = roleid.replace('<', '')
            roleid = roleid.replace('@', '')
            roleid = roleid.replace('>', '')
            roleid = roleid.replace('&', '')

        roleid = int(roleid)
        for role in roles:
            
            if role.id == roleid:
                db.add_ambassador_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return
        
        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return

    
def setup(bot):
    bot.add_cog(Guild(bot))
    print("Guild Cog Loaded")