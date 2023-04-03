"""Исполнительный модуль."""
import asyncio
import hashlib
import os
import tempfile

import aiohttp

from case.download import download_repo


def get_all_files(directory: str) -> list:
    """Функция собирает файлы c абсолютным путем."""
    files = []
    for file_item in os.listdir(directory):
        files.append(os.path.join(directory, file_item))
    return files


def get_file_hash(filepath: str) -> dict:
    """Функция вычисляет хеш sha256 переданного файла."""
    hash_ = hashlib.sha256()
    with open(filepath, 'rb') as fl:
        while True:
            file_content = fl.read()
            if not file_content:
                break
            hash_.update(file_content)
    return hash_.hexdigest()


def calculate_hashes_files(files: list) -> dict:
    """Функция вычисляет хеш суммы файлов."""
    file_hashes = {}
    for file_item in files:
        filename = file_item.split('/')[-1]
        filehash = get_file_hash(file_item)
        file_hashes[filename] = filehash
    return file_hashes


def main() -> None:
    """Исполнительная функция.

    Выполняет асинхронный цикл загрузки файлов и высчитывает хеш суммы
    """
    with tempfile.TemporaryDirectory() as tempdir:
        try:
            asyncio.run(download_repo(tempdir))
        except aiohttp.ClientResponseError as err:
            raise ConnectionError(err)
        else:
            file_hashes = calculate_hashes_files(get_all_files((tempdir)))
            with open(os.path.join(os.getcwd(), 'hashes.txt'), 'w') as fl:
                for file_item, file_hash in file_hashes.items():
                    fl.write(
                        'Hash of file "{0}" is {1}\n'.format(
                            file_item, file_hash,
                        ),
                    )


if __name__ == '__main__':
    main()
