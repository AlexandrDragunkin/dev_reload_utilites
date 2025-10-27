"""
dev_reload_utilites - Утилита для централизованного управления перезагрузкой модулей
в приложении K3-Mebel 8.1.
"""

__version__ = "0.1.0"
__author__ = "Aleksandr Dragunkin"

# Импортируем основные функции для удобного доступа
from .auto_reload_manager import (
    auto_reload_module,
    reload_module_with_dependencies,
    selective_reload,
    SetVar,
    Title,
    WString
)

from .find_recent_py_files import (
    find_recent_py_files,
    get_import_names
)

# Определяем, что будет доступно при импорте *
__all__ = [
    "auto_reload_module",
    "reload_module_with_dependencies",
    "selective_reload",
    "SetVar",
    "Title",
    "WString",
    "find_recent_py_files",
    "get_import_names"
]