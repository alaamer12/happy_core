# -------------------------
# Test Suite
# -------------------------
import unittest

from happy.util import find_first_index, find_last_index, find_all_indices, find_next_indices, replace_all, remove_all, \
    find_all, ComplexTypeValidator, Constant, Pointer, CaseInsensitiveDict, LookupDict


class TestFindFunctions(unittest.TestCase):
    def setUp(self):
        self.sequence = [1, 2, 3, 2, 4, 2, 5]
        self.empty_sequence = []
        self.non_repeating_sequence = [1, 2, 3, 4, 5]

    # Tests for find_first_index
    def test_find_first_index_present_once(self):
        self.assertEqual(find_first_index([10], 10), 0)

    def test_find_first_index_present_multiple(self):
        self.assertEqual(find_first_index(self.sequence, 2), 1)

    def test_find_first_index_not_present(self):
        self.assertIsNone(find_first_index(self.sequence, 6))

    def test_find_first_index_empty_sequence(self):
        self.assertIsNone(find_first_index(self.empty_sequence, 1))

    def test_find_first_index_different_types(self):
        mixed_sequence = [1, '2', 3.0, '2']
        self.assertEqual(find_first_index(mixed_sequence, '2'), 1)
        self.assertEqual(find_first_index(mixed_sequence, 3.0), 2)

    # Tests for find_last_index
    def test_find_last_index_present_once(self):
        self.assertEqual(find_last_index([10], 10), 0)

    def test_find_last_index_present_multiple(self):
        self.assertEqual(find_last_index(self.sequence, 2), 5)

    def test_find_last_index_not_present(self):
        self.assertIsNone(find_last_index(self.sequence, 6))

    def test_find_last_index_empty_sequence(self):
        self.assertIsNone(find_last_index(self.empty_sequence, 1))

    def test_find_last_index_different_types(self):
        mixed_sequence = [1, '2', 3.0, '2']
        self.assertEqual(find_last_index(mixed_sequence, '2'), 3)
        self.assertEqual(find_last_index(mixed_sequence, 3.0), 2)

    # Tests for find_all_indices
    def test_find_all_indices_multiple(self):
        self.assertEqual(find_all_indices(self.sequence, 2), [1, 3, 5])

    def test_find_all_indices_single(self):
        self.assertEqual(find_all_indices([1, 2, 3], 2), [1])

    def test_find_all_indices_not_present(self):
        self.assertEqual(find_all_indices(self.sequence, 6), [])

    def test_find_all_indices_empty_sequence(self):
        self.assertEqual(find_all_indices(self.empty_sequence, 1), [])

    # Tests for find_next_indices
    def test_find_next_indices_start_zero(self):
        self.assertEqual(find_next_indices(self.sequence, 2), [1, 3, 5])

    def test_find_next_indices_start_middle(self):
        self.assertEqual(find_next_indices(self.sequence, 2, start_index=2), [3, 5])

    def test_find_next_indices_start_at_last_occurrence(self):
        self.assertEqual(find_next_indices(self.sequence, 2, start_index=5), [5])

    def test_find_next_indices_start_beyond_length(self):
        self.assertEqual(find_next_indices(self.sequence, 2, start_index=10), [])

    def test_find_next_indices_target_not_present_after_start(self):
        self.assertEqual(find_next_indices(self.sequence, 2, start_index=6), [])

    def test_find_next_indices_start_index_negative(self):
        # Assuming negative start_index counts from the end
        self.assertEqual(find_next_indices(self.sequence, 2, start_index=-3), [3,5])

    def test_find_next_indices_different_types(self):
        mixed_sequence = [1, '2', 3.0, '2']
        self.assertEqual(find_next_indices(mixed_sequence, '2'), [1, 3])
        self.assertEqual(find_next_indices(mixed_sequence, 3.0), [2])

