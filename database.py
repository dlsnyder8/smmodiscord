import os
from sys import stderr, exit
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, create_session, Session
from sqlalchemy.ext.automap import automap_base
import config
from datetime import datetime, timezone, date


# DATABASE_URL
# ----------
DATABASE_URL = config.DATABASE_URL

# create engine (db object basically)
engine = create_engine(DATABASE_URL)
# start automap and create session with automap
Base = automap_base()
Base.prepare(engine, reflect=True)

session = Session(engine)

Server = Base.classes.server
Plebs = Base.classes.plebs
Guild = Base.classes.guilds
Friendly = Base.classes.friendly
Tracking = Base.classes.tracking


def add_server(serverid, name):
    try:
        session.add(Server(serverid=serverid, full_name=name))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def disc_ids(discid):
    try:
        val = session.query(Plebs.smmoid, Plebs.verified).filter_by(
            discid=discid, verified=True).all()
        return val
    except Exception as e:
        session.rollback()
        raise e


def add_server_role(serverid, roleid):
    try:
        session.query(Server).filter_by(
            serverid=serverid).update({Server.pleb_role: roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def add_leader_role(serverid, roleid):
    try:
        session.query(Server).filter_by(serverid=serverid).update(
            {Server.leader_role: roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def add_ambassador_role(serverid, roleid):
    try:
        session.query(Server).filter_by(serverid=serverid).update(
            {Server.ambassador_role: roleid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def add_new_pleb(smmoid, discid, verification, verified=False, active=False):
    try:
        session.add(Plebs(smmoid=smmoid, discid=discid,
                    verification=verification, verified=verified, pleb_active=active))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def update_pleb(smmoid, discid, verification, verified=False, active=False):
    try:
        session.query(Plebs).filter_by(smmoid=smmoid).update({
            Plebs.discid: discid,
            Plebs.verification: verification,
            Plebs.verified: verified,
            Plebs.pleb_active: active})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def get_all_plebs():
    try:
        plebs = session.query(Plebs.discid, Plebs.smmoid).filter_by(
            verified=True).all()
        return plebs
    except Exception as e:
        raise e


def islinked(discid):
    out = session.query(Plebs.verified).filter_by(
        discid=str(discid), verified=True).first()
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
        session.query(Plebs).filter_by(
            smmoid=smmoid).update({Plebs.verified: verified})
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
        session.query(Plebs).filter_by(smmoid=smmoid).update(
            {Plebs.pleb_active: active})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def remove_user(smmoid):
    try:
        session.execute("DELETE FROM plebs WHERE smmoid=:param", {
                        "param": smmoid})
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
        x = session.query(Plebs.verification).filter_by(
            smmoid=smmoid, discid=discid).first()
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
    val = session.query(Server.pleb_role).filter(
        Server.serverid == serverid).first()
    if val is not None:
        return val[0]
    else:
        return None


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


def add_guild_person(discid, smmoid):
    try:
        session.add(Guild(discid=str(discid), smmoid=smmoid,
                    leader=False, ambassador=False, guildid=0))
    except Exception as e:
        session.rollback()
        raise e


def guild_leader_update(discid, bLeader, guildid, smmoid):
    try:
        session.query(Guild).filter_by(discid=str(discid)).update(
            {Guild.leader: bLeader, Guild.guildid: guildid, Guild.smmoid: smmoid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def guild_ambassador_update(discid, bAmbassador, guildid):
    try:
        session.query(Guild).filter_by(discid=str(discid)).update(
            {Guild.ambassador: bAmbassador, Guild.guildid: guildid})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def ret_guild_smmoid(discid):
    try:
        val = session.query(Guild.guildid, Guild.smmoid).filter_by(
            discid=str(discid)).first()
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
        return session.query(Guild.ambassador, Guild.guildid).filter_by(discid=str(discid)).first()

    except Exception as e:
        session.rollback()
        raise e


def ambassadors(guildid):
    try:
        return session.query(Guild.discid).filter_by(guildid=guildid, ambassador=True).all()
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
        val = session.query(Guild.discid, Guild.smmoid,
                            Guild.guildid).filter_by(leader=True).all()
        return val
    except Exception as e:
        session.rollback()
        raise e


def remove_guild_user(smmoid):
    try:
        session.execute("DELETE FROM guilds WHERE smmoid=:param", {
                        "param": smmoid})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e

################
# Fly Commands #
################
def fly_add(discid, smmoid, guildid=0):
    try:
        session.add(Friendly(discid=str(discid),
                    smmoid=smmoid, guildid=guildid))
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def fly_update(discid, smmoid, guildid=0):
    try:
        session.query(Friendly).filter_by(discid=str(discid)).update(
            {Guild.discid: discid,
             Guild.smmoid: smmoid,
             Guild.guildid: guildid}
        )
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def in_fly(discid):
    try:
        ret = session.query(Friendly.guildid).filter_by(
            discid=str(discid)).first()
        if ret is None:
            return None
        else:
            return ret != 0

    except Exception as e:
        session.rollback()
        raise e


def all_fly():
    try:
        return session.query(Friendly.discid, Friendly.smmoid, Friendly.guildid).all()

    except Exception as e:
        session.rollback()
        raise e


def fly_remove(discid):
    try:
        session.execute("DELETE FROM friendly WHERE discid=:param", {
                        "param": str(discid)})
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e


def tracking_add(smmoid,
                 steps: int,
                 quests: int,
                 npckills: int,
                 pvpkills: int,
                 eventskills: int,
                 rep: int, tasks: int,
                 bosskills: int,
                 markettrades: int,
                 bounties: int,
                 dailies: int,
                 chests: int):

    session.add(Tracking(smmoid=smmoid, timestamp=datetime.now(timezone.utc),
                steps=steps, quests=quests, npckills=npckills,
                pvpkills=pvpkills, eventskills=eventskills,
                reputation=rep, tasks=tasks, bosskills=bosskills,
                markettrades=markettrades, bounties=bounties,
                dailies=dailies, chests=chests))
    session.commit()

# Returns the most recent data put into the database
# Returns (timestamp,steps,quests,npc,pvp,skills,rep,tasks,boss,trades,bounties,dailies,chests)
def tracking_get_latest(smmoid):
    return session.query(Tracking.timestamp, Tracking.steps, Tracking.quests, Tracking.npckills, Tracking.pvpkills, Tracking.eventskills,
                  Tracking.reputation, Tracking.tasks, Tracking.bosskills, Tracking.markettrades, Tracking.bounties,
                  Tracking.dailies, Tracking.chests).filter_by(smmoid=smmoid).order_by(Tracking.timestamp.desc()).first()
   

# Return all data for a specific person
# Mostly to be used with tracking long term info
# Returns it with the oldest data first

def tracking_get_all(smmoid):
    return session.query(Tracking.timestamp, Tracking.steps, Tracking.quests, Tracking.npckills, Tracking.pvpkills, Tracking.eventskills,
                  Tracking.reputation, Tracking.tasks, Tracking.bosskills, Tracking.markettrades, Tracking.bounties,
                  Tracking.dailies, Tracking.chests).filter_by(smmoid=smmoid).order_by(Tracking.timestamp.asc()).all()

def tracking_get_last_day(smmoid):
    # If after noon, get all information from noon today onwards
    if datetime.now(timezone.utc).hour > 12:
        resultproxy = session.execute("SELECT * FROM tracking WHERE smmoid=:param AND tracking.timestamp > CURRENT_DATE + interval '12 hour' ORDER BY tracking.timestamp", {"param":smmoid})
    # If before noon, get all information from yesterday at noon until now
    else:
        resultproxy = session.execute("SELECT * FROM tracking WHERE smmoid=:param AND tracking.timestamp > CURRENT_DATE + interval '12 hour' - interval '1 day' ORDER BY tracking.timestamp", {"param":smmoid})

    # Convert each row to a dictionary and return list of dicts
    result = [dict(row) for row in resultproxy]
    return result


def tracking_test(smmoid):
    
    if datetime.now(timezone.utc).hour > 12:
        resultproxy = session.execute("SELECT * FROM tracking WHERE smmoid=:param AND tracking.timestamp > CURRENT_DATE + interval '12 hour' ORDER BY tracking.timestamp", {"param":smmoid})
    else:
        resultproxy = session.execute("SELECT * FROM tracking WHERE smmoid=:param AND tracking.timestamp > CURRENT_DATE + interval '12 hour' - interval '1 day' ORDER BY tracking.timestamp", {"param":smmoid})


    result = [dict(row) for row in resultproxy]
    return result


if __name__ == "__main__":
    # print(is_ambassador(str(309115527962427402)))
    # print(ambassadors(424))
    # guild_leader_update(332314562575597579,False,0)
    # print(ambassadors(424))
    # print(conn_disc(587672))

    #tracking_add(2,1,1,1,1,1,1,1,1,1,1,1,1)
    #tracking_add(2,2,2,2,2,2,2,2,2,2,2,2,3)
    #print(tracking_get_last_day(2))
    info = tracking_test(2)
    print(info[0])
    #print(datetime.date(datetime.now(timezone.utc)))