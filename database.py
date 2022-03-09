from sys import exit
from sqlalchemy import create_engine, select, update, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import *
import config
from datetime import datetime, timezone
from dateutil import parser
import asyncio


# DATABASE_URL
#----------
DATABASE_URL = config.DATABASE_URL

# create engine (db object basically)
engine = create_engine(DATABASE_URL)
#print(engine.table_names())
#start automap and create session with automap
Base = automap_base()
Base.prepare(engine, reflect=True)



Server = Base.classes.server
Plebs = Base.classes.plebs
Guild = Base.classes.guilds
Friendly = Base.classes.friendly
Events = Base.classes.events
Event_info = Base.classes.event_info
Warinfo = Base.classes.warinfo
Smackback = Base.classes.smackback

asyncengine = create_async_engine(config.ASYNC_DATABASE_URL)
session = sessionmaker(
    asyncengine, expire_on_commit=False,class_=AsyncSession
)


async def add_server(serverid, name):
    async with session() as con:
        try:
            stmt = insert(Server).values(serverid=serverid,full_name=name)
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

# Returns tuple of Plebs objects
async def disc_ids(discid):
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(discid=discid,verified=True)

            ret = await (con.execute(stmt))
            return ret.fetchall()[0]
            
        except Exception as e:
            await con.rollback()
            raise e

async def add_server_role(serverid,roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.pleb_role : roleid})

            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
async def add_leader_role(serverid,roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.leader_role : roleid})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def add_ambassador_role(serverid,roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.ambassador_role : roleid})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        
async def enable_diamond_ping(serverid,bool=False):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.diamond_ping : bool})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def add_diamond_role(serverid,roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.diamond_role : roleid})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def add_diamond_channel(serverid,channelid):
    async with session() as con:
        try:
            
            stmt = update(Server).filter_by(serverid=serverid).values({Server.diamond_channel : channelid})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e

async def get_diamond_ping_info():
    async with session() as con:
        try:
            stmt = select(Server).filter_by(diamond_ping=True)
            return await con.execute(stmt).scalars().all()[0]
        except Exception as e:
            await con.rollback()
            raise e

async def server_config(serverid):
    async with session() as con:
        try:
            stmt = select(Server).filter_by(serverid=serverid)
            ret = await con.execute(stmt)

            return ret.scalars().all()[0]
        except Exception as e:
            await con.rollback()
            raise e


async def update_timestamp(serverid,timestamp : datetime):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.last_pinged : timestamp})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e


async def add_new_pleb(smmoid, discid, verification, verified = False, active = False):
    async with session() as con:
        try:
            stmt = insert(Plebs(smmoid=smmoid, discid=discid, 
                        verification=verification, verified=verified,pleb_active=active))
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def update_pleb(smmoid, discid, verification, verified = False, active = False):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(smmoid=smmoid).values({
                Plebs.discid : discid, 
                Plebs.verification : verification, 
                Plebs.verified : verified, 
                Plebs.pleb_active : active})

            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

# returns tuple of plebs
async def get_all_plebs():
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(verified=True)
            return await con.execute(stmt).fetchall()[0]
        except Exception as e:
            raise e

async def islinked(discid):
    async with session() as con:
        stmt = select(Plebs.verified).filter_by(discid=discid,verified=True)
        ret = await con.execute(stmt)
        
        if ret.fetchall() == []:
            return False
        else:
            return True

async def conn_disc(smmoid):
    async with session() as con:
        try:
            stmt = select(Plebs.discid).filter_by(smmoid=smmoid)
            ret = await con.execute(stmt)
            return ret.fetchall()[0]
        except Exception as e:
            await con.rollback()
            raise e


async def update_verified(smmoid, verified):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(smmoid=smmoid).values({Plebs.verified : verified})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def active_pleb():
    async with session() as con:
        try:
           stmt = select(Plebs).filter_by(pleb_active=True)
           ret = await con.execute(stmt)
           return ret.fetchall()[0]

        except Exception as e:
            await con.rollback()
            raise e

async def update_status(smmoid, active):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(smmoid=smmoid).values({Plebs.pleb_active : active})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def remove_user(smmoid):
    async with session() as con:
        try:
            await con.execute("DELETE FROM plebs WHERE smmoid=:param", {"param":smmoid})
            await con.commit()
            return True
        except Exception as e:
            await con.rollback()
            raise e


