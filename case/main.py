"""Исполнительный модуль."""
import asyncio
import hashlib
import os
import tempfile

import aiohttp

from case.download import download_repo


def get_all_files(directory: str) -> list:
    """Функция собирает файлы c абсолютным путем."""
    result = []
    for item in os.listdir(directory):
        result.append(os.path.join(directory, item))
    return result


def get_file_hash(filepath: str) -> dict:
    """Функция вычисляет хеш sha256 переданного файла."""
    hash_ = hashlib.sha256()
    with open(filepath, 'rb') as fl:
        while True:
            data = fl.read()
            if not data:
                break
            hash_.update(data)
    return hash_.hexdigest()


def calculate_hashes_files(files: list) -> dict:
    """Функция вычисляет хеш суммы файлов."""
    result = {}
    for file in files:
        filename = file.split('/')[-1]
        filehash = get_file_hash(file)
        result[filename] = filehash
    return result


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
                for key, value in file_hashes.items():
                    fl.write(
                        'Hash of file "{0}" is {1}\n'.format(
                            key, value,
                        ),
                    )


if __name__ == '__main__':
    main()