class TestReplaceRemoveFindAllFunctions(unittest.TestCase):
    def setUp(self):
        self.sequence = [1, 2, 3, 2, 4, 2, 5]
        self.empty_sequence = []
        self.non_repeating_sequence = [1, 2, 3, 4, 5]

    # Tests for replace_all
    def test_replace_all_multiple(self):
        replaced = replace_all(self.sequence, 2, 20)
        self.assertEqual(replaced, [1, 20, 3, 20, 4, 20, 5])

    def test_replace_all_single(self):
        replaced = replace_all([1, 2, 3], 2, 20)
        self.assertEqual(replaced, [1, 20, 3])

    def test_replace_all_no_occurrence(self):
        replaced = replace_all(self.sequence, 6, 60)
        self.assertEqual(replaced, self.sequence)

    def test_replace_all_empty_sequence(self):
        replaced = replace_all(self.empty_sequence, 1, 10)
        self.assertEqual(replaced, [])

    def test_replace_all_different_types(self):
        replaced = replace_all([1, '2', 3.0], '2', 20)
        self.assertEqual(replaced, [1, 20, 3.0])

    # Tests for remove_all
    def test_remove_all_multiple(self):
        removed = remove_all(self.sequence, 2)
        self.assertEqual(removed, [1, 3, 4, 5])

    def test_remove_all_single(self):
        removed = remove_all([1, 2, 3], 2)
        self.assertEqual(removed, [1, 3])

    def test_remove_all_no_occurrence(self):
        removed = remove_all(self.sequence, 6)
        self.assertEqual(removed, self.sequence)

    def test_remove_all_empty_sequence(self):
        removed = remove_all(self.empty_sequence, 1)
        self.assertEqual(removed, [])

    def test_remove_all_different_types(self):
        removed = remove_all([1, '2', 3.0, '2'], '2')
        self.assertEqual(removed, [1, 3.0])

    # Tests for find_all
    def test_find_all_multiple(self):
        found = find_all(self.sequence, 2)
        self.assertEqual(found, [2, 2, 2])

    def test_find_all_single(self):
        found = find_all([1, 2, 3], 2)
        self.assertEqual(found, [2])

    def test_find_all_no_occurrence(self):
        found = find_all(self.sequence, 6)
        self.assertEqual(found, [])

    def test_find_all_empty_sequence(self):
        found = find_all(self.empty_sequence, 1)
        self.assertEqual(found, [])

    def test_find_all_different_types(self):
        mixed_sequence = [1, '2', 3.0, '2']
        found = find_all(mixed_sequence, '2')
        self.assertEqual(found, ['2', '2'])
        found = find_all(mixed_sequence, 3.0)
        self.assertEqual(found, [3.0])

class TestComplexTypeValidator(unittest.TestCase):
    # Tests for simple type validation
    def test_validate_simple_type_correct(self):
        validator = ComplexTypeValidator(5, int)
        self.assertTrue(validator.validate())

    def test_validate_simple_type_incorrect(self):
        validator = ComplexTypeValidator(5, str)
        self.assertFalse(validator.validate())

    # Tests for list type validation
    def test_validate_list_correct(self):
        validator = ComplexTypeValidator([1, 2, 3], list[int])
        self.assertTrue(validator.validate())

    def test_validate_list_incorrect_element_type(self):
        validator = ComplexTypeValidator([1, '2', 3], list[int])
        self.assertFalse(validator.validate())

    def test_validate_list_incorrect_structure(self):
        validator = ComplexTypeValidator(123, list[int])
        self.assertFalse(validator.validate())

    # Tests for dict type validation
    def test_validate_dict_correct(self):
        validator = ComplexTypeValidator({'a': 1, 'b': 2}, {str: int})
        self.assertTrue(validator.validate())

    def test_validate_dict_incorrect_key_type(self):
        validator = ComplexTypeValidator({1: 'a', 2: 'b'}, {str: str})
        self.assertFalse(validator.validate())

    def test_validate_dict_incorrect_value_type(self):
        validator = ComplexTypeValidator({'a': 1, 'b': '2'}, {str: int})
        self.assertFalse(validator.validate())

    def test_validate_dict_incorrect_structure(self):
        validator = ComplexTypeValidator(['a', 'b'], {str: int})
        self.assertFalse(validator.validate())

    # Tests for set type validation
    def test_validate_set_correct(self):
        validator = ComplexTypeValidator({1, 2, 3}, set[int])
        self.assertTrue(validator.validate())

    def test_validate_set_incorrect_element_type(self):
        validator = ComplexTypeValidator({1, '2', 3}, set[int])
        self.assertFalse(validator.validate())

    def test_validate_set_incorrect_structure(self):
        validator = ComplexTypeValidator([1, 2, 3], set[int])
        self.assertFalse(validator.validate())

    # Tests for tuple type validation
    def test_validate_tuple_correct(self):
        validator = ComplexTypeValidator((1, 'a'), (int, str))
        self.assertTrue(validator.validate())

    def test_validate_tuple_incorrect_element_type(self):
        validator = ComplexTypeValidator((1, 2), (int, str))
        self.assertFalse(validator.validate())

    def test_validate_tuple_incorrect_length(self):
        validator = ComplexTypeValidator((1,), (int, str))
        self.assertFalse(validator.validate())

    def test_validate_tuple_incorrect_structure(self):
        validator = ComplexTypeValidator([1, 'a'], (int, str))
        self.assertFalse(validator.validate())

    # Tests for unsupported expected_type
    def test_validate_unsupported_type(self):
        validator = ComplexTypeValidator(5, float)
        self.assertFalse(validator.validate())

