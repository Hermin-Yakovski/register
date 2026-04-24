class Dimension:
    _name: str
    _name_cn: str
    _sign: str

    def __init__(self, name: str, name_cn: str, sign: str) -> None:
        self._name = name
        self._name_cn = name_cn
        self._sign = sign

    def __str__(self) -> str:
        return self._sign

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash(self._sign)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Dimension) and (self._sign == other.sign)

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_cn(self) -> str:
        return self._name_cn

    @property
    def sign(self) -> str:
        return self._sign


Index = Dimension("Index", "下标", "IX")
Metric = Dimension("Metric", "指标汇总", "MTC")
