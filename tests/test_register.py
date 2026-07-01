from register.register import _has_slice, _matches, _resolve
from register import Register, NumKey, Dimension, Selection


class TestHasSlice:
    def test_all_ints(self):
        assert _has_slice((1, 2, 3)) is False

    def test_with_slice(self):
        assert _has_slice((1, slice(None))) is True

    def test_with_list(self):
        assert _has_slice((1, [1, 2])) is True

    def test_non_tuple(self):
        assert _has_slice(1) is False

    def test_non_tuple_slice(self):
        assert _has_slice(slice(None)) is True


class TestMatches:
    def test_exact_match(self):
        assert _matches((1, 2), (1, 2)) is True

    def test_exact_no_match(self):
        assert _matches((1, 3), (1, 2)) is False

    def test_list_match(self):
        assert _matches((1, 2), (1, [2, 3])) is True

    def test_list_no_match(self):
        assert _matches((1, 5), (1, [2, 3])) is False

    def test_slice_all(self):
        assert _matches((1, 2), (slice(None), slice(None))) is True

    def test_slice_range_match(self):
        assert _matches((2, 1), (slice(1, 3), slice(None))) is True

    def test_slice_range_no_match(self):
        assert _matches((3, 1), (slice(1, 3), slice(None))) is False

    def test_slice_start_no_match(self):
        assert _matches((0, 1), (slice(1, 3), slice(None))) is False

    def test_slice_start_only(self):
        assert _matches((5, 1), (slice(3, None), slice(None))) is True

    def test_slice_stop_only(self):
        assert _matches((2, 1), (slice(None, 3), slice(None))) is True


class TestResolve:
    def test_all(self):
        data = {(1, 1): "a", (1, 2): "b", (2, 1): "c"}
        result = _resolve((slice(None), slice(None)), data)
        assert result == data

    def test_exact_first(self):
        data = {(1, 1): "a", (1, 2): "b", (2, 1): "c"}
        result = _resolve((1, slice(None)), data)
        assert result == {(1, 1): "a", (1, 2): "b"}

    def test_list_second(self):
        data = {(1, 1): "a", (1, 2): "b", (2, 1): "c"}
        result = _resolve((slice(None), [1]), data)
        assert result == {(1, 1): "a", (2, 1): "c"}


