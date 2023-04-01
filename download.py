import asyncio
import os
from urllib.parse import urljoin


import aiohttp
from bs4 import BeautifulSoup


URL = "https://gitea.radium.group/radium/project-configuration"


async def get_link_to_download(body):
    soup = BeautifulSoup(body, 'html.parser')
    href = soup.find('a', {"download": True})
    if href:
        link_to_download = urljoin(URL, href.get('href'))
        return link_to_download 


async def request(url: str, client: aiohttp.ClientSession):
    async with client.get(url, ssl=True) as response:
        response.raise_for_status()
        return await response.text()


async def download(
        item: BeautifulSoup, directory: str, client: aiohttp.ClientSession):

    """
    Функция-корутина - загрузчик объекта репозитория. 

    Принимает на вход:
        item - объект BeautifulSoup,требующий скачивания;
        path - директория сохранения;
        client - объект сессии клиента;
    
    Алгоритм выполнения:
        1. Парсинг raw ссылки к исходнику объекта
            1.1. В случае, если объект является директорией, 
            то рекурсивным подходом создается внутрий цикл корутинных задач загрузки объектов директории;
        2. Загрузка объекта;
        3. Запись объекта в файл;
    """
    link = urljoin(URL, item.find('a').get('href'))
    source_content = await request(link, client)
    raw_link = await get_link_to_download(source_content)
    if not raw_link:
        soup = BeautifulSoup(source_content, 'html.parser')
        items = soup.find_all('tr', class_="ready entry")
        new_directory = os.path.join(directory, link.split('/')[-1])
        if not os.path.exists(new_directory):
            os.mkdir(new_directory)
        tasks = [asyncio.create_task(download(item, new_directory, client)) for item in items]
        await asyncio.gather(*tasks)
    else:
        filename = os.path.join(directory, raw_link.split('/')[-1])
        data = await request(raw_link, client)
        with open(filename, 'w') as f:
            f.write(data)


async def download_repo(directory: str):
    """
    Главная функция-корутина, определяющая объекты для загрузки на корневом этапе и формирующая цикл задач загрузки объектов
    """
    async with aiohttp.ClientSession() as client:
        content = await request(URL, client)
        soup = BeautifulSoup(content, 'html.parser')
        objects_to_download = soup.find_all('tr', class_="ready entry")
        await asyncio.gather(*[download(object_, directory, client) for object_ in objects_to_download])
