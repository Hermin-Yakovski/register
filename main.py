import sys

from register import Register
from register.dimension import *
from register.parameter import *

if __name__ == "__main__":
    reg = Register()
    reg[Id][Index,][1,] = 1
    reg[Name][Index,][2,] = "x"

    sys.exit(0)
