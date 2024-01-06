"""
init_tables
"""

from yoyo import step

__depends__ = {}


create = """
CREATE TABLE games (
    uuid UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    state SMALLINT NOT NULL,
    initiator_id BIGINT NOT NULL,
    initiator_fullname VARCHAR(4096) NOT NULL,  -- telegram size limit 
    title VARCHAR(4096) NOT NULL,  -- telegram size limit 
    description VARCHAR(4096) NOT NULL,  -- telegram size limit 
    date_finish DATE NOT NULL
);
CREATE TABLE players (
    id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    telegram_id BIGINT NOT NULL,
    fullname VARCHAR(130) NOT NULL, -- telegram size limit 
    username VARCHAR(32) NULL,
    recipient_id INTEGER REFERENCES players (id),
    game_uuid UUID NOT NULL REFERENCES games (uuid) ON DELETE CASCADE
); 
"""
delete = "DROP TABLE IF EXISTS games, players"

steps = [step(create, delete)]
