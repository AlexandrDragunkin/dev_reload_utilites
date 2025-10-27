#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для установки пакета dev_reload_utilites с проверкой наличия зависимостей.
Этот скрипт устанавливает зависимости только в случае их отсутствия в целевой директории.
"""

import os
import sys
import subprocess
import importlib.util
import argparse
from pathlib import Path


def check_package_in_directory(package_name, target_dir):
    """
    Проверяет наличие пакета в указанной директории.
    
    Args:
        package_name (str): Имя пакета для проверки
        target_dir (str): Директория для проверки
        
    Returns:
        bool: True если пакет найден, False в противном случае
    """
    # Проверяем непосредственно в директории
    package_path = Path(target_dir) / package_name
    if package_path.exists():
        return True
    
    # Проверяем в поддиректориях
    for item in Path(target_dir).rglob(package_name):
        if item.is_dir():
            return True
    
    return False


def is_package_installed(package_name, target_dir):
    """
    Проверяет, установлен ли пакет в целевой директории.
    
    Args:
        package_name (str): Имя пакета для проверки
        target_dir (str): Директория для проверки
        
    Returns:
        bool: True если пакет установлен, False в противном случае
    """
    try:
        # Проверяем наличие пакета в файловой системе
        if check_package_in_directory(package_name, target_dir):
            return True
            
        # Проверяем, можно ли импортировать пакет
        spec = importlib.util.find_spec(package_name)
        if spec is not None:
            # Проверяем, что пакет находится в целевой директории
            if spec.origin and spec.origin.startswith(target_dir):
                return True
                
        return False
    except Exception:
        return False


def install_package_if_needed(package_name, target_dir, is_dependency=False):
    """
    Устанавливает пакет, если он не найден в целевой директории.
    
    Args:
        package_name (str): Имя пакета для установки
        target_dir (str): Целевая директория установки
        is_dependency (bool): Является ли пакет зависимостью
    """
    if is_package_installed(package_name, target_dir):
        print(f"Пакет {package_name} уже установлен в {target_dir}")
        return
    
    print(f"Установка пакета {package_name} в {target_dir}")
    
    # Формируем команду установки
    if is_dependency:
        # Для зависимостей устанавливаем без дополнительных зависимостей
        cmd = [sys.executable, "-m", "pip", "install", package_name, "--target", target_dir, "--no-deps"]
    else:
        # Для основного пакета устанавливаем без зависимостей, 
        # так как мы управляем ими отдельно
        cmd = [sys.executable, "-m", "pip", "install", 
               "git+https://github.com/AlexandrDragunkin/dev_reload_utilites", 
               "--target", target_dir, "--no-deps"]
    
    try:
        subprocess.check_call(cmd)
        print(f"Пакет {package_name} успешно установлен")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка установки пакета {package_name}: {e}")
        raise


def main():
    """Основная функция скрипта."""
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Установка пакета dev_reload_utilites с проверкой зависимостей")
    parser.add_argument("target_dir", nargs="?", default=r"c:\PKMUserData81\Proto",
                        help="Целевая директория для установки (по умолчанию: c:\\PKMUserData81\\Proto)")
    
    # Парсим аргументы
    args = parser.parse_args()
    target_dir = args.target_dir
    
    # Создаем директорию, если она не существует
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    
    # Зависимости пакета dev_reload_utilites
    dependencies = [
        "loguru"
    ]
    
    print(f"Проверка и установка зависимостей в {target_dir}")
    
    # Проверяем и устанавливаем зависимости
    for dep in dependencies:
        install_package_if_needed(dep, target_dir, is_dependency=True)
    
    # Устанавливаем основной пакет
    print("Установка основного пакета dev_reload_utilites")
    install_package_if_needed("dev_reload_utilites", target_dir, is_dependency=False)
    
    print("Установка завершена")


if __name__ == "__main__":
    main()