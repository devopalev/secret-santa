import json
import io
import uuid
from abc import ABC, abstractmethod

import asyncpg

from src import db
from src.core import config
from src.domain.model import GameSanta, Player


class AbstractRepository(ABC):
    @abstractmethod
    async def get(self, game_uuid: str) -> GameSanta:
        ...

    @abstractmethod
    async def get_list(self, telegram_id: int) -> list[GameSanta]:
        ...

    @abstractmethod
    async def save(self, game: GameSanta) -> GameSanta:
        ...

    @abstractmethod
    async def delete(self, game: GameSanta):
        ...

    @abstractmethod
    async def get_players_csv(self, game_uuid: str) -> io.BytesIO:
        ...


class Repository(AbstractRepository):
    @staticmethod
    def _build_game(raw_game: asyncpg.Record) -> GameSanta:
        dict_game = dict(**raw_game)
        # json -> array[dict]
        dict_game["players"] = json.loads(dict_game["players"])

        if dict_game["players"]:
            players = {p["id"]: Player(**p) for p in dict_game["players"]}
            for player in players.values():
                player.recipient = players.get(player.recipient_id) if player.recipient_id else None
            dict_game["players"] = list(players.values())

        return GameSanta(**dict_game)

    async def get(self, game_uuid: str) -> GameSanta:
        conn = await db.connection()

        sql = """
            select 
                games.*, 
                COALESCE(json_agg(pl.*) FILTER (WHERE pl.id IS NOT NULL), '[]') as players  -- COALESCE filtered [null]
            from games 
            left join players as pl
                on games.uuid = pl.game_uuid 
            where games.uuid = $1
            group by games.uuid;
        """

        raw_game: asyncpg.Record = await conn.fetchrow(sql, game_uuid)

        if raw_game:
            return self._build_game(raw_game)

    async def get_list(self, telegram_id: int) -> list[GameSanta]:
        conn = await db.connection()

        sql = """
            select 
                games.*, 
                COALESCE(json_agg(pl.*) FILTER (WHERE pl.id IS NOT NULL), '[]') as players  -- COALESCE filtered [null]
            from games 
            left join players as pl
                on games.uuid = pl.game_uuid 
            where games.initiator_id = $1 or pl.telegram_id = $1
            group by games.uuid;
            """

        raw_games: asyncpg.Record = await conn.fetch(sql, telegram_id)
        return [self._build_game(record) for record in raw_games or []]

    async def save(self, game: GameSanta) -> GameSanta:
        conn = await db.connection()

        # Change
        if game.uuid:
            # changed fields
            if game.meta.changed_fields:
                data = [getattr(game, f) for f in game.meta.changed_fields]
                data.append(game.uuid)
                uuid_index = len(data)
                sql_fields = ",".join(f"{f}=${i}" for i, f in enumerate(game.meta.changed_fields, 1))
                sql = f"UPDATE games SET {sql_fields} WHERE uuid=${uuid_index};"
                await conn.execute(sql, *data)
            # joined new players
            if game.meta.new_players:
                data = [(p.telegram_id, p.fullname, p.username, p.game_uuid) for p in game.meta.new_players]
                sql = "INSERT INTO players (telegram_id, fullname, username, game_uuid) VALUES ($1, $2, $3, $4);"
                await conn.executemany(sql, data)
            # finish game, shuffled players
            if game.meta.shuffled_players:
                data = [(p.id, p.recipient.id) for p in game.players]
                sql = "UPDATE players SET recipient_id=$2 where id=$1;"
                await conn.executemany(sql, data)
        # Create
        else:
            data = [getattr(game, f) for f in game.meta.changed_fields]
            sql_fields = ",".join(game.meta.changed_fields)
            sql_values = ",".join(f"${i}" for i in range(1, len(game.meta.changed_fields)+1))
            sql = f"INSERT INTO games ({sql_fields}) VALUES ({sql_values}) RETURNING uuid;"
            result: asyncpg.Record = await conn.fetchrow(sql, *data)
            game.uuid = str(result[0])

        return game

    async def delete(self, game: GameSanta):
        conn = await db.connection()
        sql = "delete from games where uuid=$1"
        await conn.execute(sql, game.uuid)

    async def get_players_csv(self, game_uuid: str) -> io.BytesIO:
        conn = await db.connection()
        sql = "select * from players where game_uuid=$1"
        result = await conn.fetch(sql, game_uuid)
        if result:
            data = (config.CSV_SPLITTER.join(result[0].keys())+"\n").encode()

            for row in result:
                data += (config.CSV_SPLITTER.join(map(str, row))+"\n").encode()
            return io.BytesIO(data)


class RepositoryMemory(AbstractRepository):
    def __init__(self):
        self.storage: dict[str, GameSanta] = {}

    async def get(self, game_uuid: str) -> GameSanta:
        return self.storage.get(game_uuid, None)

    async def get_list(self, telegram_id: int) -> list[GameSanta]:
        return [g for g in self.storage.values() if g.initiator_id == telegram_id or g.check_member(telegram_id)]

    async def save(self, game: GameSanta) -> GameSanta:
        if not game.uuid:
            game.uuid = uuid.uuid4()
        self.storage[game.uuid] = game

    async def delete(self, game: GameSanta):
        self.storage.pop(game.uuid, None)

    async def get_players_csv(self, game_uuid: str) -> io.BytesIO:
        game = self.storage.get(game_uuid, None)

        if game:
            columns = ['id', 'telegram_id', 'fullname', 'username', 'recipient_id', 'game_uuid']
            data = config.CSV_SPLITTER.join(columns).encode()

            for player in game.players:
                values = [str(getattr(player, k)) for k in columns]
                data += config.CSV_SPLITTER.join(values).encode()
            return io.BytesIO(data)