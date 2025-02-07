from enum import Enum


class FRSHQueryStatus(Enum):
    CLAIMED = "Claimed"
    AVIALABLE = "Avialable"
    UNKNOWN = "Unknown"
    ILLEGAL = "Illegal"
    WAF = "WAF"
    
    def __str__(self):
        return self.value