async def is_verified(smmoid):
    async with session() as con:
        try:
            stmt = select(Plebs.verified).filter_by(smmoid=smmoid)
            ret = await con.execute(stmt)
            x = ret.fetchall()
            
            if x != []:
                return True
            return False
        except Exception as e:
            await con.rollback()
            raise e


async def verif_key(smmoid, discid):
    async with session() as con:
        try:
            stmt = select(Plebs.verification).filter_by(smmoid=smmoid, discid=discid)
            ret = (await con.execute(stmt)).first()
            
            if ret is not None:
                return ret[0]
            
            return None
        except Exception as e:
            await con.rollback()
            raise e

async def key_init(smmoid):
    async with session() as con:
        try:
            stmt = select(Plebs.verification).filter_by(smmoid=smmoid)
            ret = (await con.execute(stmt)).first()

            if ret is not None:
                return ret[0]
            return None
        except Exception as e:
            await con.rollback()
            raise e

async def server_added(serverid):
    async with session() as con:
        return (await con.execute(select(Server).filter(Server.serverid == serverid))).scalar() is not None


async def ServerInfo(serverid):
    async with session() as con:
        stmt = select(Server).filter(Server.serverid == serverid)
        ret = (await con.execute(stmt)).first()
        if ret is not None:
            return ret[0]
        else: return None


async def all_servers():
    return session.query(Server.serverid).all()

async def is_banned(discid):
    async with session() as con:
        return (await con.execute(select(Plebs.guild_ban).filter_by(discid=str(discid)))).first()[0]

async def ban(discid,boolean : bool):
    async with session() as con:
        await con.execute(update(Plebs).filter_by(discid=str(discid)).values({Plebs.guild_ban : boolean}))
        await con.commit()
        return

async def get_smmoid(discid):
    async with session() as con:
        try:
            return (await con.execute(select(Plebs.smmoid).filter_by(discid=str(discid), verified=True))).first()[0]

        except TypeError:
            return None
        except Exception as e:
            await con.rollback()
            raise e



####################
# Guild Commands #
####################

async def is_added(discid):
    async with session() as con:
        return (await con.execute(select(Guild).filter(Guild.discid == discid))).scalar() is not None

