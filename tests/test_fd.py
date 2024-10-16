# tests/test_filter_dict.py

import pytest
from happy import FilteredDict

# Fixtures
@pytest.fixture
def sample_data():
    return {'apple': 1, 'banana': 2, 'cherry': 3, 'date': 4, 'elderberry': 5}

@pytest.fixture
def filter_dict_instance(sample_data):
    return FilteredDict(sample_data)

# Test Initialization
def test_initialization(filter_dict_instance, sample_data):
    assert isinstance(filter_dict_instance, FilteredDict)
    assert dict(filter_dict_instance) == sample_data
    assert filter_dict_instance.list_filters() == []

def test_initialization_empty():
    fd = FilteredDict()
    assert isinstance(fd, FilteredDict)
    assert dict(fd) == {}
    assert fd.list_filters() == []

def test_from_dict():
    d = {'key1': 'value1', 'key2': 'value2'}
    fd = FilteredDict.from_dict(d)
    assert isinstance(fd, FilteredDict)
    assert dict(fd) == d

# Test Adding Filters
def test_add_filter(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    assert filter_func in filter_dict_instance.list_filters()
    assert filter_dict_instance._filtered_cache is None

def test_add_multiple_filters(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_func2 = lambda item: item[0].startswith('b')
    filter_dict_instance.add_filter(filter_func1)
    filter_dict_instance.add_filter(filter_func2)
    assert filter_func1 in filter_dict_instance.list_filters()
    assert filter_func2 in filter_dict_instance.list_filters()

# Test Removing Filters
def test_remove_filter(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    assert filter_func in filter_dict_instance.list_filters()
    filter_dict_instance.remove_filter(filter_func)
    assert filter_func not in filter_dict_instance.list_filters()
    assert filter_dict_instance._filtered_cache is None

def test_remove_nonexistent_filter(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    with pytest.raises(ValueError) as exc_info:
        filter_dict_instance.remove_filter(filter_func)
    assert "Filter function not found in filters list." in str(exc_info.value)

# Test Clearing Filters
def test_clear_filters(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_func2 = lambda item: item[0].startswith('b')
    filter_dict_instance.add_filter(filter_func1)
    filter_dict_instance.add_filter(filter_func2)
    assert len(filter_dict_instance.list_filters()) == 2
    filter_dict_instance.clear_filters()
    assert filter_dict_instance.list_filters() == []
    assert filter_dict_instance._filtered_cache is None

# Test Listing Filters
def test_list_filters(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_func2 = lambda item: item[0].startswith('c')
    filter_dict_instance.add_filter(filter_func1)
    filter_dict_instance.add_filter(filter_func2)
    filters = filter_dict_instance.list_filters()
    assert len(filters) == 2
    assert filter_func1 in filters
    assert filter_func2 in filters

# Test Applying Filters
def test_apply_filters_no_filters(filter_dict_instance, sample_data):
    filtered = filter_dict_instance.apply_filters()
    assert dict(filtered) == sample_data

def test_apply_filters_single_filter(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    filtered = filter_dict_instance.apply_filters()
    expected = {'cherry': 3, 'date': 4, 'elderberry': 5}
    assert dict(filtered) == expected

def test_apply_filters_multiple_filters(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_func2 = lambda item: item[0].startswith('b') or item[0].startswith('c')
    filter_dict_instance.add_filter(filter_func1)
    filter_dict_instance.add_filter(filter_func2)
    filtered = filter_dict_instance.apply_filters()
    expected = {'banana': 2, 'cherry': 3}
    assert dict(filtered) == expected

def test_apply_filters_caching(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    first_filtered = filter_dict_instance.apply_filters()
    second_filtered = filter_dict_instance.apply_filters()
    assert first_filtered is not second_filtered  # Because a copy is returned
    assert dict(first_filtered) == {'cherry': 3, 'date': 4, 'elderberry': 5}

# Test `__getitem__` Behavior
def test_getitem_without_filters(filter_dict_instance):
    assert filter_dict_instance['apple'] == 1
    assert filter_dict_instance['date'] == 4

def test_getitem_with_filters_existing_key(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    assert filter_dict_instance['cherry'] == 3
    assert filter_dict_instance['elderberry'] == 5

def test_getitem_with_filters_nonexistent_key(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    with pytest.raises(KeyError):
        _ = filter_dict_instance['banana']

# Test `get_filtered_items`
def test_get_filtered_items_no_filters(filter_dict_instance, sample_data):
    filtered_items = filter_dict_instance.get_filtered_items()
    assert filtered_items == list(sample_data.items())

def test_get_filtered_items_with_filters(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_func2 = lambda item: item[0].startswith('c')
    filter_dict_instance.add_filter(filter_func1)
    filter_dict_instance.add_filter(filter_func2)
    filtered_items = filter_dict_instance.get_filtered_items()
    assert filtered_items == [('cherry', 3)]

# Test `add_regex_filter`
def test_add_regex_filter_key(filter_dict_instance):
    pattern = r'^b|c'
    filter_dict_instance.add_regex_filter(pattern, search_in='key')
    filtered = filter_dict_instance.apply_filters()
    expected = {'banana': 2, 'cherry': 3}
    assert dict(filtered) == expected

def test_add_regex_filter_value(filter_dict_instance):
    pattern = r'^[34]$'  # Match values 3 or 4
    filter_dict_instance.add_regex_filter(pattern, search_in='value')
    filtered = filter_dict_instance.apply_filters()
    expected = {'cherry': 3, 'date': 4}
    assert dict(filtered) == expected

def test_add_regex_filter_invalid_search_in(filter_dict_instance):
    with pytest.raises(ValueError) as exc_info:
        filter_dict_instance.add_regex_filter(r'^a', search_in='invalid')
    assert "search_in must be 'key' or 'value'" in str(exc_info.value)

# Test `add_key_filter` and `add_value_filter`
def test_add_key_filter(filter_dict_instance):
    key_predicate = lambda key: key.endswith('e')
    filter_dict_instance.add_key_filter(key_predicate)
    filtered = filter_dict_instance.apply_filters()
    expected = {'apple': 1, 'date': 4}
    assert dict(filtered) == expected

def test_add_value_filter(filter_dict_instance):
    value_predicate = lambda value: value % 2 == 0
    filter_dict_instance.add_value_filter(value_predicate)
    filtered = filter_dict_instance.apply_filters()
    expected = {'banana': 2, 'date': 4}
    assert dict(filtered) == expected

# Test `update_filters`
def test_update_filters(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_func2 = lambda item: item[0].startswith('c')
    new_filters = [filter_func1, filter_func2]
    filter_dict_instance.update_filters(new_filters)
    assert filter_dict_instance.list_filters() == new_filters
    filtered = filter_dict_instance.apply_filters()
    expected = {'cherry': 3}
    assert dict(filtered) == expected

def test_update_filters_empty(filter_dict_instance):
    filter_func1 = lambda item: item[1] > 1
    filter_dict_instance.add_filter(filter_func1)
    assert len(filter_dict_instance.list_filters()) == 1
    filter_dict_instance.update_filters([])
    assert filter_dict_instance.list_filters() == []
    assert dict(filter_dict_instance.apply_filters()) == dict(filter_dict_instance)

# Test `__repr__`
def test_repr(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    repr_str = repr(filter_dict_instance)
    assert "FilteredDict" in repr_str
    assert "apple" in repr_str
    assert "filters" in repr_str
    assert str(filter_func) in repr_str

# Test Cache Invalidation
def test_cache_invalidation_on_add_filter(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.apply_filters()  # Populate cache
    assert filter_dict_instance._filtered_cache is not None
    filter_dict_instance.add_filter(filter_func)
    assert filter_dict_instance._filtered_cache is None

def test_cache_invalidation_on_setitem(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    filter_dict_instance.apply_filters()  # Populate cache
    assert filter_dict_instance._filtered_cache is not None
    filter_dict_instance['fig'] = 6  # Modify dict
    assert filter_dict_instance._filtered_cache is None

def test_cache_invalidation_on_delitem(filter_dict_instance):
    filter_func = lambda item: item[1] > 2
    filter_dict_instance.add_filter(filter_func)
    filter_dict_instance.apply_filters()  # Populate cache
    assert filter_dict_instance._filtered_cache is not None
    del filter_dict_instance['cherry']
    assert filter_dict_instance._filtered_cache is None

# Test `__setitem__` and `__delitem__`
def test_setitem(filter_dict_instance):
    filter_dict_instance['fig'] = 6
    assert filter_dict_instance['fig'] == 6
    assert 'fig' in filter_dict_instance

def test_delitem(filter_dict_instance):
    del filter_dict_instance['apple']
    assert 'apple' not in filter_dict_instance
    with pytest.raises(KeyError):
        _ = filter_dict_instance['apple']

# Test Error Handling in `__getitem__`
def test_getitem_keyerror(filter_dict_instance):
    with pytest.raises(KeyError):
        _ = filter_dict_instance['nonexistent']

# Test Complex Filter Scenario
def test_complex_filters(filter_dict_instance):
    # Add multiple filters
    filter_dict_instance.add_filter(lambda item: item[1] >= 2)
    filter_dict_instance.add_filter(lambda item: 'e' in item[0])
    filter_dict_instance.add_regex_filter(r'^d', search_in='key')  # Keys starting with 'd'
    filtered = filter_dict_instance.apply_filters()
    expected = {'date': 4}
    assert dict(filtered) == expected

# Test Filters on Non-String Keys/Values
def test_filters_non_string_keys(filter_dict_instance):
    # Add integer keys
    fd = FilteredDict({1: 'one', 2: 'two', 3: 'three'})
    fd.add_key_filter(lambda key: key > 1)
    filtered = fd.apply_filters()
    expected = {2: 'two', 3: 'three'}
    assert dict(filtered) == expected

def test_filters_non_string_values(filter_dict_instance):
    # Add mixed value types
    fd = FilteredDict({'a': 1, 'b': 'two', 'c': 3.0})
    fd.add_value_filter(lambda value: isinstance(value, int))
    filtered = fd.apply_filters()
    expected = {'a': 1}
    assert dict(filtered) == expected
