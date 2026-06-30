from register import Register, Method
from key import ParameterKey
from dimension import Dimension

# dimension and parameter
Amount = ParameterKey(1, 'amount', '件量', float)
Location = Dimension('location', '地点', 'L')
Owner = Dimension('owner', '所有者', 'N')

# construct demo Register
reg = Register[ParameterKey]()
reg[Amount][Location, Owner,][1, 1,] = 1.1
reg[Amount][Location, Owner,][1, 2,] = 2.2
reg[Amount][Location, Owner,][2, 1,] = 3.3
reg[Amount][Location, Owner,][2, 2,] = 4.4
reg[Amount][Location, Owner,][2, 3,] = 5.5

# api
reg[Amount][Location, Owner,][:, :,].sum()    # = 16.5
reg[Amount][Location, Owner,][:, :,].agg(Register.SUM)    # alternatively use agg + method
reg[Amount][Location, Owner,][:, :,].agg(Register.SUM, **config)    # alternatively use agg + method + config
reg[Amount][Location, Owner,][1, :,].sum()    # = 3.3
reg[Amount][Location, Owner,][2, [1, 2],].sum()    # = 7.7
