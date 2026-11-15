from enum import Enum

# 1. two numbers MainEntity
# 2. two numbers SubEntity
# 3. Last three are for count
#
# 20xxxxx (auth) and 90xxxxx (system) are shared by all iZero services,
# keep their values identical to the iZero auth service.

class MessageId(int, Enum):
    AUTH_NOT_AUTHENTICATED = 2000001
    AUTH_NOT_AUTHORIZED = 2000002
    PRINT_INVALID_DATA = 3000001
    PRINT_TEMPLATE_FILLING_FAILED = 3000002
    PRINT_RENDERING_FAILED = 3000003
    SYSTEM_INTERNAL_FAIL = 9000001
