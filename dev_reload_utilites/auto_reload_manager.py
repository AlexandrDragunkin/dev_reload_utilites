# -*- coding: utf-8 -*-
from __future__ import annotations


__author__ = 'Aleksandr Dragunkin --<alexandr69@gmail.com>'
__created__= '27.10.2025'
__version__ = '0.1.00'
# -------------------------------------------------------------------------------
# Name:        auto_reload_manager
# Purpose:     Централизованный механизм перезагрузки
#              отслеживает зависимости и автоматически перезагружает все связанные модули.
# Copyright:   (c) GEOS 2012-2025 http://k3info.ru/
# Licence:     FREE
# ------------------------------------------------------------------------------

"""
Модуль для централизованного управления перезагрузкой модулей.

Этот модуль предоставляет функции для автоматической перезагрузки модулей Python
и их зависимостей. Он отслеживает зависимости между модулями и обеспечивает
целостную перезагрузку всех связанных компонентов.

Важно: Этот модуль предназначен для работы внутри закрытого скомпилированного
пакета k3, который является частью приложения mebel.exe. Приложение mebel.exe
является самодостаточным интерпретатором Python 3.7 32bit.

Основные функции:
- auto_reload_module: Перезагрузка модуля и его зависимостей
- reload_module_with_dependencies: Перезагрузка модуля и зависимых от него модулей
- selective_reload: Перезагрузка модулей по префиксу имени

Классы для работы с диалогами:
- SetVar: Основной класс для создания диалоговых окон
- Title: Титульная часть диалога
- WString: Виджет для ввода строк
"""

from itertools import chain
import os
import pickle
import sys
import importlib

import k3 # type: ignore
from loguru import logger
from dev_reload_utilites.find_recent_py_files import get_import_names



class key:
    """Ключи к3"""
    left = k3.k_left
    right = k3.k_right
    center = k3.k_center
    auto = k3.k_auto
    size = k3.k_size
    done = k3.k_done
    lst = k3.k_list
    listonly = k3.k_listonly
    current = k3.k_current


class _Children:
    """Класс для наследования.
    Реализует атрибут children у наследников.

    При присвоении атрибута children удаляет из последовательностей _children None
    """

    def __init__(self):
        self._children = []

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, items):
        self._children.extend(chain(*items))
        self._children = tuple(child for child in self._children if child is not None)

    def __iter__(self):
        return iter(self._children)


class Title(_Children):
    """Титульная часть диалога
    ____________________________


    Именованные аргументы:

     - title - <str> заголовок окна
     - picfile - <str> Путь к файлу рисунка
     - pos - <key.left,key.right,key.center> вариант позиционирования текста по умолчанию слева.

    Далее последовательность строк подсказки

    t = Title('Ввод параметров', 'Параметры:', pos=key.left)
    print(t.children)
    t = Title('Ввод параметров', 'Параметры:')
    print(t.children)
    t = Title('Ввод параметров', 'Параметры:', 'Ещё какая то строка',
                picfile=r'c:\PKM74\Data\PKM\Pictures\1 вариант.jpg',
                pos=key.right)
    print(t.children)
    for e in t:
        print(e)

    >>>('Ввод параметров', 'Параметры:', <Ключ: done(17002)>)
       ('Ввод параметров', 'Параметры:', <Ключ: done(17002)>)
       ('Ввод параметров', 'c:\\PKM74\\Data\\PKM\\Pictures\\1 вариант.jpg', 'Параметры:', 'Ещё какая то строка', <Ключ: done(17002)>)
       Ввод параметров
       c:\PKM74\Data\PKM\Pictures\1 вариант.jpg
       Параметры:
       Ещё какая то строка
       <Ключ: done(17002)>

    """

    def __init__(self, title, *w,
                 picfile="",
                 pos=None):

        super(Title, self).__init__()

        if isinstance(pos, k3.Keyword):
            if len(w):
                tuple(chain((pos, ), (w, )))

        self.children = (title, picfile, ), w, (key.done, )


class DialogWidget(_Children):

    def __init__(self):
        super(DialogWidget, self).__init__()
        self._value = k3.Var()

    @property
    def value(self):
        return self._value


