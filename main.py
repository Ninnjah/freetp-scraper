import asyncio
import logging
import re
from os import environ
from typing import Optional, Iterable, List

from dotenv import load_dotenv
if __name__ == "__main__":
    load_dotenv(".env")

from httpx import AsyncClient, ConnectTimeout, ConnectError, ReadTimeout, Response

from sqlalchemy import bindparam
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from torrentool.api import Torrent
from torrentool.bencode import Bencode

from models.file import File

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.ERROR)


async def request(client: AsyncClient, url: str, timeout: int = 5, attempts: int = 5) -> Optional[Response]:
    for _ in range(attempts):
        try:
            try:
                logger.debug(f"client.get({url})")
                return await client.get(url)
            except (ConnectTimeout, ConnectError):
                return

        except ReadTimeout:
            logger.warning(f"ReadTimeout on {url}. Waiting of {timeout} seconds")
            await asyncio.sleep(timeout)
            continue


async def create_engine(db_url: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(db_url)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    return async_session


async def get_file_info(r: Response) -> Optional[File]:
    game_id = int(r.url.params.get("id"))
    name_re = re.compile(r"\"\s*(.+?)\s*\"")

    name = re.search(name_re, r.headers.get("content-disposition"))
    if not name:
        logger.info(f"{game_id} - NOT FOUND")
        return None
    name = name.group(1)
    name = re.sub(r"\[FreeTP\.Org\]", "", name)

    ext = name.split(".")[-1]
    if not ext:
        return None

    if ext == "torrent":
        torrent = Torrent(Bencode.decode(r.content, byte_keys={'pieces'}))
        size = torrent.total_size
    else:
        try:
            size = int(r.headers.get("content-length"))
        except (ValueError, TypeError):
            size = None

    r = File(
        id=game_id,
        name=name,
        ext=ext,
        url=f"https://freetp.org/engine/download.php?id={game_id}",
        size=size
    )
    logger.info(f"{game_id} - DOWNLOADED | {r}")
    return r


async def download_file(game_id: int) -> Optional[File]:
    logger.info(f"Start to download {game_id}")
    file_url = f"https://freetp.org/engine/download.php?id={game_id}"

    async with AsyncClient() as client:
        r = await request(client, file_url)
    if not r.headers.get("content-type") == "application/force-download":
        return

    file = await get_file_info(r)
    logger.info(f"{game_id} - DOWNLOADED | {file}")
    return file


async def download_bunch(game_ids: Iterable[int]) -> List[File]:
    file_url = ["https://freetp.org/engine/download.php?id={game_id}".format(game_id=x) for x in game_ids]

    async with AsyncClient() as client:
        r = await asyncio.gather(*[request(client, url) for url in file_url])

    files = [
        await get_file_info(file)
        for file in r
        if file.headers.get("content-type") == "application/force-download"
    ]
    return [x for x in files if x]


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    db_session = await create_engine(environ.get("DATABASE_URL"))

    logger.info("Creating tasks")

    chunk = 10
    for x in range(1, 10000, chunk):
        files = await download_bunch(range(x, x + chunk))

        async with db_session() as session:
            async with session.begin():
                file_table = File.__table__
                stmt = (
                    insert(file_table)
                    .values(
                        id=bindparam("id"),
                        name=bindparam("name"),
                        ext=bindparam("ext"),
                        url=bindparam("url"),
                        size=bindparam("size"),
                    )
                    .on_conflict_do_update(
                        constraint=file_table.primary_key,
                        set_=dict(
                            name=bindparam("name"),
                            ext=bindparam("ext"),
                            url=bindparam("url"),
                            size=bindparam("size"),
                        )
                    )
                )
                await session.execute(
                    stmt, [
                        {"id": file.id, "name": file.name, "ext": file.ext, "url": file.url, "size": file.size}
                        for file in files
                    ]
                )
                await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
