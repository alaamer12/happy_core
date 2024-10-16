import pytest
import os
import json
import configparser
from happy import Environment, MODES
from happy.exceptions import EnvError


@pytest.fixture
def temp_env_file(tmp_path):
    """
    Create a temporary .env file for testing.
    """
    env_path = tmp_path / ".env"
    with open(env_path, 'w') as f:
        f.write("KEY1=value1\nKEY2=value2\n")
    return str(env_path)


@pytest.fixture
def environment(temp_env_file):
    """
    Initialize the Environment class with the temporary .env file.
    """
    return Environment(env_data=temp_env_file)


def test_load_env(environment, temp_env_file, monkeypatch):
    """
    Test loading environment variables from the .env file.
    """
    # Use monkeypatch to ensure that os.environ is updated
    environment.load_env()
    assert os.getenv("KEY1") == "value1"
    assert os.getenv("KEY2") == "value2"


def test_read_env(environment):
    """
    Test reading environment variables from the .env file.
    """
    env_vars = environment.read_env()
    assert env_vars["KEY1"] == "value1"
    assert env_vars["KEY2"] == "value2"


def test_set_env(environment, temp_env_file):
    """
    Test setting a new environment variable.
    """
    environment.set_env("KEY3", "value3")
    env_vars = environment.read_env()
    assert env_vars["KEY3"] == "value3"

    # Verify that the .env file was updated
    with open(temp_env_file, 'r') as f:
        content = f.read()

    # Quotes are important here
    assert "KEY3='value3'" in content


def test_get_env(environment):
    """
    Test retrieving an existing and a non-existing environment variable.
    """
    value = environment.get_env("KEY1")
    assert value == "value1"
    value_none = environment.get_env("NON_EXISTENT_KEY")
    assert value_none is None


def test_override_env(environment):
    """
    Test overriding an environment variable without saving to the .env file.
    """
    override = environment.override_env("KEY1", "new_value1")
    assert override["KEY1"] == "new_value1"
    # Ensure the original .env file remains unchanged
    env_vars = environment.read_env()
    assert env_vars["KEY1"] == "value1"


def test_filter_env_by_key(environment):
    """
    Test filtering environment variables by key.
    """
    results = environment.filter_env("KEY1", search_in="key")
    assert results == [("KEY1", "value1")]


def test_filter_env_by_value(environment):
    """
    Test filtering environment variables by value.
    """
    results = environment.filter_env("value2", search_in="value")
    assert results == [("KEY2", "value2")]


def test_filter_env_invalid_search_in(environment):
    """
    Test filtering with an invalid search_in parameter.
    """
    with pytest.raises(ValueError):
        environment.filter_env("value", search_in="invalid")


def test_filter_with_predicate(environment):
    """
    Test filtering environment variables using a custom predicate.
    """
    predicate = lambda k, v: k.startswith("KEY") and v.endswith("1")
    results = environment.filter_with_predicate(predicate)
    assert results == [("KEY1", "value1")]


def test_mode_decorator(environment):
    """
    Test the mode_decorator to ensure functions execute only in the specified mode.
    """
    @environment.mode(func_mode=MODES.DEV)
    def dev_function():
        return "dev"

    @environment.mode(func_mode=MODES.TEST)
    def test_function():
        return "test"

    # Initially in DEV mode
    assert dev_function() == "dev"
    assert test_function() is None

    # Change mode to TEST
    environment._mode = MODES.TEST
    assert dev_function() is None
    assert test_function() == "test"


def test_from_json(tmp_path):
    """
    Test loading environment variables from a JSON file.
    """
    json_path = tmp_path / "env.json"
    data = {"JSON_KEY1": "json_value1", "JSON_KEY2": "json_value2"}
    with open(json_path, 'w') as f:
        json.dump(data, f)

    env = Environment.from_json(str(json_path))
    assert env.get_env("JSON_KEY1") == "json_value1"
    assert env.get_env("JSON_KEY2") == "json_value2"


