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
reg[price][(region,)][('Shanghai',)] = 150.0

# Select data
for index in reg.select(price, (region,), ('Beijing',)):
    print(f"Price in Beijing: {reg[price][(region,)][index]}")

# Export to DataFrame
frames = reg.as_frames()
df = frames[(region,)]
print(df)
```

## API Reference

### Classes

- **Register**: Multi-dimensional data registry
- **Parameter**: Typed key with metadata (id, name, name_cn, vtype)
- **Dimension**: Defines a dimension for indexing

### Predefined Dimensions

- **Index**: Special dimension for row indices
- **Metric**: Dimension for metric aggregation

### Predefined Parameters

- **Id**: ID parameter (int)
- **Code**: Code parameter (str)
- **Name**: Name parameter (str)

## License

See LICENSE file.
