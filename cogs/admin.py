import discord
from discord.embeds import Embed
from discord.ext import commands
from discord.utils import get
from util import checks
import database as db
import api
import asyncio
import time
import logging

dyl = 332314562575597579
server = 444067492013408266

fly = (408,455,541,482)


logger = logging.getLogger('__name__')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


    
    
    @checks.is_owner()
    @commands.group(aliases = ['a'],hidden=True, case_insensitive=True)
    async def admin(self,ctx):
        if ctx.invoked_subcommand is None:
            pass

    
    @checks.is_owner()
    @admin.command()
    async def forceremove(self,ctx,smmoid:int):
        try:
            val = db.remove_user(smmoid)
            if val:
                await ctx.send("Success!")
            else:
                await ctx.send("They weren't removed. Either they never started verification or something else.")
        except Exception as e:
            await ctx.send("Uh oh")
            raise e



    @checks.is_owner()
    @admin.command(hidden=True)
    async def unlink(self,ctx,member:discord.Member):
        if(db.islinked(str(member.id))):
            smmoid = db.get_smmoid(str(member.id))
            if(db.remove_user(str(smmoid))):
                await ctx.send(f"User {smmoid} successfully removed")
            else:
                await ctx.send(f"User {smmoid} was not removed")
                return

            if db.is_added(str(member.id)): # if linked to a guild
                leaderrole = ctx.guild.get_role(int(db.leader_id(server)))
                ambassadorrole = ctx.guild.get_role(int(db.ambassador_role(server)))

                guildid, smmoid = db.ret_guild_smmoid(str(member.id))
                if(db.is_leader(str(member.id))):
                    
                    ambassadors = db.all_ambassadors()
                    guildambs = [x for x in ambassadors if x[2] == guildid]
                    
                    print(f"{member.name} has been removed as a leader when unlinked")
                    # if not leader, remove role and update db
                    await member.remove_roles(leaderrole)
                    db.remove_guild_user(smmoid)

                    if len(guildambs) > 0:
                        for amb in guildambs:
                            user = ctx.guild.get_member(int(amb[0]))
                            print(f"{user.name} is not an ambassador because the leader has been unlinked")
                            await user.remove_roles(ambassadorrole)
                            db.guild_ambassador_update(amb[0], False, 0)
                else:
                    #user is an ambassador
                    
                    print(f"{member.name} is not an ambassador because they unlinked")
                    await member.remove_roles(ambassadorrole)
                    db.remove_guild_user(smmoid)





        else:
            await ctx.send("This user is not linked.")



    @checks.is_owner()
    @commands.group(aliases=['fv'], hidden=True)
    async def forceverify(self, ctx, member: discord.Member, arg:int):
        try:
            db.add_new_pleb(arg,str(member.id),None,verified=True)
            await ctx.send(f"{member.name} has been linked to {arg}")
        except:
            await ctx.send(f"You messed something up or {member.name} already started the verification process. bully dyl or something to fix")




    @admin.command()
    @checks.is_owner()
    async def remove(self,ctx,arg:int):
        try:
            db.remove_user(arg)
        except Exception as e:
            await ctx.send(e)
            return

    
    




    @admin.command()
    @checks.is_owner()
    async def ping(ctx):
        start = time.perf_counter()
        message = await ctx.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(content='Pong! {:.2f}ms'.format(duration))

        
    @admin.command(name='init', description="Sets up bot in server",hidden=True)
    @checks.is_owner()
    async def init(self,ctx):
        guild = ctx.guild
        print(guild.id)

        if db.server_added(guild.id):
            await ctx.send("Server has already been initialized")
            return
        try:
            db.add_server(guild.id, guild.name)
            await ctx.send("Server successfully initialized")
            return
        except:
            await ctx.send(f"Something went wrong. Contact <@{dyl}> on Discord for help")
            return
    
    @admin.command(hidden=True)
    @checks.is_owner()
    async def set_role(self, ctx, *args):

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
                db.add_server_role(ctx.guild.id, roleid)
                await ctx.send("Role successfully added!")
                return
        
        await ctx.send(f'It looks like `{roleid}` is not in this server. Please try again')
        return


    @admin.command(aliases = ['rb'])
    @checks.is_owner()
    async def rollback(self,ctx):
        db.rollback()
        await ctx.send("Database Rollback in progress")
        return

    
    @commands.command(hidden=True)
    @checks.is_owner()
    async def reload(self,ctx,*,cog:str):
        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} -{e}')
        
        else:
            await ctx.send('**SUCCESS!**')


    @commands.command(hidden=True)
    @checks.is_owner()
    async def give(self,ctx, arg: int, members: commands.Greedy[discord.Member]):
        for member in members:
            smmoid = db.get_smmoid(str(member.id))
            if(api.pleb_status(smmoid)): # If they a pleb
                await ctx.send(f"{member.name}: <https://web.simple-mmo.com/senditem/{smmoid}/{arg}>")
            else:
                await ctx.send(f"{member.name} is not a pleb anymore")
        

def setup(bot):
    bot.add_cog(Admin(bot))
    print("Admin Cog Loaded")