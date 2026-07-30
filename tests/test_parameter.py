from or_register.key import NumKey, StrKey
from or_register.parameter import Code, Id, Name


class TestId:
    def test_is_num_key(self):
        assert isinstance(Id, NumKey)

    def test_id(self):
        assert Id.id == 1

    def test_name(self):
        assert Id.name == "Id"

    def test_vtype(self):
        assert Id.vtype is int


class TestCode:
    def test_is_str_key(self):
        assert isinstance(Code, StrKey)

    def test_id(self):
        assert Code.id == 2

    def test_name(self):
        assert Code.name == "Code"


class TestName:
    def test_is_str_key(self):
        assert isinstance(Name, StrKey)

    def test_id(self):
        assert Name.id == 3

    def test_name(self):
        assert Name.name == "Name"