async def add_guild_person(discid,smmoid):
    async with session() as con:
        try:
            await con.execute(insert(Guild(discid=discid, smmoid=smmoid,leader=False,ambassador=False, guildid=0)))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def guild_leader_update(discid, bLeader, guildid, smmoid):
    async with session() as con:
        try:
            await con.execute(update(Guild).filter_by(discid = discid).values({Guild.leader : bLeader, Guild.guildid : guildid, Guild.smmoid : smmoid}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e


async def guild_ambassador_update(discid, bAmbassador, guildid):
    async with session() as con:
        try:
            await con.execute(update(Guild).filter_by(discid = discid).update({Guild.ambassador : bAmbassador, Guild.guildid : guildid}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e

async def ret_guild_smmoid(discid):
    async with session() as con:
        try:
            val = (await con.execute(select(Guild.guildid, Guild.smmoid).filter_by(discid=discid))).first()
            return val[0], val[1]

        except Exception as e:
            await con.rollback()
            raise e

# Returns True/False
async def is_leader(discid):
    async with session() as con:
        try:
            ret = (await con.execute(select(Guild.leader).filter_by(discid=discid))).first()
            if ret is not None:
                return ret[0]
            else: return False

        except Exception as e:
            await con.rollback()
            raise e

# Returns True/False
async def is_ambassador(discid):
    async with session() as con:
        try:
            ret = await con.execute(select(Guild.ambassador).filter_by(discid=str(discid))).first()
            if ret is not None:
                return ret[0]
            else: return False

        except Exception as e:
            await con.rollback()
            raise e

async def ambassadors(guildid):
    async with session() as con:
        try:
            return (await con.execute(select(Guild.discid).filter_by(guildid=guildid,ambassador=True))).all()
        except Exception as e:
            await con.rollback()
            raise e

async def all_ambassadors():
    async with session() as con:
        try:
            return (await con.execute(select(Guild.discid, Guild.smmoid, Guild.guildid).filter_by(ambassador=True))).all()
        except Exception as e:
            await con.rollback()
            raise e

async def all_leaders():
    async with session() as con:
        try:
            return (await con.execute(select(Guild.discid, Guild.smmoid, Guild.guildid).filter_by(leader=True))).all()
        except Exception as e:
            await con.rollback()
            raise e

async def remove_guild_user(smmoid):
    async with session() as con:
        try:
            await con.execute("DELETE FROM guilds WHERE smmoid=:param", {"param":smmoid})
            await con.commit()
            return True
        except Exception as e:
            await con.rollback()
            raise e

async def fly_add(discid,smmoid,guildid=0):
    try:
        session.add(Friendly(discid=str(discid), smmoid=smmoid,guildid=guildid))
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e

async def fly_update(discid,smmoid,guildid=0):
    try:
        session.query(Friendly).filter_by(discid=str(discid)).update(
            {Guild.discid : discid,
            Guild.smmoid : smmoid,
            Guild.guildid : guildid}
        )
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e

async def in_fly(discid):
    try:
        ret = session.query(Friendly.guildid).filter_by(discid=str(discid)).first()
        if ret is None:
            return None
        else:
            return ret != 0
        

    except Exception as e:
        await con.rollback()
        raise e


async def all_fly():
    try:
        session.query(Friendly.discid, Friendly.smmoid,Friendly.guildid).all()

    except Exception as e:
        await con.rollback()
        raise e

async def fly_remove(discid):
    try:
        session.execute("DELETE FROM friendly WHERE discid=:param", {"param":str(discid)})
        session.commit()
        return True
    except Exception as e:
        await con.rollback()
        raise e


# Event Database Commands
async def create_event(serverid,name,eventtype,roleid):
    # session.add(Guild(discid=str(discid), smmoid=smmoid,leader=False,ambassador=False, guildid=0))
    try:
        eventtoadd = Events(serverid=serverid,name=name,type=eventtype,event_role=roleid)
        session.add(eventtoadd)
        session.commit()
        return eventtoadd.id
    except Exception as e:
        await con.rollback()
        raise e

async def start_event(eventid):
    try:
        session.query(Events).filter_by(id=eventid).update({Events.is_started : True, Events.start_time : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e
async def end_event(eventid):
    try:
        session.query(Events).filter_by(id=eventid).update({Events.is_ended : True, Events.end_time : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e

async def active_events():
    try:
        return session.query(Events.id, Events.serverid, Events.name, Events.type).filter_by(is_started=True,is_ended=False).all()
    except Exception as e:
        await con.rollback()
        raise e

async def available_events():
    try:
         return session.query(Events.id, Events.serverid, Events.name, Events.type, Events.friendly_only,Events.event_role).filter_by(is_started=False).all()
         
    except Exception as e:
        await con.rollback()
        raise e


async def participant_progress(eventid,discordid):
    try:
        return session.query(Event_info.starting_stat,Event_info.current_stat,Event_info.current_stat - Event_info.starting_stat,Event_info.last_updated).filter_by(id=eventid,discordid=discordid).first()
    except Exception as e:
        await con.rollback()
        raise e

async def event_info(eventid):
    try:
        return session.query(Events.serverid,
                            Events.name,
                            Events.type,
                            Events.is_started,
                            Events.is_ended,
                            Events.start_time,
                            Events.end_time,
                            Events.friendly_only,
                            Events.event_role).filter_by(id=eventid).first()
    except Exception as e:
        await con.rollback()
        raise e

async def event_guild_only(eventid, boolean):
    try:
        session.query(Events).filter_by(id=eventid).update({Events.friendly_only : boolean})
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e

async def join_event(eventid,discordid):
    try:
        session.add(Event_info(id=eventid,discordid=discordid))
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e

async def has_joined(eventid,discordid):
    try:
        return session.query(Event_info).filter_by(id=eventid,discordid=discordid).first() is not None
    except Exception as e:
        await con.rollback()
        raise e

async def get_participants(eventid):
    try:
        return session.query(Event_info.discordid,Event_info.starting_stat,Event_info.current_stat,Event_info.last_updated,Event_info.current_stat - Event_info.starting_stat).filter_by(id=eventid).all()
    except Exception as e:
        await con.rollback()
        raise e

async def update_start_stat(eventid,discordid,stat):
    try:
        session.query(Event_info).filter_by(id=eventid,discordid=discordid).update({Event_info.starting_stat : stat, Event_info.current_stat : stat, Event_info.last_updated : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e

async def update_stat(eventid,discordid,stat):
    try:
        session.query(Event_info).filter_by(id=eventid,discordid=discordid).update({Event_info.current_stat : stat, Event_info.last_updated : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        await con.rollback()
        raise e


###########################
# War Info Commands #
###########################

async def warinfo_setup(discordid,smmoid,guildid):
    session.add(Warinfo(discordid=discordid,smmoid=smmoid,guildid=guildid,last_pinged=datetime.now(timezone.utc)))
    commit()
    return

async def warinfo_guild(discordid,guildid):
    session.query(Warinfo).filter_by(discordid=discordid).update({Warinfo.guildid : guildid})
    commit()
    return

async def warinfo_minlevel(discordid,minlevel):
    session.query(Warinfo).filter_by(discordid=discordid).update({Warinfo.min_level : minlevel})
    commit()
    return

async def warinfo_maxlevel(discordid,maxlevel):
    session.query(Warinfo).filter_by(discordid=discordid).update({Warinfo.max_level : maxlevel})
    commit()
    return

async def warinfo_goldping(discordid,ping : bool):
    session.query(Warinfo).filter_by(discordid=discordid).update({Warinfo.gold_ping : ping})
    commit()
    return

async def warinfo_goldamount(discordid,amount : int):
    session.query(Warinfo).filter_by(discordid=discordid).update({Warinfo.gold_amount : amount})
    commit()
    return

async def warinfo_isadded(discid):
    return session.query(Warinfo).filter_by(discordid=discid).scalar() is not None

async def warinfo_profile(discid):
    return session.query(Warinfo.smmoid,
                        Warinfo.guildid,
                        Warinfo.min_level,
                        Warinfo.max_level,
                        Warinfo.gold_ping,
                        Warinfo.gold_amount).filter_by(discordid=discid).first()
async def gold_ping_users():
    return session.query(Warinfo.smmoid,
                            Warinfo.discordid,
                            Warinfo.gold_amount,
                            Warinfo.last_pinged).filter_by(gold_ping=True).all()
async def warinfo_ping_update(discordid):
    session.query(Warinfo).filter_by(discordid=discordid).update({Warinfo.last_pinged : datetime.now(timezone.utc)})
    commit()
    return

async def warinfo_test():
    members = session.query(Warinfo.discordid).all()
    for member in members:
        print(member)
        session.query(Warinfo).filter_by(discordid=member[0]).update({Warinfo.last_pinged : datetime.now(timezone.utc)})
        commit()


async def sb_create(tobesmacked : int, guildmember: int, messageid : int):
    session.add(Smackback(tobesmacked=tobesmacked,guildmember=guildmember,posted=datetime.now(timezone.utc),messageid=messageid))
    commit()
    return

async def sb_iscompleted(id : int):
    return session.query(Smackback.completed).filter_by(id=id).first()[0]

async def sb_complete(id: int):
    session.query(Smackback).filter_by(id=id).update({Smackback.completed : True})
    commit()
    return

async def sb_info(id: int):
    return session.query(Smackback.tobesmacked,
                    Smackback.guildmember,
                    Smackback.completed_by,
                    Smackback.completed,
                    Smackback.messageid,
                    Smackback.posted,
                    Smackback.completed_at).filter_by(id=id).first()





async def main():
    #async with engine.begin() as conn:




    #await server_config(731379317182824478)
    #await add_diamond_channel(538144211866746883,538150639872638986)
    #await add_server(1234,"testtest server")
    print((await is_leader(332314562575597579)))
    #print(server.serverid)

if __name__ == "__main__":
    #print(is_ambassador(str(309115527962427402)))
    # print(ambassadors(424))
    # guild_leader_update(332314562575597579,False,0)
    # print(ambassadors(424))
    # print(conn_disc(587672))
    #print(in_fly(439777465494142996))
    # update_start_stat(2,332314562575597579,5)
    # update_stat(2,332314562575597579,852)
    #print(type(get_participants(80)))
    #print(server_config(731379317182824478))
    #update_timestamp(731379317182824478,datetime.now(timezone.utc))
    #print(has_joined(10,332314562575597579))
    #rollback()
    #warinfo_test()
    #warinfo_goldamount(723340862393942027,5000000)
    # print(is_banned(332314562575597579))
    # ban(332314562575597579,False)
    # print(is_banned(332314562575597579))
    # print(is_verified(385801))
    #print(event_info(16))

    asyncio.run(main())


