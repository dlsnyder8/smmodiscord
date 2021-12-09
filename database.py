import os
from sys import stderr, exit
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, create_session, Session
from sqlalchemy.ext.automap import automap_base
import config
from datetime import datetime, timezone
from dateutil import parser


# DATABASE_URL
#----------
DATABASE_URL = config.DATABASE_URL

# create engine (db object basically)
engine = create_engine(DATABASE_URL)
#start automap and create session with automap
Base = automap_base()
Base.prepare(engine, reflect=True)

session = Session(engine)

Server = Base.classes.server
Plebs = Base.classes.plebs
Guild = Base.classes.guilds
Friendly = Base.classes.friendly
Events = Base.classes.events
Event_info = Base.classes.event_info

def add_server(serverid, name):
    try:
        session.add(Server(serverid=serverid,full_name=name))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def disc_ids(discid):
    try:
       val = session.query(Plebs.smmoid, Plebs.verified).filter_by(discid=discid,verified=True).all()
       return val
    except Exception as e:
        session.rollback()
        raise e 

def add_server_role(serverid,roleid):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.pleb_role : roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
def add_leader_role(serverid,roleid):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.leader_role : roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def add_ambassador_role(serverid,roleid):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.ambassador_role : roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
        
def enable_diamond_ping(serverid,bool=False):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.diamond_ping : bool})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def add_diamond_role(serverid,roleid):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.diamond_role : roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def add_diamond_channel(serverid,channelid):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.diamond_channel : channelid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def get_diamond_ping_info():
    try:
        return session.query(Server.serverid,Server.diamond_role,Server.diamond_channel, Server.last_pinged).filter_by(diamond_ping=True).all()
    except Exception as e:
        session.rollback()
        raise e

def update_timestamp(serverid,timestamp : datetime):
    try:
        session.query(Server).filter_by(serverid=serverid).update({Server.last_pinged : timestamp})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def add_new_pleb(smmoid, discid, verification, verified = False, active = False):
    try:
        session.add(Plebs(smmoid=smmoid, discid=discid, 
                    verification=verification, verified=verified,pleb_active=active))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def update_pleb(smmoid, discid, verification, verified = False, active = False):
    try:
        session.query(Plebs).filter_by(smmoid=smmoid).update({
            Plebs.discid : discid, 
            Plebs.verification : verification, 
            Plebs.verified : verified, 
            Plebs.pleb_active : active})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def get_all_plebs():
    try:
        plebs = session.query(Plebs.discid, Plebs.smmoid).filter_by(verified=True).all()
        return plebs
    except Exception as e:
        raise e

def islinked(discid):
        out = session.query(Plebs.verified).filter_by(discid=str(discid),verified=True).first()
        if out is None:
            return False
        else:
            return True

def conn_disc(smmoid):
    try:
        user = session.query(Plebs.discid).filter_by(smmoid=smmoid).first()[0]
        return user
    except Exception as e:
        session.rollback()
        raise e

def rollback():
    session.rollback()

def update_verified(smmoid, verified):
    try:
        session.query(Plebs).filter_by(smmoid=smmoid).update({Plebs.verified : verified})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def active_pleb():
    try:
        return session.query(Plebs.smmoid, Plebs.discid).filter_by(pleb_active=True).all()

    except Exception as e:
        session.rollback()
        raise e

def update_status(smmoid, active):
    try:
        session.query(Plebs).filter_by(smmoid=smmoid).update({Plebs.pleb_active : active})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def remove_user(smmoid):
    try:
        session.execute("DELETE FROM plebs WHERE smmoid=:param", {"param":smmoid})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e


def is_verified(smmoid):
    try:
        x = session.query(Plebs.verified).filter_by(smmoid=smmoid).first()
        if x is not None:
            x = x[0]
        return x
    except Exception as e:
        session.rollback()
        raise e
def verif_key(smmoid, discid):
    try:
        x = session.query(Plebs.verification).filter_by(smmoid=smmoid, discid=discid).first()
        if x is not None:
            x = x[0]
        print(x)
        return x
    except Exception as e:
        session.rollback()
        raise e

def key_init(smmoid):
    try:
        x = session.query(Plebs.verification).filter_by(smmoid=smmoid).first()
        if x is not None:
            x = x[0]
        print(x)
        return x
    except Exception as e:
        session.rollback()
        raise e

def server_added(serverid):
    return session.query(Server).filter(Server.serverid == serverid).scalar() is not None

def pleb_id(serverid):
    val = session.query(Server.pleb_role).filter(Server.serverid == serverid).first()
    if val is not None:
        return val[0]
    else: return None

def leader_id(serverid):
    return session.query(Server.leader_role).filter(Server.serverid == serverid).first()[0]

def ambassador_role(serverid):
    return session.query(Server.ambassador_role).filter(Server.serverid == serverid).first()[0]

def all_servers():
    return session.query(Server.serverid).all()

def get_smmoid(discid):
    try:
        return session.query(Plebs.smmoid).filter_by(discid=str(discid), verified=True).first()[0]

    except TypeError:
        return None
    except Exception as e:
        session.rollback()
        raise e
####################
# Guild Commands #
####################

def is_added(discid):
    return session.query(Guild).filter(Guild.discid == str(discid)).scalar() is not None

def add_guild_person(discid,smmoid):
    try:
        session.add(Guild(discid=str(discid), smmoid=smmoid,leader=False,ambassador=False, guildid=0))
    except Exception as e:
        session.rollback()
        raise e

