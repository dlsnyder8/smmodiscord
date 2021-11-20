CREATE TABLE "server" (
  "serverid" int PRIMARY KEY,
  "full_name" varchar(256),
  "pleb_role" numeric DEFAULT null,
  "leader_role" numeric DEFAULT null,
  "ambassador_role" numeric DEFAULT null
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
)
};

CREATE TABLE "tracking" (
  "id" SERIAL PRIMARY KEY,
  "smmoid" int,
  "timestamp" datetime,
  "steps" int,
  "quests" int,
  "npckills" int,
  "pvpkills" int,
  "eventskills" int,
  "reputation" int,
  "tasks" int,
  "bosskills" int,
  "markettrades" int,
  "bounties" int,
  "dailies" int,
  "chests" int
);