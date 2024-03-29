from sys import exit
from sqlalchemy import create_engine, select, update, insert
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.exc import *
from datetime import datetime, timezone
import asyncio
import config
import api


# DATABASE_URL
# ----------
DATABASE_URL = config.DATABASE_URL

# create engine (db object basically)
engine = create_engine(DATABASE_URL, pool_size=1, max_overflow=0)
# print(engine.table_names())
# start automap and create session with automap
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
Profile_Data = Base.classes.profile_data
engine.dispose()

if config.main_acct:
    size = 3
else:
    size = 1
asyncengine = create_async_engine(
    config.ASYNC_DATABASE_URL, pool_pre_ping=True, pool_size=size, max_overflow=size)
session = sessionmaker(
    asyncengine, expire_on_commit=False, class_=AsyncSession
)


async def execute(command: str):
    async with session() as con:
        try:
            data = await con.execute(command)
            await con.commit()
            return [r for r in data.fetchall()]

        except Exception as e:
            await con.rollback()
            return e
        finally:
            await con.close()


async def add_server(serverid, name):
    async with session() as con:
        try:
            stmt = insert(Server).values(serverid=serverid, full_name=name)
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

"""Returns tuple of Plebs objects"""


async def disc_ids(discid):
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(discid=discid, verified=True)

            data = await (con.execute(stmt))
            return [r[0] for r in data.fetchall()]

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def add_server_role(serverid, roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(
                serverid=serverid).values({Server.pleb_role: roleid})

            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def add_leader_role(serverid, roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.leader_role: roleid})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def add_ambassador_role(serverid, roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.ambassador_role: roleid})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def enable_diamond_ping(serverid, bool=False):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(
                serverid=serverid).values({Server.diamond_ping: bool})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def premium_server(serverid):
    async with session() as con:
        try:
            stmt = select(Server).filter_by(serverid=serverid)
            data = await con.execute(stmt)
            data = data.fetchone()[0]
            
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

    return data.premium

async def set_premium(serverid,isprem : bool):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values({Server.premium : isprem})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()
        
    

async def add_diamond_role(serverid, roleid):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.diamond_role: roleid})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def add_diamond_channel(serverid, channelid):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.diamond_channel: channelid})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def change_diamond_amount(serverid, amount):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.diamond_amount: amount})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def change_guild_role(serverid, roleid):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.guild_role: roleid})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def change_non_guild_role(serverid, roleid):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.non_guild_role: roleid})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_token(serverid, api_token):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.api_token: api_token})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_guilds(serverid, guilds):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.guilds: guilds})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_logging(serverid, channel):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.log_channel: channel})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_welcome(serverid, channel):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.welcome_channel: channel})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_guild_name(serverid, name):
    async with session() as con:
        try:

            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.guild_name: name})

            await con.execute(stmt)
            await con.commit()

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def get_diamond_ping_info():
    async with session() as con:
        try:
            stmt = select(Server).filter_by(diamond_ping=True)
            data = await con.execute(stmt)
            return [r[0] for r in data.fetchall()]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def server_config(serverid):
    async with session() as con:
        try:
            stmt = select(Server).filter_by(serverid=serverid)
            data = await con.execute(stmt)

            return [r[0] for r in data.fetchall()][0]
        except IndexError:
            return None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_timestamp(serverid, timestamp: datetime):
    async with session() as con:
        try:
            stmt = update(Server).filter_by(serverid=serverid).values(
                {Server.last_pinged: timestamp})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def add_new_pleb(smmoid, discid, verification, verified=False, active=False):
    async with session() as con:
        try:
            stmt = insert(Plebs).values(smmoid=smmoid, discid=discid,
                                        verification=verification, verified=verified, pleb_active=active)
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

async def get_yearly_token(discid):
    async with session() as con:
        try:
            stmt = select(Plebs.yearlytoken).filter_by(verified=True, discid=discid)
            data = await con.execute(stmt)
            return data.fetchone()[0]
        except Exception as e:
            raise e
        finally:
            await con.close()

async def update_yearly_token(discid, token):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(verified=True, discid=discid).values({
                Plebs.yearlytoken: token
            })
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e 
        finally:
            await con.close()


