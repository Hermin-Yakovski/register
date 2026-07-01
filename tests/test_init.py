import register


class TestExports:
    def test_register(self):
        assert hasattr(register, "Register")

    def test_method(self):
        assert not hasattr(register, "Method")

    def test_key_view(self):
        assert hasattr(register, "KeyView")

    def test_index_space(self):
        assert hasattr(register, "IndexSpace")

    def test_selection(self):
        assert hasattr(register, "Selection")

    def test_register_key(self):
        assert hasattr(register, "RegisterKey")

    def test_num_key(self):
        assert hasattr(register, "NumKey")

    def test_str_key(self):
        assert hasattr(register, "StrKey")

    def test_dimension_key(self):
        assert hasattr(register, "DimensionKey")

    def test_dimension_collection_key(self):
        assert hasattr(register, "DimensionCollectionKey")

    def test_no_parameter_key(self):
        assert not hasattr(register, "ParameterKey")

    def test_no_position_key(self):
        assert not hasattr(register, "PositionKey")

    def test_no_iterable_key(self):
        assert not hasattr(register, "IterableKey")

    def test_no_dimension_as_key(self):
        assert not hasattr(register, "DimensionAsKey")

    def test_all_exports(self):
        expected = {
            "Register", "KeyView", "IndexSpace", "Selection",
            "RegisterKey", "NumKey", "StrKey", "DimensionKey", "DimensionCollectionKey",
            "Dimension", "Index", "Metric",
            "Id", "Code", "Name",
            "RegisterError", "ValidationError", "DimensionError",
        }
        assert expected == set(register.__all__)