def test_from_dict(tmp_path):
    """
    Test loading environment variables from a dictionary.
    """
    env_dict = {"DICT_KEY1": "dict_value1", "DICT_KEY2": "dict_value2"}
    env = Environment.from_dict(env_dict)
    assert env.get_env("DICT_KEY1") == "dict_value1"
    assert env.get_env("DICT_KEY2") == "dict_value2"


def test_from_config(tmp_path):
    """
    Test loading environment variables from a configuration (.ini) file.
    """
    config_path = tmp_path / "config.ini"
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'CONFIG_KEY1': 'config_value1', 'CONFIG_KEY2': 'config_value2'}
    with open(config_path, 'w') as f:
        config.write(f)

    env = Environment.from_config(str(config_path))
    assert env.get_env("config_key1") == "config_value1"
    assert env.get_env("config_key2") == "config_value2"


def test_repr(environment):
    """
    Test the __repr__ method of the Environment class.
    """
    repr_str = repr(environment)
    assert "mode=dev" in repr_str
    assert f"env_path={environment._env_data}" in repr_str
    assert "('KEY1', 'value1')" in repr_str


def test_initialization_with_kwargs(tmp_path):
    """
    Test initializing the Environment class with custom _env_path and _mode.
    """
    env_path = tmp_path / ".env"
    with open(env_path, 'w') as f:
        f.write("INIT_KEY=init_value\n")
    # Initialize with env_path parameter
    env = Environment(env_data=str(env_path))
    # Set the mode after initialization
    env._mode = MODES.PROD
    assert env.get_env("INIT_KEY") == "init_value"
    assert env._mode == MODES.PROD


def test_handle_env_path_none():
    """
    Test that passing None as env_path raises an EnvFileError.
    """
    with pytest.raises(EnvError) as exc_info:
        Environment(env_data=None)  # Assuming env_path can be None
    assert str(exc_info.value) == "Invalid .env data."

def test_mode_decorator_no_decorator():
    """
    Test that functions without the mode decorator are always executed.
    """
    env = Environment()
    @env.mode(func_mode=MODES.DEV)
    def dev_function():
        return "dev"

    @env.mode(func_mode=MODES.TEST)
    def test_function():
        return "test"

    # Functions without decorator should always execute
    def regular_function():
        return "regular"

    assert regular_function() == "regular"


def test_set_env_overwrites_existing(environment, temp_env_file):
    """
    Test that setting an existing environment variable overwrites its value.
    """
    environment.set_env("KEY1", "new_value1")
    env_vars = environment.read_env()
    assert env_vars["KEY1"] == "new_value1"
    # Verify that the .env file was updated
    with open(temp_env_file, 'r') as f:
        content = f.read()
    assert "KEY1='new_value1'" in content


def test_multiple_env_files(tmp_path):
    """
    Test initializing multiple Environment instances with different .env files.
    """
    env_path1 = tmp_path / ".env1"
    with open(env_path1, 'w') as f:
        f.write("KEY1=value1_env1\n")

    env_path2 = tmp_path / ".env2"
    with open(env_path2, 'w') as f:
        f.write("KEY1=value1_env2\n")

    env1 = Environment(env_data=str(env_path1))
    env2 = Environment(env_data=str(env_path2))

    assert env1.get_env("KEY1") == "value1_env1"
    assert env2.get_env("KEY1") == "value1_env2"


def test_environment_isolation(environment, tmp_path):
    """
    Test that changes in one Environment instance do not affect another.
    """
    # Create another .env file
    env_path = tmp_path / "another.env"
    with open(env_path, 'w') as f:
        f.write("ANOTHER_KEY=another_value\n")

    env2 = Environment(env_data=str(env_path))

    # Set a variable in the first environment
    environment.set_env("KEY3", "value3")
    assert environment.get_env("KEY3") == "value3"
    assert env2.get_env("KEY3") is None

    # Set a variable in the second environment
    env2.set_env("ANOTHER_KEY2", "another_value2")
    assert env2.get_env("ANOTHER_KEY2") == "another_value2"
    assert environment.get_env("ANOTHER_KEY2") is None
