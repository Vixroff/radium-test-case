import asyncio
import hashlib
import os
import tempfile


import aiohttp


from download import download_repo


def get_all_files(directory):
    """Функция рекурсивно собирает пути файлов переданной директории и возвращает список """
    result = []
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)):
            result.append(os.path.join(directory, item))
        elif os.path.isdir(os.path.join(directory, item)):
            result.extend(get_all_files(os.path.join(directory, item)))
    return result


def get_file_hash(filepath):
    """Функция вычисляет хеш sha256 переданного файла"""
    hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(2048)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()


def calculate_hashes_files(files: list):
    """Функция вычисляет хеши переданных файлов в списке и возвращает словарь"""
    result = {}
    for file in files:
        filename = file.split('/')[-1]
        filehash = get_file_hash(file)
        result[filename] = filehash
    return result


def main():
    with tempfile.TemporaryDirectory() as tempdir:
        try:
            asyncio.run(download_repo(tempdir))
        except aiohttp.ClientResponseError as e:
            print(f'Connection is failed - status: {e.status}')
        else:
            files = get_all_files((tempdir))
            file_hashes = calculate_hashes_files(files)
            with open(os.path.join(os.getcwd(), 'hashes.txt'), 'w') as f:
                for key, value in file_hashes.items():
                    f.write(
                        f'Hash of file "{key}" is {value}\n'
                    )


if __name__ == "__main__":
    main()