class TestConstant(unittest.TestCase):
    def setUp(self):
        self.const = Constant(a=1, b='test')

    def test_constant_initialization(self):
        self.assertEqual(self.const.a, 1)
        self.assertEqual(self.const.b, 'test')

    def test_constant_immutable_setattr(self):
        with self.assertRaises(AttributeError):
            self.const.a = 10

    def test_constant_immutable_delattr(self):
        with self.assertRaises(AttributeError):
            del self.const.a

    def test_constant_equality(self):
        const1 = Constant(a=1, b='test')
        const2 = Constant(a=1, b='test')
        const3 = Constant(a=2, b='test')
        self.assertEqual(const1, const2)
        self.assertNotEqual(const1, const3)

    def test_constant_ordering(self):
        const1 = Constant(a=1, b='apple')
        const2 = Constant(a=2, b='banana')
        const3 = Constant(a=1, b='apple')
        self.assertLess(const1, const2)
        self.assertGreater(const2, const1)
        self.assertEqual(const1, const3)

    def test_constant_str_repr(self):
        self.assertEqual(str(self.const), "{'a': 1, 'b': 'test'}")
        self.assertEqual(repr(self.const), "{'a': 1, 'b': 'test'}")

class TestPointer(unittest.TestCase):
    def setUp(self):
        self.ptr = Pointer(10)
        self.other_ptr = Pointer(20)

    def test_pointer_initialization(self):
        self.assertEqual(self.ptr.get(), 10)
        self.assertEqual(self.other_ptr.get(), 20)

    def test_pointer_set(self):
        self.ptr.set(30)
        self.assertEqual(self.ptr.get(), 30)

    def test_pointer_address(self):
        addr1 = self.ptr.address()
        addr2 = self.ptr.address()
        self.assertEqual(addr1, addr2)
        self.assertNotEqual(addr1, self.other_ptr.address())

    def test_pointer_point_to(self):
        self.ptr.point_to(self.other_ptr)
        self.assertEqual(self.ptr.get(), 20)
        self.ptr.set(25)
        self.assertEqual(self.other_ptr.get(), 25)

    def test_pointer_point_to_invalid(self):
        with self.assertRaises(TypeError):
            self.ptr.point_to(100)  # Not a Pointer instance

    def test_pointer_is_null(self):
        null_ptr = Pointer(None)
        self.assertTrue(null_ptr.is_null())
        self.assertFalse(self.ptr.is_null())

    def test_pointer_str_repr(self):
        ptr_str = str(self.ptr)
        self.assertIn("Pointer(value=10, address=", ptr_str)
        self.assertEqual(repr(self.ptr), ptr_str)

    def test_pointer_delete(self):
        del self.ptr
        # After deletion, we can't access self.ptr, so we skip testing internal state

    def test_pointer_ordering(self):
        ptr1 = Pointer(10)
        ptr2 = Pointer(20)
        ptr3 = Pointer(10)
        self.assertLess(ptr1, ptr2)
        self.assertGreater(ptr2, ptr1)
        self.assertEqual(ptr1, ptr3)

