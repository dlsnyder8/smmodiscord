CREATE TABLE "server" (
  "serverid" int PRIMARY KEY,
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
  "pleb_active" boolean DEFAULT false
);

CREATE TABLE "guilds" (
  "discid" varchar(64) PRIMARY KEY,
  "smmoid" int,
  "leader" boolean DEFAULT false,
  "ambassador" boolean DEFAULT false,
  "guildid" int
);

CREATE TABLE "friendly" (
  "discid" varchar(64) PRIMARY KEY,
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
  "friendly_only" bool default true
  "event_role" numeric
);


CREATE TABLE "event_info" (
  "serial" SERIAL PRIMARY KEY,
  "id" int,
  "discordid" numeric,
  "starting_stat" int,
  "current_stat" int,
  "last_updated" timestamp
);

CREATE TABLE "warinfo" (
  "discordid" numeric PRIMARY KEY,
  "smmoid" int,
  "guildid" int,
  "min_level" int default 200,
  "max_level" int default 10000,
  "gold_ping" bool default false,
  "gold_amount" numeric default 5000000,
  "last_pinged" timestamp default null
);

