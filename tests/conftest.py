import sys
from unittest import mock

# mock для Keyword
class MockKeyword:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"<Ключ: {self.name}>"

# mock для Var
class MockVar:
    def __init__(self, value=None):
        self.value = value

# mock для модуля k3
k3_mock = mock.MagicMock()

# Добавляем необходимые атрибуты для k3
k3_mock.k_left = MockKeyword("left")
k3_mock.k_right = MockKeyword("right")
k3_mock.k_center = MockKeyword("center")
k3_mock.k_auto = MockKeyword("auto")
k3_mock.k_size = MockKeyword("size")
k3_mock.k_done = MockKeyword("done")
k3_mock.k_list = MockKeyword("list")
k3_mock.k_listonly = MockKeyword("listonly")
k3_mock.k_current = MockKeyword("current")
k3_mock.k_string = MockKeyword("string")

# Добавляем классы
k3_mock.Keyword = MockKeyword
k3_mock.Var = MockVar

# mock для setvar
k3_mock.setvar = mock.MagicMock(return_value=[True])

# Подменяем модуль k3 в sys.modules
sys.modules['k3'] = k3_mock