class WString(DialogWidget):
    def __init__(self, prompt, *v, defval=None, size=key.auto, lst=None):

        super(WString, self).__init__()
        self._size = size
        self.default = defval

        if v:
            if lst is None:
                self._children = (k3.k_string, self.size,
                                  k3.k_default, self.default, key.lst, v, k3.k_done,
                                  prompt, self._value,
                                  )
            else:
                i_current = v.index(lst)
                if i_current:
                    v = list(v)
                    v.insert(i_current, key.current)
                self._children = (k3.k_string, self.size,
                                  key.listonly, v, k3.k_done,
                                  prompt, self._value,
                                  )

        else:
            self._children = (k3.k_string, self.size,
                              k3.k_default, self.default,
                              prompt, self._value,
                              )

    @property
    def size(self):
        if isinstance(self._size, (int, float)):
            return (key.size, self._size)
        else:
            if isinstance(self._size, k3.Keyword):
                return self._size
            else:
                if self._size > 120:
                    self._size = 120
                elif self._size <1:
                    self._size = 1
            return self._size

    @property
    def value(self):
        return self._value.value


class SetVar(_Children):
    """Ввод параметров в диалоговом окне
    _____________________________________

    example:

    >>>
       dlg = SetVar()
       dlg.promt = Title('Введите парметры', 'Параметры:')
       dlg.widgets.extend([
           WDigit('Введите число', defval=100),
           WDigit('Выберите число', 1, 2, 3, 4, 5, defval=100),
           WDigit('Выберите число', 100, 200, 300, 400, 500, lst=300),
           WBool('Риторический вопрос', defval=True),
           WString('Строку введите пожлста', defval='fff'),
           WString('Выберите строку пожалуйста', 'раз', 'два', 'три', defval='fff'),
           WString('Выберите строку пожалуйста', 'раз', 'два', 'три', lst='два'),
           WGuidesLismat(f'Выберите направляющую',prop_ ='guide',id_ = 10622,defvalue = 21050)
       ])
       res = dlg.view()
       for w in dlg.widgets:
           print(w.value)

    """

    def __init__(self):
        super(SetVar, self).__init__()
        self.promt = None
        self.widgets = []
        pass

    def view(self):
        """Отображает  диалог с именем name и структурой widget.lst_params
        на экране. """
        self.children = self.widgets
        ok_flag = k3.setvar(
            self.promt.children,
            self.children,
            k3.k_done)
        self.ok_flag = ok_flag[0]
        return ok_flag[0]

    @property
    def value(self):
        res = []
        for w in self.widgets:
            if isinstance(w.value, k3.Var):
                res.append(w.value.value)
            else:
                res.append(w.value)
        return res



