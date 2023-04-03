import os
import pytest
import hashlib

from tests.test_download import mock_aioresponses
from case.main import (
    get_all_files,
    get_file_hash,
    calculate_hashes_files,
    main,
)


def test_get_all_files(tmpdir):
    assert get_all_files(tmpdir) == []
    for i in range(2):
        with open(os.path.join(tmpdir, f'{i}.txt'), 'w') as f:
            f.write(f'{i}')
    assert get_all_files(tmpdir) == [f'{tmpdir}/0.txt', f'{tmpdir}/1.txt']


def test_get_file_hash():
    file = 'tests/fixtures/files/all.toml'
    with open(file, 'rb') as f:
        content = f.read()
        hash_ = hashlib.sha256(content)
    assert get_file_hash(file) == hash_.hexdigest()


def test_calculate_hashes_files(tmpdir):
    assert calculate_hashes_files([]) == {}
    files = ['tests/fixtures/files/all.toml', 'tests/fixtures/files/flake8.toml']
    expected = {
        'all.toml': get_file_hash(files[0]),
        'flake8.toml': get_file_hash(files[1]),
    }
    assert calculate_hashes_files(files) == expected


@pytest.fixture(autouse=True)
def patch_os_getcwd(tmpdir, monkeypatch):
    def mock_getcwd():
        return tmpdir
    monkeypatch.setattr(os, 'getcwd', mock_getcwd)


def test_main(tmpdir, mock_aioresponses):
    main()
    assert os.listdir(tmpdir) == ['hashes.txt']
