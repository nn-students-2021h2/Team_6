import os
import sys

from numpy import save
sys.path.append('c:\\PyhonProjects\\Intel_python\\team_6_last\\Team_6\\Picture_bot')
import unittest
import shutil
from pathlib import Path
from Config import Configs

# 31.01.2022 TO DO: invalid compilation of cli_args unit_tests

class TestBaseConfig_creation(unittest.TestCase):
    def test_default_file_path(self):
        conf_1 = Configs.config()
        self.assertEqual(str(conf_1._file_path),
         "C:\\PyhonProjects\\Intel_python\\team_6_last\\Team_6\\Picture_bot\\Config\\config.json")

    def test_user_file_path(self):
        conf_1 = Configs.config(file_path = Path(__file__).resolve().parent / 'config.json')
        self.assertEqual(str(conf_1._file_path),
         "C:\\PyhonProjects\\Intel_python\\team_6_last\\Team_6\\Picture_bot\\Config\\tests\\config.json")
    
    def test_singleton(self):
        conf_1 = Configs.config()
        conf_2 = Configs.config(file_path = Path(__file__).resolve().parent / 'config.json')
        self.assertIs(conf_1, conf_2)
    
    def test_json_parse(self):
        conf_1 = Configs.config()
        test_dict = {
                "config_name": "default_test",
                "NAME": "test_config",
                "MODE": "common",
                "HOST": "localhost",
                "PORT": 8080
        }
        self.assertEqual(conf_1._properties, test_dict)

    def test_json_with_cli_parse(self):
        conf_1 = Configs.config(cli_args=["NAME=from_test_config" ,"PORT=5050"])
        test_dict = {
                "config_name": "default_test",
                "NAME": "from_test_config",
                "MODE": "common",
                "HOST": "localhost",
                "PORT": 5050
        }
        self.assertEqual(conf_1._properties, test_dict)

    def test_default_file_not_found(self):
        source_dir = Path(__file__).parent.parent
        json_conf = source_dir / 'config.json'
        
        save_dir = Path(__file__).parent / 'save'
        os.mkdir(save_dir)

        shutil.copy(json_conf, save_dir)
        os.remove(json_conf)

        with self.assertRaises(Configs.ConfigException):
            conf_1 = Configs.config()
    
    def test_invalid_decoding(self):
        with self.assertRaises(Configs.ConfigException):
            conf_1 = Configs.config(file_path = Path(__file__).resolve().parent / 'invalid_config.json')
    
    def test_invalid_properties(self):
        with self.assertRaises(Configs.ConfigException):
            conf_1 = Configs.config(cli_args=["RUN_TYPE=from_test_config" ,"PORT=5050"])

    def test_invalid_type_of_properties(self):
        with self.assertRaises(Configs.ConfigException):
            conf_1 = Configs.config(cli_args=["NAME=['bot', 'core']"])
    
    def tearDown(self) -> None:
        del Configs.config._SingleInstanceMetaClass__single_instance
        Configs.config._SingleInstanceMetaClass__single_instance = None
        
        source_dir = Path(__file__).parent.parent
        save_dir = Path(__file__).parent / 'save'
        save_file_name = 'config.json'
        if(save_dir.exists()):
            shutil.copy(save_dir / save_file_name, source_dir)
            shutil.rmtree(save_dir)
        
class TestBaseConfig(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()