def _find_dependent_modules(module_name):
    """
    Найти все модули, которые зависят от указанного модуля.
    
    Эта функция сканирует все загруженные модули и проверяет их содержимое
    на наличие импортов указанного модуля. Поддерживаются различные кодировки файлов.
    
    Args:
        module_name (str): Имя модуля, для которого нужно найти зависимости
        
    Returns:
        list: Список имен модулей, которые зависят от указанного модуля
    """
    dependent_modules = []
    for name, module in sys.modules.items():
        if hasattr(module, '__file__') and module.__file__:
            try:
                # Попробуем сначала UTF-8, затем другие кодировки
                encodings = ['utf-8', 'cp1251', 'latin1']
                content = None
                for encoding in encodings:
                    try:
                        with open(module.__file__, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                # Если ни одна кодировка не сработала, пропускаем файл
                if content is None:
                    continue
                    
                if f'import {module_name}' in content or f'from {module_name}' in content:
                    dependent_modules.append(name)
            except (IOError, OSError):
                pass
    return dependent_modules


def _get_package_dependencies(package):
    assert(hasattr(package, "__package__"))
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    node_set = {fn}  # набор имен файлов модулей
    node_depth_dict = {fn:0} # отслеживает наибольшую глубину, которую мы видели для каждого узла
    node_pkg_dict = {fn:package} # сопоставление имен файлов модуля с объектами модуля
    link_set = set() # кортеж (имя файла родительского модуля, имя файла дочернего модуля)
    del fn

    def dependency_traversal_recursive(module, depth):
        for module_child in vars(module).values():

            # skip anything that isn't a module
            if not isinstance(module_child, types.ModuleType):
                continue

            fn_child = getattr(module_child, "__file__", None)

            # пропустить что-либо без имени файла или вне пакета
            if (fn_child is None) or (not fn_child.startswith(fn_dir)):
                continue

            # мы видели этот модуль раньше? если нет, то добавьте в базу
            if not fn_child in node_set:
                node_set.add(fn_child)
                node_depth_dict[fn_child] = depth
                node_pkg_dict[fn_child] = module_child

            # установите глубину как самую глубокую глубину, с которой мы столкнулись в узле
            node_depth_dict[fn_child] = max(depth, node_depth_dict[fn_child])

            # посещали ли мы этот дочерний модуль из этого родительского модуля раньше?
            if not ((module.__file__, fn_child) in link_set):
                link_set.add((module.__file__, fn_child))
                dependency_traversal_recursive(module_child, depth+1)
            else:
                print(f"В графе зависимостей {module_child} обнаружен цикл!")
                continue

                # raise ValueError("В графе зависимостей обнаружен цикл!")


def auto_reload_module(module_name):
    """
    Автоматически перезагрузить модуль и все его зависимости.
    
    Эта функция перезагружает указанный модуль, а затем находит и перезагружает
    все модули, которые зависят от него. Это обеспечивает целостную перезагрузку
    модуля со всеми его зависимостями.
    
    Args:
        module_name (str): Имя модуля для перезагрузки
    """
    # Сначала перезагружаем сам модуль
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
        print(f"Перезагружен модуль {module_name}")
    
    # Находим и перезагружаем все зависимые модули
    dependent_modules = _find_dependent_modules(module_name)
    for dep_module in dependent_modules:
        if dep_module in sys.modules:
            importlib.reload(sys.modules[dep_module])
            print(f"Перезагружен зависимый модуль {dep_module}")

def reload_module_with_dependencies(module_name):
    """
    Перезагрузить модуль и все модули, которые зависят от него.
    
    Другой вариант auto_reload_module. Эта функция перезагружает указанный модуль,
    а затем находит и перезагружает все модули, которые зависят от него.
    Отличие от auto_reload_module в том, что она использует функцию
    _get_package_dependencies для определения зависимостей.
    
    Args:
        module_name (str): Имя модуля для перезагрузки
    """
    # Если модуль загружен, перезагружаем его
    if module_name in sys.modules:
        module = sys.modules[module_name]
        # Получаем зависимости модуля
        try:
            node_pkg_dict, node_depth_dict = _get_package_dependencies(module)
            # Перезагружаем в обратном порядке
            for (d, v) in sorted([(d, v) for v, d in node_depth_dict.items()], reverse=True):
                if v in node_pkg_dict:
                    importlib.reload(node_pkg_dict[v])
                    print(f"Перезагружен {v}")
        except:
            # Если не удалось получить зависимости, просто перезагружаем модуль
            importlib.reload(module)
            print(f"Перезагружен модуль {module_name}")

def selective_reload(module_name_prefix):
    """
    Перезагрузить все модули с указанным префиксом.
    
    Механизм полной очистки кэша импортов. Можно адаптировать его для перезагрузки
    только определенных модулей, которые начинаются с указанного префикса.
    
    Args:
        module_name_prefix (str): Префикс имени модулей для перезагрузки
    """
    modules_to_reload = []
    for module_name, module in sys.modules.items():
        if module_name.startswith(module_name_prefix):
            modules_to_reload.append((module_name, module))
    
    # Сортируем по имени модуля для обеспечения правильного порядка перезагрузки
    modules_to_reload.sort()
    
    for module_name, module in modules_to_reload:
        try:
            importlib.reload(module)
            print(f"Перезагружен модуль {module_name}")
        except Exception as e:
            print(f"Ошибка перезагрузки модуля {module_name}: {e}")

# Файл для сохранения последнего значения defModuleName и def_reload_fun
DEF_MODULE_NAME_FILE = os.path.join(os.path.dirname(__file__), '.def_module_name')

def save_def_module_name(module_name, reload_function='auto_reload_module'):
    """
    Сохранить значение defModuleName и имя функции перезагрузки в файл.
    
    Эта функция сохраняет имя модуля и имя функции перезагрузки в файл
    для последующего использования при следующем запуске программы.
    
    Args:
        module_name (str): Имя модуля для сохранения
        reload_function (str, optional): Имя функции перезагрузки. По умолчанию 'auto_reload_module'
    """
    try:
        with open(DEF_MODULE_NAME_FILE, 'wb') as f:
            pickle.dump((module_name, reload_function), f)
    except Exception as e:
        print(f"Ошибка сохранения defModuleName: {e}")

def load_def_module_name():
    """
    Загрузить значение defModuleName и имя функции перезагрузки из файла.
    
    Эта функция загружает имя модуля и имя функции перезагрузки из файла,
    сохраненного функцией save_def_module_name. Если файл не существует
    или поврежден, возвращаются значения по умолчанию.
    
    Returns:
        tuple: Кортеж из двух элементов: (имя_модуля, имя_функции_перезагрузки)
    """
    try:
        if os.path.exists(DEF_MODULE_NAME_FILE):
            with open(DEF_MODULE_NAME_FILE, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, tuple) and len(data) == 2:
                    return data
                else:
                    # Если данные в старом формате, возвращаем их как имя модуля
                    return (data, 'auto_reload_module')
    except Exception as e:
        print(f"Ошибка загрузки defModuleName: {e}")
    return ('MyModule', 'auto_reload_module')  # Значения по умолчанию

# Загружаем имя модуля и имя функции перезагрузки
defModuleData = load_def_module_name()
defModuleName = defModuleData[0]
defReloadFunction = defModuleData[1]

def safe_call_local(function_name, *args, **kwargs):
    """
    Безопасный вызов функции в текущем модуле.
    
    Эта функция проверяет наличие функции с указанным именем в глобальном
    пространстве имен текущего модуля и вызывает её с переданными аргументами,
    если она существует и является вызываемой.
    
    Args:
        function_name (str): Имя функции для вызова
        *args: Позиционные аргументы для передачи функции
        **kwargs: Именованные аргументы для передачи функции
        
    Returns:
        Результат вызова функции
        
    Raises:
        NameError: Если функция с указанным именем не найдена
        TypeError: Если объект с указанным именем не является функцией
    """
    if function_name in globals():
        func = globals()[function_name]
        if callable(func):
            return func(*args, **kwargs)
        else:
            raise TypeError(f"{function_name} не является функцией")
    else:
        raise NameError(f"Функция {function_name} не найдена")

if __name__ == '__main__':
    reload_functions =('auto_reload_module', 'reload_module_with_dependencies', 'selective_reload')
    import_names = get_import_names(minutes=30)
    print(f"\nИмена модулей для импорта: {import_names}")

    dlg = SetVar()
    dlg.promt = Title('Централизованный механизм перезагрузки',
                      'Автоматически перезагружает модуль и все','его зависимости','...',
                      'За последние 30 минут исправлены модули:',*import_names[:3], '..............',
                      'По умалчанию показан самый "молодой" модуль из списка.',
                      'Выберите при необходимости другой модуль для перезагрузки.',
                      'Во втором поле можно выбрать функцию перезагрузки.', 
                      'Если нет острой необходимости оставьте значение по умолчанию auto_reload_module.')
    if import_names:
        defModuleName = import_names[0]
    dlg.widgets.extend([
        WString('Выберите имя модуля:', *import_names, lst=defModuleName),
        WString('Укажите функцию перезагрузки:', *reload_functions, lst=defReloadFunction),
    ])
    res = dlg.view()
    defModuleName = dlg.widgets[0].value
    defReloadFunction = dlg.widgets[1].value
    if res:
        save_def_module_name(defModuleName, defReloadFunction)  # Сохраняем новое значение имени модуля и функции перезагрузки
        logger.debug(f'defModuleName = {defModuleName}, defReloadFunction = {defReloadFunction}')

        try:
            safe_call_local(defReloadFunction, defModuleName)
        except Exception as e:
            print(f'Ошибка: {e}')
        # Возможные варианты использования:
        # auto_reload_module(defModuleName)
        # reload_module_with_dependencies(defModuleName)
        # selective_reload(defModuleName)
    else:
        print('Отмена')