class TestCaseInsensitiveDict(unittest.TestCase):
    def setUp(self):
        self.cid = CaseInsensitiveDict({'Key1': 'value1', 'KEY2': 'value2'})
        self.empty_cid = CaseInsensitiveDict()

    def test_set_and_get_item(self):
        self.cid['Key3'] = 'value3'
        self.assertEqual(self.cid['key3'], 'value3')
        self.assertEqual(self.cid['KEY3'], 'value3')

    def test_get_item_case_insensitive(self):
        self.assertEqual(self.cid['key1'], 'value1')
        self.assertEqual(self.cid['KEY1'], 'value1')

    def test_del_item_case_insensitive(self):
        del self.cid['KEY1']
        self.assertNotIn('key1', self.cid)

    def test_iter_keys(self):
        keys = list(self.cid)
        self.assertIn('Key1', keys)
        self.assertIn('KEY2', keys)

    def test_len(self):
        self.assertEqual(len(self.cid), 2)
        self.cid['Key3'] = 'value3'
        self.assertEqual(len(self.cid), 3)

    def test_contains(self):
        self.assertIn('key1', self.cid)
        self.assertIn('KEY2', self.cid)
        self.assertNotIn('key3', self.cid)

    def test_eq(self):
        c1 = CaseInsensitiveDict({'key1': 'value1', 'key2': 'value2'})
        c2 = CaseInsensitiveDict({'key1': 'Value1', 'key2': 'value2'})
        self.assertEqual(c1, c2)

    def test_lower_keys(self):
        lower_keys = list(self.cid.lower_keys())
        self.assertIn('Key1', lower_keys)
        self.assertIn('KEY2', lower_keys)

    def test_lower_items(self):
        lower_items = list(self.cid.lower_items())
        self.assertIn(('key1', 'value1'), lower_items)
        self.assertIn(('key2', 'value2'), lower_items)

    def test_copy(self):
        copy_cid = self.cid.copy()
        self.assertEqual(copy_cid, self.cid)
        copy_cid['Key3'] = 'value3'
        self.assertNotEqual(copy_cid, self.cid)

    def test_repr(self):
        self.assertEqual(repr(self.cid), "{'Key1': 'value1', 'KEY2': 'value2'}")

    # noinspection PyTypeChecker
    def test_empty_case_insensitive_dict(self):
        self.assertEqual(len(self.empty_cid), 0)
        self.assertEqual(list(self.empty_cid), [])
        self.empty_cid['newKey'] = 'newValue'
        self.assertEqual(self.empty_cid['NEWKEY'], 'newValue')

# class TestLookupDict(unittest.TestCase):
#     def setUp(self):
#         self.ld = LookupDict(name="TestLookup")
#         self.ld['key1'] = 'value1'  # These assignments affect __dict__
#         self.ld.__dict__['key2'] = 'value2'
#
#     def test_initialization(self):
#         self.assertEqual(self.ld.name, "TestLookup")
#         self.assertEqual(self.ld.get('key1'), 'value1')
#         self.assertEqual(self.ld.get('key2'), 'value2')
#         self.assertIsNone(self.ld.get('key3'))
#
#     def test_getitem_existing(self):
#         self.assertEqual(self.ld['key1'], 'value1')
#         self.assertEqual(self.ld['key2'], 'value2')
#
#     def test_getitem_non_existing(self):
#         with self.assertRaises(KeyError):
#             _ = self.ld['key3']
#
#     def test_get_method(self):
#         self.assertEqual(self.ld.get('key1'), 'value1')
#         self.assertEqual(self.ld.get('key3', 'default'), 'default')
#
#     def test_repr(self):
#         self.assertEqual(repr(self.ld), "<lookup 'TestLookup'>")
#
#     def test_setitem_affects_dict(self):
#         self.ld['key3'] = 'value3'
#         self.assertEqual(self.ld.get('key3'), 'value3')
#
#     def test_update_lookup_dict(self):
#         self.ld.update({'key4': 'value4'})
#         self.assertEqual(self.ld.get('key4'), 'value4')
#
#     def test_lookup_dict_as_dict(self):
#         # Since LookupDict inherits from dict but overrides __getitem__,
#         # ensure that standard dict methods behave as expected.
#         self.assertEqual(dict(self.ld), {})
#         self.ld['key5'] = 'value5'
#         self.assertEqual(dict(self.ld), {})
#         # Access via __dict__
#         self.assertEqual(self.ld.get('key5'), 'value5')

# -------------------------
# Run the Tests
# -------------------------

if __name__ == '__main__':
    unittest.main()