async def update_pleb(smmoid, discid, verification, verified=False, active=False):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(smmoid=smmoid).values({
                Plebs.discid: discid,
                Plebs.verification: verification,
                Plebs.verified: verified,
                Plebs.pleb_active: active})

            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

# returns tuple of plebs


async def get_all_plebs():
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(verified=True)
            data = await con.execute(stmt)
            return [r[0] for r in data.fetchall()]
        except Exception as e:
            raise e
        finally:
            await con.close()


async def islinked(discid):
    async with session() as con:
        try:
            stmt = select(Plebs.verified).filter_by(
                discid=discid, verified=True)
            ret = await con.execute(stmt)

            if ret.fetchall() == []:
                return False
            else:
                return True
        finally:
            await con.close()


async def conn_disc(smmoid):
    async with session() as con:
        try:
            stmt = select(Plebs.discid).filter_by(smmoid=smmoid)
            ret = await con.execute(stmt)
            return ret.fetchall()[0]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_verified(smmoid, verified):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(
                smmoid=smmoid).values({Plebs.verified: verified})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def active_pleb():
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(pleb_active=True)
            ret = await con.execute(stmt)
            return ret.fetchall()[0]

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_status(smmoid, active):
    async with session() as con:
        try:
            stmt = update(Plebs).filter_by(smmoid=smmoid).values(
                {Plebs.pleb_active: active})
            await con.execute(stmt)
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def remove_user(smmoid):
    async with session() as con:
        try:
            await con.execute("DELETE FROM plebs WHERE smmoid=:param", {"param": smmoid})
            await con.commit()
            return True
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def is_verified(smmoid):
    async with session() as con:
        try:
            stmt = select(Plebs.verified).filter_by(smmoid=smmoid)
            ret = await con.execute(stmt)
            x = ret.fetchall()[0]

            if x != []:
                return x[0]
            return False

        except IndexError:
            return False

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def verif_key(smmoid, discid):
    async with session() as con:
        try:
            stmt = select(Plebs.verification).filter_by(
                smmoid=smmoid, discid=discid)
            ret = (await con.execute(stmt)).first()

            if ret is not None:
                return ret[0]

            return None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


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
        finally:
            await con.close()


async def server_added(serverid):
    async with session() as con:
        try:
            return (await con.execute(select(Server).filter(Server.serverid == serverid))).scalar() is not None
        finally:
            await con.close()


async def ServerInfo(serverid):
    async with session() as con:
        try:
            stmt = select(Server).filter(Server.serverid == serverid)
            ret = (await con.execute(stmt)).first()
            if ret is not None:
                return ret[0]
            else:
                return None
        finally:
            await con.close()


async def all_servers():
    async with session() as con:
        try:
            stmt = select(Server)
            data = await con.execute(stmt)
            return [r[0] for r in data.fetchall()]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def is_banned(discid):
    async with session() as con:
        try:
            ret = (await con.execute(select(Plebs.guild_ban).filter_by(discid=discid))).first()[0]
            return False if ret is None else ret
        finally:
            await con.close()


async def ban(discid, boolean: bool):
    async with session() as con:
        try:
            await con.execute(update(Plebs).filter_by(discid=discid).values({Plebs.guild_ban: boolean}))
            await con.commit()
            return
        finally:
            await con.close()


async def get_smmoid(discid):
    async with session() as con:
        try:
            return (await con.execute(select(Plebs.smmoid).filter_by(discid=discid, verified=True))).first()[0]

        except TypeError:
            return None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def user_info(discid):
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(discid=discid, verified=True)
            data = await con.execute(stmt)
            data = data.first()
            return None if data == [] else data[0]
        except TypeError:
            return None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_arcade_tokens(discid, tokens):
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(discid=discid, verified=True)
            user = (await con.execute(stmt)).first()[0]

            user.tokens += tokens
            await con.commit()
        except:
            pass
        finally:
            await con.close()

    return user.tokens


async def update_arcade_tickets(discid, tickets):
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(discid=discid, verified=True)
            user = (await con.execute(stmt)).first()[0]

            user.tickets += tickets
            await con.commit()
        except:
            pass
        finally:
            await con.close()

    return user.tickets


