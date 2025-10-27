# -*- coding: utf-8 -*-
from __future__ import annotations
__author__ = 'Aleksandr Dragunkin --<alexandr69@gmail.com>'
__created__= '27.10.2025'
__version__ = '0.1.00'
# -------------------------------------------------------------------------------
# Name:        find_recent_py_files
# Purpose:     
# Copyright:   (c) GEOS 2012-2025 http://k3info.ru/
# Licence:     FREE
# ------------------------------------------------------------------------------

import os
import datetime
from typing import List, Tuple


def find_proto_path() -> str:
    """
    Найти путь к директории Proto относительно текущего файла.
    
    Returns:
        str: Путь к директории Proto.
    """
    # Получаем путь к текущему файлу
    cpath = os.path.dirname(os.path.abspath(__file__))
    
    # Разбиваем путь на компоненты
    plist = cpath.split(os.sep)
    
    # Приводим к нижнему регистру для поиска
    lower_plist = list(map(lambda s: s.lower(), plist))
    
    # Находим индекс 'proto' в пути
    try:
        index_proto = lower_plist.index('proto')
    except ValueError:
        # Если 'proto' не найден, возвращаем текущую директорию
        return "."
    
    # Формируем путь к директории Proto
    proto_list = plist[:index_proto + 1]
    
    # Корректно формируем абсолютный путь для Windows
    if len(proto_list) > 1 and ':' in proto_list[0]:
        # Если первый элемент содержит ':', это диск Windows
        proto_path = proto_list[0] + os.sep
        proto_path = os.path.join(proto_path, *proto_list[1:])
    else:
        # Для других случаев используем стандартное объединение
        proto_path = os.path.join(*proto_list)
    
    return proto_path


def find_recent_py_files(root_dir: str = None, minutes: int = 30) -> List[Tuple[str, datetime.datetime]]:
    """
    Поиск последних изменённых py-файлов за указанное количество минут.
    
    Args:
        root_dir (str): Корневая директория для поиска. По умолчанию директория Proto.
        minutes (int): Количество минут для поиска. По умолчанию 30.
        
    Returns:
        List[Tuple[str, datetime.datetime]]: Список кортежей с путями к файлам и временем их изменения.
    """
    # Если директория не указана, ищем директорию Proto
    if root_dir is None:
        root_dir = find_proto_path()
    
    # Проверяем, является ли путь абсолютным, если нет - преобразуем
    if not os.path.isabs(root_dir):
        root_dir = os.path.abspath(root_dir)
    
    # Вычисляем время, до которого нужно искать файлы
    time_threshold = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
    
    recent_files = []
    
    # Рекурсивно проходим по всем файлам в директории
    try:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                # Проверяем только .py файлы
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        # Получаем время последней модификации файла
                        mod_time = os.path.getmtime(file_path)
                        mod_datetime = datetime.datetime.fromtimestamp(mod_time)
                        
                        # Проверяем, был ли файл изменён в заданный период
                        if mod_datetime > time_threshold:
                            # Сохраняем относительный путь для удобства отображения
                            relative_path = os.path.relpath(file_path, root_dir)
                            recent_files.append((relative_path, mod_datetime))
                    except OSError as e:
                        # Пропускаем файлы, к которым нет доступа
                        print(f"Не удалось получить время модификации файла {file_path}: {e}")
                        continue
    except Exception as e:
        print(f"Ошибка при обходе директории {root_dir}: {e}")
        return []
    
    # Сортируем по времени модификации (новые первыми)
    recent_files.sort(key=lambda x: x[1], reverse=True)
    
    return recent_files


def get_import_names(root_dir: str = None, minutes: int = 30) -> Tuple[str, ...]:
    """
    Получить кортеж с именами модулей в формате, пригодном для импорта.
    
    Args:
        root_dir (str): Корневая директория для поиска. По умолчанию директория Proto.
        minutes (int): Количество минут для поиска. По умолчанию 30.
        
    Returns:
        Tuple[str, ...]: Кортеж с именами модулей, отсортированными по времени изменения.
    """
    # Если директория не указана, ищем директорию Proto
    if root_dir is None:
        root_dir = find_proto_path()
    
    # Проверяем, является ли путь абсолютным, если нет - преобразуем
    if not os.path.isabs(root_dir):
        root_dir = os.path.abspath(root_dir)
    
    # Получаем список последних изменённых файлов
    recent_files = find_recent_py_files(root_dir, minutes)
    
    # Формируем список имён модулей
    import_names = []
    for file_path, _ in recent_files:
        # Убираем расширение .py
        if file_path.endswith('.py'):
            module_path = file_path[:-3]
            # Заменяем разделители пути на точки
            module_name = module_path.replace(os.sep, '.')
            import_names.append(module_name)
    
    return tuple(import_names)


def print_recent_py_files(root_dir: str = None, minutes: int = 30) -> None:
    """
    Печать последних изменённых py-файлов за указанное количество минут.
    
    Args:
        root_dir (str): Корневая директория для поиска. По умолчанию директория Proto.
        minutes (int): Количество минут для поиска. По умолчанию 30.
    """
    # Если директория не указана, ищем директорию Proto
    if root_dir is None:
        root_dir = find_proto_path()
    
    # Проверяем, является ли путь абсолютным, если нет - преобразуем
    if not os.path.isabs(root_dir):
        root_dir = os.path.abspath(root_dir)
    
    recent_files = find_recent_py_files(root_dir, minutes)
    
    print(f"Поиск файлов в директории: {root_dir}")
    
    if not recent_files:
        print(f"Нет .py файлов, изменённых за последние {minutes} минут.")
        return
    
    print(f"Найдено {len(recent_files)} .py файлов, изменённых за последние {minutes} минут:")
    for file_path, mod_time in recent_files:
        print(f"  {mod_time.strftime('%Y-%m-%d %H:%M:%S')} - {file_path}")
    
    # Выводим имена модулей для импорта
    import_names = get_import_names(root_dir, minutes)
    print(f"\nИмена модулей для импорта: {import_names}")


# Пример использования
if __name__ == "__main__":
    # Поиск файлов в директории Proto за последние 30 минут
    print_recent_py_files(None, 30)    
    # import_names = get_import_names(minutes=30)
    # print(f"\nИмена модулей для импорта: {import_names}")