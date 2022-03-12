CREATE TABLE "server" (
  "serverid" bigint PRIMARY KEY,
  "full_name" varchar(256),
  "pleb_role" numeric DEFAULT null,
  "leader_role" numeric DEFAULT null,
  "ambassador_role" numeric DEFAULT null,
  "diamond_ping" boolean DEFAULT false,
  "diamond_role" numeric DEFAULT null,
  "diamond_channel" numeric DEFAULT null,
  "last_pinged" timestamp default null
);

CREATE TABLE "plebs" (
  "smmoid" int PRIMARY KEY,
  "discid" varchar(64),
  "verification" varchar(32),
  "verified" boolean DEFAULT false,
  "pleb_active" boolean DEFAULT false,
  "guild_ban" boolean default false
);

CREATE TABLE "guilds" (
  "discid" bigint PRIMARY KEY,
  "smmoid" int,
  "leader" boolean DEFAULT false,
  "ambassador" boolean DEFAULT false,
  "guildid" int
);

CREATE TABLE "friendly" (
  "discid" bigint PRIMARY KEY,
  "smmoid" int,
  "guildid" int
);

CREATE TABLE "events" (
  "id" SERIAL PRIMARY KEY,
  "serverid" numeric,
  "name" varchar(64),
  "type" varchar(16),
  "is_started" boolean DEFAULT false,
  "is_ended" boolean default false,
  "start_time" timestamp,
  "end_time" timestamp,
  "friendly_only" bool default true,
  "event_role" numeric
);


CREATE TABLE "event_info" (
  "serial" SERIAL PRIMARY KEY,
  "id" int,
  "discordid" bigint,
  "starting_stat" int,
  "current_stat" int,
  "last_updated" timestamp
);

CREATE TABLE "warinfo" (
  "discordid" bigint PRIMARY KEY,
  "smmoid" int,
  "guildid" int,
  "min_level" int default 200,
  "max_level" int default 10000,
  "gold_ping" bool default false,
  "gold_amount" numeric default 5000000,
  "last_pinged" timestamp default null
);

CREATE TABLE "smackback" (
  "id" SERIAL PRIMARY KEY,
  "tobesmacked" numeric,
  "guildmember" numeric,
  "completed_by" numeric default null,
  "posted" timestamp,
  "completed_at" timestamp default null,
  "completed" bool default false,
  "messageid" numeric

);

CREATE TABLE "drifters" {
  "id" SERIAL PRIMARY KEY,
  "discordid" numeric,
  "npc_yesterday" numeric,
  "npc_today" numeric,
  "step_yesterday" numeric,
  "step_today" numeric,
  "pvp_yesterday" numeric,
  "pvp_today" numeric,
  "update_yesterday" timestamp,
  "update_today" timestamp
}
