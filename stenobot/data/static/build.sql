-- From Solaris: https://github.com/parafoxia/Solaris

CREATE TABLE IF NOT EXISTS bot (
    Key text PRIMARY KEY,
    Value text
);

INSERT OR IGNORE INTO bot VALUES ("last commit", CURRENT_TIMESTAMP);

CREATE TABLE IF NOT EXISTS errors (
    Ref text PRIMARY KEY,
    ErrorTime text DEFAULT CURRENT_TIMESTAMP,
    Cause text,
    Traceback text
);

CREATE TABLE IF NOT EXISTS guild_config (
    guildId             STRING (18) PRIMARY KEY,
    name                STRING      UNIQUE
                                    NOT NULL,
    setTime             DATETIME    NOT NULL,
    setByUserId         STRING      NOT NULL,
    commandPrefix       STRING      NOT NULL,
    notificationChannel STRING,
    defaultLogChannelId INTEGER,
    logChannelId        INTEGER,
    runFts              STRING,
    defaultAdminRoleId  INTEGER,hg
    adminRoleId         INTEGER
);

CREATE TABLE IF NOT EXISTS entrants (
	GuildID integer,
	UserID integer,
	Timeout text,
	PRIMARY KEY (GuildID, UserID)
);

CREATE TABLE IF NOT EXISTS accepted (
	GuildID integer,
	UserID integer,
	PRIMARY KEY (GuildID, UserID)
);

-- warn

CREATE TABLE IF NOT EXISTS warn (
	GuildID integer PRIMARY KEY,
	WarnRoleID integer,
	MaxPoints integer,
	MaxStrikes interger
);

CREATE TABLE IF NOT EXISTS warntypes (
	GuildID integer,
	WarnType text,
	Points integer,
	PRIMARY KEY (GuildID, WarnType)
);

CREATE TABLE IF NOT EXISTS warns (
	WarnID text PRIMARY KEY,
	GuildID integer,
	UserID integer,
	ModID integer,
	WarnTime text DEFAULT CURRENT_TIMESTAMP,
	WarnType text,
	Comment text
);

CREATE TABLE IF NOT EXISTS notes (
    noteId   INTEGER  PRIMARY KEY AUTOINCREMENT,
    time     DATETIME,
    userId   INTEGER,
    notebook STRING,
    text     STRING
);


CREATE TABLE IF NOT EXISTS members (
    guildId       INTEGER,
    userId        INTEGER,
    open_notebook STRING,
    PRIMARY KEY (guildId, userId)
);


