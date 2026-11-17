from enum import Enum

# 1. two numbers MainEntity
# 2. two numbers SubEntity
# 3. Last three are for count
#
# 90xxxxx (system) is shared by all iZero services, keep its values
# identical to the iZero auth service.

class MessageId(int, Enum):
    PRINT_INVALID_DATA = 3000001
    SYSTEM_INTERNAL_FAIL = 9000001
