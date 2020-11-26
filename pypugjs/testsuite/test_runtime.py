from pypugjs import runtime


class TestIteration(object):
    def test_it_returns_mappings_unaltered(self):
        mapping = {}
        assert runtime.iteration(mapping, 1) is mapping

    def test_it_returns_empty_list_on_empty_input(self):
        test_list = iter([])
        assert list(runtime.iteration(test_list, 1)) == []

    def test_it_iterates_as_is_if_numkeys_is_same_as_cardinality(self):
        test_list = [(1, 2), (3, 4)]
        assert list(runtime.iteration(test_list, 2)) == test_list

    def test_it_extends_with_index_if_items_are_iterable(self):
        test_list = [('a',), ('b',)]
        assert list(runtime.iteration(test_list, 2)) == [('a', 0), ('b', 1)]

    def test_it_adds_index_if_items_are_strings(self):
        test_list = ['a', 'b']
        assert list(runtime.iteration(test_list, 2)) == [('a', 0), ('b', 1)]

    def test_it_adds_index_if_items_are_non_iterable(self):
        test_list = [1, 2]
        assert list(runtime.iteration(test_list, 2)) == [(1, 0), (2, 1)]

    def test_it_doesnt_swallow_first_item_of_iterators(self):
        test_list = [1, 2]
        iterator = iter(test_list)
        assert list(runtime.iteration(iterator, 1)) == test_list

    def test_nested_empty_array_with_single_key(self):
        test_list = [[]]
        assert list(runtime.iteration(test_list, 1)) == test_list
