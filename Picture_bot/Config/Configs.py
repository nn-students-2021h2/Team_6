from msilib.schema import File
from tokenize import Single
from pathlib import Path
import json
import os
import ast
#Вариант с метаклассом выбран по причиние не повторяющегося вызова конструктора класса синглтона
#И более нативного кода реализации, все видно, все по полочкам

class SingleInstanceMetaClass(type):
    def __init__(self, name, bases, dic):
        #name - имя класса
        #bases - базовые классы
        #dic - ключевые аргументы
        self.__single_instance = None
        super().__init__(name, bases, dic)
        #На выходе будет объект SingleInstanceMetaClass инициализированный классом name

    def __call__(cls, *args, **kwargs):
        #Config_SingleInstanceMetaClass(Config с его аргументами)
        #Если у класса cls есть поле __single_instance, то возвращаем это поле
        if cls.__single_instance:
            return cls.__single_instance
        #Вызываем стандартный new инстанцируем объект класса cls
        single_object = super(type, cls).__new__(cls)
        #Надеюсь полулось что он стандарнтый

        #Инициализируем объект класса cls
        single_object.__init__(*args, **kwargs)
        
        cls.__single_instance = single_object
        return single_object

class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

class config(metaclass=SingleInstanceMetaClass):
    # Проверить default_cfg_path
    default_cfg_path = Path(__file__).resolve().parent / "config.json"
    _properties = None

    def __init__(self, file_path=None, cli_args=None):
        self._file_path = file_path or config.default_cfg_path
        self._cli_args = cli_args or []

        #use file_path inside
        self._json_cfg = self._load_cfg()
        #use cli_args
        self._args = self._parse_cli_args()
        #use _json_cfg and _args inside
        self._properties = self._parse_properties()

    def _load_cfg(self):
        json_cfg = None
        try:
            with open(self._file_path, encoding="utf-8") as cfg:
                json_cfg = json.load(cfg)
        # JSONDecodeError можно бы использовать.
        # FileNoteFound
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise ConfigException(f"Failed to process configuration file: {self._file_path}, {type(exc).__name__}")
        return json_cfg

    def _parse_cli_args(self):
        """Parse argparse arguments with patterns: 'name=value' or 'name'"""
        parsed_cli_args = {}
        for cli_arg in self._cli_args:
            arg = cli_arg.split("=")
            if arg[0] not in self._json_cfg:
                raise ConfigException(f"Unsupported argument: {arg}")
            #То есть мы предполагаем что у нас есть некоторое выражение включающее литеральные константы, и в дальнейшем мы это выражение проверяем
            parsed_cli_args[arg[0]] = True if len(arg) == 1 else "=".join(arg[1:])
        return parsed_cli_args
    
    def _parse_properties(self):
        parsed_properties = {}
        for name, value in self._json_cfg.items():
            if hasattr(self, name):
                raise ConfigException(f"Duplicating prosperity: {name}")
            property_value = self._args.get(name) or os.getenv(name)
            
            if property_value:
                # Try to set prosperity_value as Python literal structures, e.g. DRY_RUN=False
                
                try:
                    property_value = ast.literal_eval(property_value)
                except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError) as exc:
                    pass
                if not isinstance(property_value, type(value)):
                    raise ConfigException(f"Python type of {name} parameter must be {type(value)}")
            else:
                property_value = value
            parsed_properties[name] = property_value
        return parsed_properties

class bot_config(config):
    default_cfg_path = Path(__file__).resolve().parent / "bot_config.json"
    def __init__(self, file_path=None, cli_args=None):
        super().__init__(file_path, cli_args)

class core_config(config):
    default_cfg_path = Path(__file__).resolve().parent / "core_config.json"
    def __init__(self, file_path=None, cli_args=None):
        super().__init__(file_path, cli_args)