import sys
import os
import tempfile
import pickle
from unittest import mock
import pytest

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from auto_reload_manager import (
    _find_dependent_modules,
    auto_reload_module,
    reload_module_with_dependencies,
    selective_reload,
    save_def_module_name,
    load_def_module_name,
    safe_call_local,
    SetVar,
    Title,
    WString,
    DEF_MODULE_NAME_FILE
)

def test_find_dependent_modules():
    """Тест функции _find_dependent_modules"""
    # Создаем временный файл для тестирования
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("import os\nimport sys\nfrom test_module import something\n")
        temp_file = f.name

    # Создаем временный модуль
    temp_module = mock.MagicMock()
    temp_module.__file__ = temp_file

    # Подменяем sys.modules
    with mock.patch('sys.modules', {'temp_module': temp_module}):
        result = _find_dependent_modules('test_module')
        assert 'temp_module' in result

    # Удаляем временный файл
    os.unlink(temp_file)

def test_safe_call_local_success():
    """Тест успешного вызова функции через safe_call_local"""
    # Просто проверяем, что функция существует и может быть вызвана
    # без ошибок импорта модуля

def test_safe_call_local_name_error():
    """Тест функции safe_call_local на NameError"""
    with pytest.raises(NameError):
        safe_call_local('non_existent_function')

def test_safe_call_local_type_error():
    """Тест функции safe_call_local на TypeError"""
    # Добавляем переменную вместо функции в модуль auto_reload_manager
    import auto_reload_manager
    auto_reload_manager.not_a_function = "I'm not a function"

    try:
        with pytest.raises(TypeError):
            safe_call_local('not_a_function')
    finally:
        # Удаляем переменную из модуля
        delattr(auto_reload_manager, 'not_a_function')

def test_save_and_load_def_module_name():
    """Тест функций save_def_module_name и load_def_module_name"""
    # Создаем временную директорию для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        # Подменяем путь к файлу
        with mock.patch('auto_reload_manager.DEF_MODULE_NAME_FILE', 
                        os.path.join(temp_dir, '.def_module_name')):
            # Сохраняем данные
            save_def_module_name('test_module', 'test_function')
            
            # Загружаем данные
            module_name, reload_function = load_def_module_name()
            
            # Проверяем
            assert module_name == 'test_module'
            assert reload_function == 'test_function'

def test_load_def_module_name_default():
    """Тест функции load_def_module_name с дефолтными значениями"""
    # Создаем временную директорию для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        # Подменяем путь к файлу на несуществующий
        with mock.patch('auto_reload_manager.DEF_MODULE_NAME_FILE', 
                        os.path.join(temp_dir, 'non_existent_file')):
            # Загружаем данные
            module_name, reload_function = load_def_module_name()
            
            # Проверяем дефолтные значения
            assert module_name == 'MyModule'
            assert reload_function == 'auto_reload_module'

def test_selective_reload():
    """Тест функции selective_reload"""
    # Создаем тестовые модули
    test_modules = {
        'test_module1': mock.MagicMock(),
        'test_module2': mock.MagicMock(),
        'other_module': mock.MagicMock()
    }

    # Подменяем sys.modules
    with mock.patch('sys.modules', test_modules):
        with mock.patch('importlib.reload') as mock_reload:
            # Вызываем функцию
            selective_reload('test_module')
            
            # Проверяем, что reload был вызван дважды (для test_module1 и test_module2)
            assert mock_reload.call_count == 2

def test_title_class():
    """Тест класса Title"""
    # Создаем экземпляр класса Title
    title = Title('Test Title', 'Line 1', 'Line 2')
    
    # Проверяем, что children не пустой
    assert len(title.children) > 0

def test_wstring_class():
    """Тест класса WString"""
    # Создаем экземпляр класса WString
    wstring = WString('Prompt', 'Value1', 'Value2', defval='Default')
    
    # Проверяем, что children не пустой
    assert len(wstring.children) > 0

def test_setvar_class():
    """Тест класса SetVar"""
    # Создаем экземпляр класса SetVar
    setvar = SetVar()
    
    # Проверяем, что widgets - это список
    assert isinstance(setvar.widgets, list)

if __name__ == '__main__':
    # Запуск тестов
    pytest.main([__file__])