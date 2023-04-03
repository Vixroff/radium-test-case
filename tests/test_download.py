import asyncio
import os
from urllib.parse import urljoin

import aiohttp
import pytest
from aioresponses import aioresponses
from bs4 import BeautifulSoup

from case.download import (
    URL,
    get_link_to_download,
    request,
    download,
    download_repo,
)


@pytest.mark.parametrize(
    "response, expected",
    [
        ('<a download href=\'/what/we/need\'><a>', 'https://gitea.radium.group/what/we/need'),
        ('<tr class=\'ready entry\'><a href=\'lol\'><a><tr>', None),
        ('<a>download<a>', None),
    ]
)
@pytest.mark.asyncio()
async def test_get_link_to_download(response, expected):
    assert await get_link_to_download(response) == expected


@pytest.fixture(scope="module")
def mock_aioresponses():
    """Создает фейковые ответы по необходимым маршрутам."""
    with aioresponses() as mock:
        mock.get(
            URL,
            status=200,
            body="""
            <tr class="ready entry"><a href="/file.txt"></a></tr>
            <tr class="ready entry"><a href="/folder"></a></tr>
            """,
        )
        mock.get(
            urljoin(URL, '/file.txt'),
            status=200,
            body='<a download href="/raw/file.txt"><a/>',
        )
        mock.get(
            urljoin(URL, '/raw/file.txt'),
            status=200,
            body='this is test file',
        )
        mock.get(
            urljoin(URL, '/folder'),
            status=200,
            body='<a download href="/raw/folder/ffile.txt"><a/>',
        )
        mock.get(
            urljoin(URL, '/raw/folder/ffile.txt'),
            status=200,
            body='this is test folder file'
        )
        yield mock


@pytest.mark.asyncio()
async def test_request(mock_aioresponses):
    async with aiohttp.ClientSession() as client:
        data = await request(URL, client)
        assert data == """
            <tr class="ready entry"><a href="/file.txt"></a></tr>
            <tr class="ready entry"><a href="/folder"></a></tr>
            """


@pytest.mark.asyncio()
async def test_download_file(tmpdir, mock_aioresponses):
    async with aiohttp.ClientSession() as client:
        soup = BeautifulSoup(
            '<tr class="ready entry"><a href="/file.txt"></a></tr>',
            'html.parser',
        )
        await download(soup, tmpdir, client)
        assert os.listdir(tmpdir) == ['file.txt']
        with open(os.path.join(tmpdir, 'file.txt')) as f:
            actual = f.read()
        assert actual == 'this is test file'


@pytest.mark.asyncio()
async def test_download_folder(tmpdir, mock_aioresponses):
    async with aiohttp.ClientSession() as client:
        soup = BeautifulSoup(
            '<tr class="ready entry"><a href="/folder"></a></tr>',
            'html.parser',
        )
        await download(soup, tmpdir, client)
        assert os.listdir(tmpdir) == ['ffile.txt']
        with open(os.path.join(tmpdir, 'ffile.txt')) as f:
            actual = f.read()
        assert actual == 'this is test folder file'


# @pytest.mark.asyncio()
# async def test_download_repo(tmpdir, mock_aioresponses):
#     await download_repo(tmpdir)
#     assert len(os.listdir(tmpdir)) == 2
#     assert os.listdir(tmpdir) == ['file.txt', 'ffile.txt']
