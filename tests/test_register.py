import pytest
from register.register import _has_slice, _matches, _resolve, Selection
from register import Register, NumKey, Dimension


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
        assert repr(idx_space) == f"IndexSpace({k}, 0 entries)"

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

    def test_agg_sum(self):
        assert self.reg[self.k][self.dim,][:,].agg(Register.SUM) == 6.0

    def test_agg_mean(self):
        assert self.reg[self.k][self.dim,][:,].agg(Register.MEAN) == 2.0

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


class TestSelect:
    def test_select_all(self):
        reg = Register()
        k = NumKey(1, "a", "A", int)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10
        reg[k][dim,][2,] = 20
        indices = list(reg.select(k, (dim,)))
        assert (1,) in indices
        assert (2,) in indices

    def test_select_with_target(self):
        reg = Register()
        k = NumKey(1, "a", "A", int)
        dim = Dimension("loc", "地点", "L")
        reg[k][dim,][1,] = 10
        reg[k][dim,][2,] = 20
        indices = list(reg.select(k, (dim,), target=(1,)))
        assert indices == [(1,)]

    def test_select_with_none_wildcard(self):
        reg = Register()
        k = NumKey(1, "a", "A", int)
        d1 = Dimension("loc", "地点", "L")
        d2 = Dimension("owner", "所有者", "N")
        reg[k][d1, d2][1, 1] = 10
        reg[k][d1, d2][1, 2] = 20
        reg[k][d1, d2][2, 1] = 30
        indices = list(reg.select(k, (d1, d2), target=(1, None)))
        assert (1, 1) in indices
        assert (1, 2) in indices
        assert (2, 1) not in indices


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
