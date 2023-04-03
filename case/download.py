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
    repo_item: BeautifulSoup, folder: str, client: aiohttp.ClientSession,
) -> None:
    """Функция-корутина - загрузчик объекта репозитория.

    Принимает на вход:
        repo_item - объект BeautifulSoup,требующий скачивания;
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
    item_content = await request(
        urljoin(URL, repo_item.find('a').get('href')),
        client,
    )
    raw_link = await get_link_to_download(item_content)
    if raw_link:
        raw_content = await request(raw_link, client)
        with open(
            os.path.join(folder, raw_link.split('/')[-1]), 'w',
        ) as fl:
            fl.write(raw_content)
    else:
        soup = BeautifulSoup(item_content, 'html.parser')
        await asyncio.gather(
            *[download(
                repo_item,
                folder,
                client,
            ) for repo_item in soup.find_all('tr', class_='ready entry')
            ],
        )


async def download_repo(folder: str) -> None:
    """Функция-корутина, скачивающая репозиторий."""
    async with aiohttp.ClientSession() as client:
        repo_content = await request(URL, client)
        soup = BeautifulSoup(repo_content, 'html.parser')
        repo_items = soup.find_all('tr', class_='ready entry')
        await asyncio.gather(
            *[download(repo_item, folder, client) for repo_item in repo_items],
        )
