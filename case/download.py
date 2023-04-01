"""Модуль содержит асинхронные корутины."""
import asyncio
import os
from typing import Union
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

URL = 'https://gitea.radium.group/radium/project-configuration'


async def get_link_to_download(body: str) -> Union[str, None]:
    """Функция-корутина парсит загрузочную raw ссылку."""
    soup = BeautifulSoup(body, 'html.parser')
    href = soup.find('a', {'download': True})
    if href:
        return urljoin(URL, href.get('href'))


async def request(url: str, client: aiohttp.ClientSession) -> str:
    """Функция-корутина делает запрос к серверу."""
    async with client.get(url, ssl=True) as response:
        response.raise_for_status()
        return await response.text()


async def download(
    item: BeautifulSoup, folder: str, client: aiohttp.ClientSession,
) -> None:
    """Функция-корутина - загрузчик объекта репозитория.

    Принимает на вход:
        item - объект BeautifulSoup,требующий скачивания;
        path - директория сохранения;
        client - объект сессии клиента;

    Алгоритм выполнения:
        1. Парсинг raw ссылки к исходнику объекта
            1.1. В случае, если объект является директорией,
            то рекурсивным подходом создается внутрий цикл
            корутинных задач загрузки объектов директории;
        2. Загрузка объекта;
        3. Запись объекта в файл;
    """
    content = await request(
        urljoin(URL, item.find('a').get('href')),
        client,
    )
    raw_link = await get_link_to_download(content)
    if raw_link:
        data = await request(raw_link, client)
        with open(
            os.path.join(folder, raw_link.split('/')[-1]), 'w',
        ) as file:
            file.write(data)
    else:
        soup = BeautifulSoup(content, 'html.parser')
        await asyncio.gather(
            *[download(
                item,
                folder,
                client,
            ) for item in soup.find_all('tr', class_='ready entry')
            ],
        )


async def download_repo(folder: str) -> None:
    """Функция-корутина, скачивающая репозиторий."""
    async with aiohttp.ClientSession() as client:
        content = await request(URL, client)
        soup = BeautifulSoup(content, 'html.parser')
        items = soup.find_all('tr', class_='ready entry')
        await asyncio.gather(
            *[download(item, folder, client) for item in items],
        )