class TestRegister:
    def test_empty(self):
        reg = Register()
        assert repr(reg) == "Register(empty)"

    def test_getitem_auto_init(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        kv = reg[k]
        assert repr(kv) == f"KeyView({k}, empty)"

    def test_contains(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        assert k not in reg
        reg[k]  # auto-init
        assert k in reg

    def test_assign_and_get(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert reg[k][dim,][1,] == 10.0

    def test_repr(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert "params=1" in repr(reg)
        assert "cells=1" in repr(reg)


class TestKeyView:
    def test_getitem_auto_init(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        idx_space = reg[k][dim,]
        assert repr(idx_space) == f"IndexSpace({k}, ({dim!r}), 0 entries)"

    def test_repr_with_data(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        result = repr(reg[k])
        assert f"KeyView({k}" in result
        assert "loc" in result
        assert "2" in result

    def test_iter(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1,][1,] = 1.0
        reg[k][d2,][1,] = 2.0
        dims = list(reg[k])
        assert (d1,) in dims
        assert (d2,) in dims

    def test_pop(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        popped = reg[k].pop((dim,))
        assert popped == {(1,): 10.0}
        assert (dim,) not in list(reg[k])


class TestIndexSpace:
    def test_exact_getset(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert reg[k][dim,][1,] == 10.0

    def test_contains(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        assert (1,) in reg[k][dim,]
        assert (2,) not in reg[k][dim,]

    def test_slice_returns_selection(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        sel = reg[k][dim,][:,]
        assert isinstance(sel, Selection)

    def test_update(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,].update({(1,): 10.0, (2,): 20.0})
        assert reg[k][dim,][1,] == 10.0
        assert reg[k][dim,][2,] == 20.0

    def test_keys(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        keys = reg[k][dim,].keys()
        assert (1,) in keys
        assert (2,) in keys
        assert len(keys) == 2

    def test_values(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        values = list(reg[k][dim,].values())
        assert 10.0 in values
        assert 20.0 in values
        assert len(values) == 2

    def test_all(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 1.0
        reg[k][d1, d2][1, 2] = 2.0
        reg[k][d1, d2][2, 1] = 3.0
        sel = reg[k][d1, d2].all
        assert isinstance(sel, Selection)
        assert sel.sum() == 6.0

    def test_first(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        idx, val = reg[k][dim,].first
        assert idx == (1,)
        assert val == 10.0

    def test_len(self):
        reg = Register()
        k = NumKey(1, "amount", "件量")
        dim = Dimension("loc", "地点", "L")
        assert len(reg[k][dim,]) == 0
        reg[k][dim,][1,] = 10.0
        reg[k][dim,][2,] = 20.0
        assert len(reg[k][dim,]) == 2


class TestSelection:
    def setup_method(self):
        self.reg = Register()
        self.k = NumKey(1, "amount", "件量", float)
        self.dim = Dimension("loc", "地点", "L")
        self.reg[self.k][self.dim,][1,] = 1.0
        self.reg[self.k][self.dim,][2,] = 2.0
        self.reg[self.k][self.dim,][3,] = 3.0

    def test_sum(self):
        assert self.reg[self.k][self.dim,][:,].sum() == 6.0

    def test_mean(self):
        assert self.reg[self.k][self.dim,][:,].mean() == 2.0

    def test_min(self):
        assert self.reg[self.k][self.dim,][:,].min() == 1.0

    def test_max(self):
        assert self.reg[self.k][self.dim,][:,].max() == 3.0

    def test_range(self):
        assert self.reg[self.k][self.dim,][:,].range() == 2.0

    def test_partial_slice(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 1.0
        reg[k][d1, d2][1, 2] = 2.0
        reg[k][d1, d2][2, 1] = 3.0
        reg[k][d1, d2][2, 2] = 4.0
        assert reg[k][d1, d2][1, :].sum() == 3.0
        assert reg[k][d1, d2][2, :].sum() == 7.0

    def test_list_selector(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 1.0
        reg[k][d1, d2][1, 2] = 2.0
        reg[k][d1, d2][2, 1] = 3.0
        reg[k][d1, d2][2, 2] = 4.0
        reg[k][d1, d2][2, 3] = 5.0
        assert reg[k][d1, d2][2, [1, 2]].sum() == 7.0

    def test_proxy_delegable_method(self):
        """@delegable method is callable through Selection."""
        assert self.reg[self.k][self.dim,][:,].sum() == 6.0

    def test_proxy_non_delegable_raises(self):
        """Calling a non-@delegable method raises AttributeError."""
        import pytest
        sel = self.reg[self.k][self.dim,][:,]
        with pytest.raises(AttributeError, match="has no delegable method"):
            sel.validate()

    def test_proxy_undefined_raises(self):
        """Calling a nonexistent method raises AttributeError."""
        import pytest
        sel = self.reg[self.k][self.dim,][:,]
        with pytest.raises(AttributeError, match="has no delegable method"):
            sel.nonexistent_method()

    def test_proxy_private_raises(self):
        """Accessing _-prefixed attributes raises AttributeError."""
        import pytest
        sel = self.reg[self.k][self.dim,][:,]
        with pytest.raises(AttributeError):
            sel._private_method()

    def test_proxy_concrete_kwargs(self):
        """Delegable method works with proxy — kwargs passed through."""
        from register.key import _BaseKey, delegable, Selected
        from register import Dimension
        from typing import Any

        class MockKey(_BaseKey):
            @delegable
            def weighted_sum(self, selected: Selected, *, weight: float = 1.0) -> float:
                return sum(selected.values()) * weight

        reg = Register()
        mk = MockKey(99, "mock", "模拟")
        dim = Dimension("loc", "地点", "L")
        reg[mk][dim,][1,] = 2.0
        reg[mk][dim,][2,] = 3.0
        sel = reg[mk][dim,][:,]
        assert sel.weighted_sum() == 5.0
        assert sel.weighted_sum(weight=2.0) == 10.0

    def test_selection_repr(self):
        """Selection repr shows key, dims, and entry count."""
        sel = self.reg[self.k][self.dim,][:,]
        r = repr(sel)
        assert "Selection" in r
        assert "3 entries" in r


class TestValidate:
    def test_validate_returns_register(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        reg[k][dim,][2,] = 2.0
        result = reg.validate()
        assert isinstance(result, Register)

    def test_validate_all_valid(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        reg[k][dim,][2,] = 2.0
        result = reg.validate()
        assert result[k][dim,][1,] is True
        assert result[k][dim,][2,] is True

    def test_validate_some_invalid(self):
        reg = Register()
        k = NumKey(1, "amount", "件量", float)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 1.0
        reg[k][dim,][2,] = "bad"
        result = reg.validate()
        assert result[k][dim,][1,] is True
        assert result[k][dim,][2,] is False
