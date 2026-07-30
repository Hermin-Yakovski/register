import or_register


class TestExports:
    def test_register(self):
        assert hasattr(or_register, "Register")

    def test_no_method(self):
        assert not hasattr(or_register, "Method")

    def test_key_view(self):
        assert hasattr(or_register, "KeyView")

    def test_index_space(self):
        assert hasattr(or_register, "IndexSpace")

    def test_selection(self):
        assert hasattr(or_register, "Selection")

    def test_register_key(self):
        assert hasattr(or_register, "RegisterKey")

    def test_num_key(self):
        assert hasattr(or_register, "NumKey")

    def test_str_key(self):
        assert hasattr(or_register, "StrKey")

    def test_dimension_key(self):
        assert hasattr(or_register, "DimensionKey")

    def test_dimension_collection_key(self):
        assert hasattr(or_register, "DimensionCollectionKey")

    def test_no_parameter_key(self):
        assert not hasattr(or_register, "ParameterKey")

    def test_no_position_key(self):
        assert not hasattr(or_register, "PositionKey")

    def test_no_iterable_key(self):
        assert not hasattr(or_register, "IterableKey")

    def test_no_dimension_as_key(self):
        assert not hasattr(or_register, "DimensionAsKey")

    def test_delegable(self):
        assert hasattr(or_register, "delegable")

    def test_selected(self):
        assert hasattr(or_register, "Selected")

    def test_all_exports(self):
        expected = {
            "Register",
            "KeyView",
            "IndexSpace",
            "Selection",
            "RegisterKey",
            "NumKey",
            "StrKey",
            "DimensionKey",
            "DimensionCollectionKey",
            "delegable",
            "Selected",
            "Dimension",
            "Index",
            "Metric",
            "Id",
            "Code",
            "Name",
            "RegisterError",
            "ValidationError",
            "DimensionError",
        }
        assert expected == set(or_register.__all__)
