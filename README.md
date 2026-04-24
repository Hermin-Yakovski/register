# Register

Multi-dimensional data registry with validation and pandas export.

## Installation

```bash
pip install register
```

## Quick Example

```python
from register import Register, Parameter, Dimension

# Define custom parameter and dimension
price = Parameter(4, 'price', '价格', float)
region = Dimension('region', '地区', 'REG')

# Use the register
reg = Register()
reg[price][(region,)][('Beijing',)] = 100.0

# Export to DataFrame
frames = reg.as_frames()
```

## License

See LICENSE file.