async def all_arcade_info():
    async with session() as con:
        try:
            stmt = select(Plebs).filter_by(verified=True)
            data = await con.execute(stmt)
            data = [r[0] for r in data.fetchall()]

        except:
            pass
        finally:
            await con.close()

    return data

####################
# Guild Commands #
####################


async def is_added(discid):
    async with session() as con:
        try:
            return (await con.execute(select(Guild).filter(Guild.discid == discid))).scalar() is not None
        finally:
            await con.close()


async def add_guild_person(discid, smmoid):
    async with session() as con:
        try:
            await con.execute(insert(Guild).values(discid=discid, smmoid=smmoid, leader=False, ambassador=False, guildid=0))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def guild_leader_update(discid, bLeader, guildid, smmoid):
    async with session() as con:
        try:
            await con.execute(update(Guild).filter_by(discid=discid).values({Guild.leader: bLeader, Guild.guildid: guildid, Guild.smmoid: smmoid}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def guild_ambassador_update(discid, bAmbassador, guildid):
    async with session() as con:
        try:
            await con.execute(update(Guild).filter_by(discid=discid).values({Guild.ambassador: bAmbassador, Guild.guildid: guildid}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def ret_guild_smmoid(discid):
    async with session() as con:
        try:
            val = (await con.execute(select(Guild.guildid, Guild.smmoid).filter_by(discid=discid))).first()
            return val[0], val[1]

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

# Returns True/False


async def is_leader(discid):
    async with session() as con:
        try:
            ret = (await con.execute(select(Guild.leader).filter_by(discid=discid))).first()
            if ret is not None:
                return ret[0]
            else:
                return False

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

# Returns True/False


async def is_ambassador(discid):
    async with session() as con:
        try:
            ret = await con.execute(select(Guild.ambassador).filter_by(discid=discid)).first()
            if ret is not None:
                return ret[0]
            else:
                return False

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def ambassadors(guildid):
    async with session() as con:
        try:
            data = (await con.execute(select(Guild).filter_by(guildid=guildid, ambassador=True)))

            return [r[0] for r in data.fetchall()]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def all_ambassadors():
    async with session() as con:
        try:
            data = (await con.execute(select(Guild.discid, Guild.smmoid, Guild.guildid).filter_by(ambassador=True)))
            return data.fetchall()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def all_leaders():
    async with session() as con:
        try:
            data = (await con.execute(select(Guild.discid, Guild.smmoid, Guild.guildid).filter_by(leader=True)))
            return data.fetchall()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def remove_guild_user(smmoid):
    async with session() as con:
        try:
            await con.execute("DELETE FROM guilds WHERE smmoid=:param", {"param": smmoid})
            await con.commit()
            return True
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def fly_add(discid, smmoid, guildid=0):
    async with session() as con:
        try:
            await con.execute(insert(Friendly).values(discid=discid, smmoid=smmoid, guildid=guildid))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def fly_update(discid, smmoid, guildid=0):
    async with session() as con:
        try:
            await con.execute(update(Friendly).filter_by(discid=discid).values(
                {Guild.discid: discid,
                 Guild.smmoid: smmoid,
                 Guild.guildid: guildid}
            ))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def in_fly(discid):
    async with session() as con:
        try:
            ret = (await con.execute(select(Friendly.guildid).filter_by(discid=discid))).first()
            if ret is None:
                return False
            else:
                return ret != 0

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def fly_remove(discid):
    async with session() as con:
        try:
            await con.execute("DELETE FROM friendly WHERE discid=:param", {"param": discid})
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


# Event Database Commands
async def create_event(serverid: int, name: str, eventtype: str, roleid: int):
    async with session() as con:
        try:

            event = await con.execute(insert(Events).values(serverid=serverid,
                                                            name=name,
                                                            type=eventtype, event_role=roleid))
            await con.commit()
            return event.inserted_primary_key[0]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def start_event(eventid: int, server: int):
    async with session() as con:
        try:
            await con.execute(update(Events).filter_by(id=int(eventid), serverid=server).values(
                {Events.is_started: True, Events.start_time: datetime.utcnow()}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def end_event(eventid: int, server: int):
    async with session() as con:
        try:
            await con.execute(update(Events).filter_by(id=int(eventid), serverid=server).values({Events.is_ended: True, Events.end_time: datetime.utcnow()}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def cleanup_event(eventid: int, server: int):
    async with session() as con:
        try:
            await con.execute(update(Events).filter_by(id=int(eventid), serverid=server).values({Events.event_role: None}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def active_events(server: int = None):
    async with session() as con:
        try:
            if server is not None:
                data = await con.execute(select(Events).filter_by(is_started=True, is_ended=False, serverid=server))
            else:
                data = await con.execute(select(Events).filter_by(is_started=True, is_ended=False))
            return [r[0] for r in data.fetchall()]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def available_events(server: int):
    async with session() as con:
        try:
            data = await con.execute(select(Events).filter_by(is_started=False, serverid=server))
            return [r[0] for r in data.fetchall()]

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def finished_events(server: int):
    async with session() as con:
        try:
            stmt = select(Events).filter(Events.is_started == True, Events.is_ended ==
                                         True, Events.event_role != None, Events.serverid == server)

            data = await con.execute(stmt)

            data = [r[0] for r in data.fetchall()]
            return data

        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def participant_progress(eventid: int, discordid: int):
    async with session() as con:
        try:
            return (await con.execute(select(Event_info.starting_stat,
                                             Event_info.current_stat,
                                             Event_info.current_stat - Event_info.starting_stat,
                                             Event_info.last_updated).filter_by(id=eventid,
                                                                                discordid=discordid))).first()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def event_info(eventid: int, server: int):
    async with session() as con:
        try:
            return (await con.execute(select(Events).filter_by(id=int(eventid), serverid=server))).first()[0]

        except TypeError:
            return None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def event_guild_only(eventid: int, server: int, boolean: bool):
    async with session() as con:
        try:
            await con.execute(update(Events).filter_by(id=eventid, serverid=server).values({Events.guild_only: boolean}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def join_event(eventid: int, discordid):
    async with session() as con:
        try:
            await con.execute(insert(Event_info).values(id=int(eventid), discordid=discordid))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def has_joined(eventid: int, discordid):
    async with session() as con:
        try:
            return (await con.execute(select(Event_info).filter_by(id=int(eventid), discordid=discordid))).first() is not None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def valid_event(eventid: int, server: int):
    async with session() as con:
        try:

            valid = (await con.execute(select(Events).filter_by(id=int(eventid),serverid=server))).fetchone()
            return False if valid is None else valid[0]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

# Returns a list of Event_info objects
# If eventid is not valid, returns an empty list


async def get_participants(eventid: int):
    async with session() as con:
        try:
            valid = (await con.execute(select(Events).filter_by(id=int(eventid)))).fetchone()
            if not valid:
                return None
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

    async with session() as con:
        try:
            data = await con.execute(select(Event_info).filter_by(id=int(eventid)))
            return [r[0] for r in data.fetchall()]
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_start_stat(eventid, discordid, stat):
    async with session() as con:
        try:
            await con.execute(update(Event_info).filter_by(id=int(eventid),
                                                           discordid=discordid).values({Event_info.starting_stat: stat,
                                                                                        Event_info.current_stat: stat,
                                                                                        Event_info.last_updated: datetime.now(timezone.utc)}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


async def update_stat(eventid, discordid, stat):
    async with session() as con:
        try:
            await con.execute(update(Event_info).filter_by(id=int(eventid),
                                                           discordid=discordid).values({Event_info.current_stat: stat,
                                                                                        Event_info.last_updated: datetime.now(timezone.utc)}))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()


###########################
# War Info Commands #
###########################

async def warinfo_setup(discordid, smmoid, guildid):
    async with session() as con:
        try:
            await con.execute(insert(Warinfo).values(discordid=discordid,
                                                     smmoid=smmoid,
                                                     guildid=guildid,
                                                     last_pinged=datetime.now(timezone.utc)))
            await con.commit()
            return
        finally:
            await con.close()


async def warinfo_guild(discordid, guildid):
    async with session() as con:
        try:
            await con.execute(update(Warinfo).filter_by(discordid=discordid).values({Warinfo.guildid: guildid}))
            await con.commit()
            return
        finally:
            await con.close()


async def warinfo_minlevel(discordid, minlevel):
    async with session() as con:
        try:
            await con.execute(update(Warinfo).filter_by(discordid=discordid).values({Warinfo.min_level: minlevel}))
            await con.commit()
            return
        finally:
            await con.close()


async def warinfo_maxlevel(discordid, maxlevel):
    async with session() as con:
        try:
            await con.execute(update(Warinfo).filter_by(discordid=discordid).values({Warinfo.max_level: maxlevel}))
            await con.commit()
            return
        finally:
            await con.close()


async def warinfo_goldping(discordid, ping: bool):
    async with session() as con:
        try:
            await con.execute(update(Warinfo).filter_by(discordid=discordid).values({Warinfo.gold_ping: ping}))
            await con.commit()
            return
        finally:
            await con.close()


async def warinfo_goldamount(discordid, amount: int):
    async with session() as con:
        try:
            await con.execute(update(Warinfo).filter_by(discordid=discordid).values({Warinfo.gold_amount: amount}))
            await con.commit()
            return
        finally:
            await con.close()


async def warinfo_isadded(discid):
    async with session() as con:
        try:
            return (await con.execute(select(Warinfo).filter_by(discordid=discid))).scalar() is not None
        finally:
            await con.close()


async def warinfo_profile(discid):
    async with session() as con:
        try:
            return (await con.execute(select(Warinfo).filter_by(discordid=discid))).first()[0]
        finally:
            await con.close()


async def gold_ping_users():
    async with session() as con:
        try:
            data = (await con.execute(select(Warinfo).filter_by(gold_ping=True)))
            return [r[0] for r in data.fetchall()]
        finally:
            await con.close()


async def warinfo_ping_update(discordid):
    async with session() as con:
        try:
            await con.execute(update(Warinfo).filter_by(discordid=discordid).values({Warinfo.last_pinged: datetime.now(timezone.utc)}))
            await con.commit()
            return
        finally:
            await con.close()


async def rollback():
    async with session() as con:
        await con.rollback()
        
async def store_data(smmoid, data):
    async with session() as con:
        try:
            await con.execute(insert(Profile_Data).values(smmoid=smmoid, data=data, timestamp = datetime.now(timezone.utc)))
            await con.commit()
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()
            
async def get_data(smmoid):
    async with session() as con:
        try:
            data = await con.execute(select(Profile_Data).filter_by(smmoid=smmoid).order_by(Profile_Data.timestamp.desc()).limit(1))
            result = data.first()
            return (result[0].data, result[0].timestamp) if result else (None, datetime.now(timezone.utc))
        except Exception as e:
            await con.rollback()
            raise e
        finally:
            await con.close()

# async def warinfo_test():
#     async with session() as con:
    #     members = session.query(Warinfo.discordid).all()
    #     for member in members:
    #         print(member)
    #         session.query(Warinfo).filter_by(discordid=member[0]).update({Warinfo.last_pinged : datetime.now(timezone.utc)})
    #         commit()


# async def sb_create(tobesmacked : int, guildmember: int, messageid : int):
#     async with session() as con:
#         await con.execute(insert(Smackback).values(tobesmacked=tobesmacked,guildmember=guildmember,posted=datetime.now(timezone.utc),messageid=messageid))
#         await con.commit()
#         return

# async def sb_iscompleted(id : int):
#     return session.query(Smackback.completed).filter_by(id=id).first()[0]

# async def sb_complete(id: int):
#     session.query(Smackback).filter_by(id=id).update({Smackback.completed : True})
#     commit()
#     return

# async def sb_info(id: int):
#     return session.query(Smackback.tobesmacked,
#                     Smackback.guildmember,
#                     Smackback.completed_by,
#                     Smackback.completed,
#                     Smackback.messageid,
#                     Smackback.posted,
#                     Smackback.completed_at).filter_by(id=id).first()


async def main():
    # async with engine.begin() as conn:
    print(await is_banned(302100896249282571))
    # await server_config(731379317182824478)
    # await add_diamond_channel(538144211866746883,538150639872638986)
    # await add_server(1234,"testtest server")
    # print((await is_leader(332314562575597579)))
    # print(server.serverid)

if __name__ == "__main__":
    

    asyncio.run(main())
