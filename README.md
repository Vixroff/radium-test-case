[![Test Coverage](https://api.codeclimate.com/v1/badges/b5519cc19f3aad92c445/test_coverage)](https://codeclimate.com/github/Vixroff/radium-test-case/test_coverage)

[![lints-and-tests](https://github.com/Vixroff/radium-test-case/actions/workflows/code_check.yaml/badge.svg)](https://github.com/Vixroff/radium-test-case/actions/workflows/code_check.yaml)
# Тестовое задание компании "Радиум" #

## Требования ##

- Напишите скрипт, асинхронно, в 3 одновременных задачи, скачивающий содержимое HEAD репозитория https://gitea.radium.group/radium/project-configuration во временную папку.

- После выполнения всех асинхронных задач скрипт должен посчитать sha256 хэши от каждого файла.

- Код должен проходить без замечаний проверку линтером wemake-python-styleguide. Конфигурация nitpick - https://gitea.radium.group/radium/project-configuration

- Обязательно 100% покрытие тестами


## Запуск ##

Для запуска выполнения необходимо иметь установленными:
 - Python 3.10
 - Poetry 

Далее следует порядок действий:

1. Клонируйте репозиторий
2. Установите виртуальное окружение и зависимости 
    `poetry install`
3. Запустите скрипт
    `make run`

Итогом работы станет созданный в директории запуска файл "hashes.txt", в котором будут определенны хеш дайджесты файлов.
