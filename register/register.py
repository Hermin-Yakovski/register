import logging
from collections import defaultdict
from typing import Any, Generator, Generic, Iterator, TypeVar, get_args, get_origin

import pandas as pd

from .dimension import Dimension, Index
from .exception import DimensionError, ValidationError
from .parameter import Parameter

K = TypeVar("K", bound=Parameter)

logger = logging.getLogger("register")


class Method(int):
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return False
        return int(self) == int(other)

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, Method):
            return True
        return int(self) != int(other)

    def __hash__(self) -> int:
        return super().__hash__()


class DimensionAsKey:
    _data: dict[tuple[Any, ...], dict[tuple[int, ...], Any]]

    def __init__(self) -> None:
        self._data = defaultdict(dict)

    def __getitem__(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data[key]

    def __iter__(self) -> Iterator[tuple[Any, ...]]:
        return iter(self._data)

    def pop(self, key: tuple[Any, ...]) -> dict[tuple[int, ...], Any]:
        return self._data.pop(key, {})


class Register(Generic[K]):
    ALL: Method = Method(0)
    SUM: Method = Method(1)
    MAX: Method = Method(2)
    MIN: Method = Method(3)
    RANGE: Method = Method(4)
    _data: dict[K, DimensionAsKey]

    def __init__(self) -> None:
        self._data = defaultdict(DimensionAsKey)

    def __getitem__(self, key: K) -> DimensionAsKey:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def select(
        self,
        key: K,
        dimension: tuple[Dimension, ...],
        target: tuple[int, ...] | None = None,
    ) -> Generator[tuple[int, ...], None, None]:
        for index in self._data[key][dimension]:
            if target is None:
                yield index
            elif all(self.ALL == j or i == j for i, j in zip(index, target)):
                yield index

    def as_frames(self, display_cn: bool = False) -> dict[tuple[Dimension, ...], pd.DataFrame]:
        frames: dict[tuple[Dimension, ...], pd.DataFrame] = {}
        rows: dict[tuple[Dimension, ...], dict[tuple[int, ...], list[Any]]] = {}
        columns: dict[tuple[Dimension, ...], list[str]] = {}

        for key in self._data:
            col: str = key.name_cn if display_cn else key.name
            for dimension in self._data[key]:
                if dimension not in rows:
                    rows[dimension] = {}
                    columns[dimension] = []
                if col not in columns[dimension]:
                    for index in rows[dimension]:
                        rows[dimension][index].append(None)
                    columns[dimension].append(col)
                for index, value in self._data[key][dimension].items():
                    if index not in rows[dimension]:
                        rows[dimension][index] = [None for _ in columns[dimension]]
                    rows[dimension][index][-1] = value

        for dimension in columns:
            dataframe_columns: list[str] = [
                d.name_cn if display_cn else d.name for d in dimension
            ] + columns[dimension]
            dataframe_rows: list[list[Any]] = []
            for index in rows[dimension]:
                dataframe_rows.append([i for i in index] + rows[dimension][index])
            frames[dimension] = pd.DataFrame(dataframe_rows, columns=dataframe_columns)

        return frames

    def validate(self, dim: DimensionAsKey, raise_errors: bool = False) -> None:
        for key in self._data:
            for dimension in self._data[key]:
                for index in self._data[key][dimension]:
                    # Validate index
                    for d, ix in zip(dimension, index):
                        if not ((ix,) in dim[d,] or isinstance(ix, Method) or d == Index):
                            msg = (
                                f"[v{key.id}] {key}{dimension}{index}: "
                                f"index {ix} does not match any index of dimension {d.name}"
                            )
                            if raise_errors:
                                raise DimensionError(msg)
                            logger.warning(msg)

                    value = self._data[key][dimension][index]
                    if key.vtype is Any:
                        pass

                    elif get_origin(key.vtype) in [list, set, tuple]:
                        # value -> iterable
                        origin = get_origin(key.vtype)
                        if origin is not None and not isinstance(value, origin):
                            msg = (
                                f"[v{key.id}] {key}{dimension}{index}: "
                                f"expected {origin}, got {type(value)}, value={value}"
                            )
                            if raise_errors:
                                raise ValidationError(msg)
                            logger.warning(msg)

                        arg = get_args(key.vtype)[0]
                        if get_args(arg):
                            arg = get_args(arg)[0]

                        for v in value:
                            if isinstance(arg, Dimension):
                                if (v,) not in dim[arg,]:
                                    msg = (
                                        f"[v{key.id}] {key}{dimension}{index}: "
                                        f"value {v} does not match any index of dimension {arg.name}"
                                    )
                                    if raise_errors:
                                        raise ValidationError(msg)
                                    logger.warning(msg)
                            elif not isinstance(v, arg):
                                msg = (
                                    f"[v{key.id}] {key}{dimension}{index}: "
                                    f"{get_origin(key.vtype)} expected elements of {arg}, "
                                    f"got {type(v)}, value={v}"
                                )
                                if raise_errors:
                                    raise ValidationError(msg)
                                logger.warning(msg)

                    elif isinstance(key.vtype, Dimension):
                        if (value,) not in dim[key.vtype,]:
                            msg = (
                                f"[v{key.id}] {key}{dimension}{index}: "
                                f"value {value} does not match any index of dimension {key.vtype.name}"
                            )
                            if raise_errors:
                                raise ValidationError(msg)
                            logger.warning(msg)

                    elif not isinstance(value, key.vtype):
                        msg = (
                            f"[v{key.id}] {key}{dimension}{index}: "
                            f"expected {key.vtype}, got {type(value)}, value={value}"
                        )
                        if raise_errors:
                            raise ValidationError(msg)
                        logger.warning(msg)