def guild_leader_update(discid, bLeader, guildid, smmoid):
    try:
        session.query(Guild).filter_by(discid = str(discid)).update({Guild.leader : bLeader, Guild.guildid : guildid, Guild.smmoid : smmoid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def guild_ambassador_update(discid, bAmbassador, guildid):
    try:
        session.query(Guild).filter_by(discid = str(discid)).update({Guild.ambassador : bAmbassador, Guild.guildid : guildid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def ret_guild_smmoid(discid):
    try:
        val = session.query(Guild.guildid, Guild.smmoid).filter_by(discid=str(discid)).first()
        return val[0], val[1]

    except Exception as e:
        session.rollback()
        raise e

def is_leader(discid):
    try:
        return session.query(Guild.leader).filter_by(discid=str(discid)).first()

    except Exception as e:
        session.rollback()
        raise e

def is_ambassador(discid):
    try:
        return session.query(Guild.ambassador,Guild.guildid).filter_by(discid=str(discid)).first()

    except Exception as e:
        session.rollback()
        raise e

def ambassadors(guildid):
    try:
        return session.query(Guild.discid).filter_by(guildid=guildid,ambassador=True).all()
    except Exception as e:
        session.rollback()
        raise e

def all_ambassadors():
    try:
        return session.query(Guild.discid, Guild.smmoid, Guild.guildid).filter_by(ambassador=True).all()
    except Exception as e:
        session.rollback()
        raise e

def all_leaders():
    try:
        val = session.query(Guild.discid, Guild.smmoid, Guild.guildid).filter_by(leader=True).all()
        return val
    except Exception as e:
        session.rollback()
        raise e

def remove_guild_user(smmoid):
    try:
        session.execute("DELETE FROM guilds WHERE smmoid=:param", {"param":smmoid})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e

def fly_add(discid,smmoid,guildid=0):
    try:
        session.add(Friendly(discid=str(discid), smmoid=smmoid,guildid=guildid))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def fly_update(discid,smmoid,guildid=0):
    try:
        session.query(Friendly).filter_by(discid=str(discid)).update(
            {Guild.discid : discid,
            Guild.smmoid : smmoid,
            Guild.guildid : guildid}
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def in_fly(discid):
    try:
        ret = session.query(Friendly.guildid).filter_by(discid=str(discid)).first()
        if ret is None:
            return None
        else:
            return ret != 0
        

    except Exception as e:
        session.rollback()
        raise e


def all_fly():
    try:
        session.query(Friendly.discid, Friendly.smmoid,Friendly.guildid).all()

    except Exception as e:
        session.rollback()
        raise e

def fly_remove(discid):
    try:
        session.execute("DELETE FROM friendly WHERE discid=:param", {"param":str(discid)})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e


# Event Database Commands
def create_event(serverid,name,eventtype):
    # session.add(Guild(discid=str(discid), smmoid=smmoid,leader=False,ambassador=False, guildid=0))
    try:
        eventtoadd = Events(serverid=serverid,name=name,type=eventtype)
        session.add(eventtoadd)
        session.commit()
        return eventtoadd.id
    except Exception as e:
        session.rollback()
        raise e

def start_event(eventid):
    try:
        session.query(Events).filter_by(id=eventid).update({Events.is_started : True, Events.start_time : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
def end_event(eventid):
    try:
        session.query(Events).filter_by(id=eventid).update({Events.is_ended : True, Events.end_time : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def active_events():
    try:
        return session.query(Events.id, Events.serverid, Events.name, Events.type).filter_by(is_started=True,is_ended=False).all()
    except Exception as e:
        session.rollback()
        raise e

def available_events():
    try:
         return session.query(Events.id, Events.serverid, Events.name, Events.type, Events.friendly_only).filter_by(is_started=False).all()
         
    except Exception as e:
        session.rollback()
        raise e


def participant_progress(eventid,discordid):
    try:
        return session.query(Event_info.starting_stat,Event_info.current_stat,Event_info.current_stat - Event_info.starting_stat,Event_info.last_updated).filter_by(id=eventid,discordid=discordid).first()
    except Exception as e:
        session.rollback()
        raise e

def event_info(eventid):
    try:
        return session.query(Events.serverid,Events.name,Events.type,Events.is_started,Events.is_ended,Events.start_time,Events.end_time,Events.friendly_only).filter_by(id=eventid).first()
    except Exception as e:
        session.rollback()
        raise e

def event_guild_only(eventid, boolean):
    try:
        session.query(Events).filter_by(id=eventid).update({Events.friendly_only : boolean})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def join_event(eventid,discordid):
    try:
        session.add(Event_info(id=eventid,discordid=discordid))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def get_participants(eventid):
    try:
        return session.query(Event_info.discordid,Event_info.starting_stat,Event_info.current_stat,Event_info.last_updated,Event_info.current_stat - Event_info.starting_stat).filter_by(id=eventid).all()
    except Exception as e:
        session.rollback()
        raise e

def update_start_stat(eventid,discordid,stat):
    try:
        session.query(Event_info).filter_by(id=eventid,discordid=discordid).update({Event_info.starting_stat : stat, Event_info.current_stat : stat})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

def update_stat(eventid,discordid,stat):
    try:
        session.query(Event_info).filter_by(id=eventid,discordid=discordid).update({Event_info.current_stat : stat, Event_info.last_updated : datetime.now(timezone.utc)})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e



if __name__ == "__main__":
    #print(is_ambassador(str(309115527962427402)))
    # print(ambassadors(424))
    # guild_leader_update(332314562575597579,False,0)
    # print(ambassadors(424))
    # print(conn_disc(587672))
    #print(in_fly(439777465494142996))
    # update_start_stat(2,332314562575597579,5)
    # update_stat(2,332314562575597579,852)
    print(type(get_participants(80)))



