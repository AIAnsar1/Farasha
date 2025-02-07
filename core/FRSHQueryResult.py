


class FRSHQueryResult():
    def __init__(self, Username, SiteName, SiteUrlUser, Status, QueryTime=None, Context=None):
        self.Username = Username
        self.SiteName = SiteName
        self.SiteUrlUser = SiteUrlUser
        self.Status = Status
        self.QueryTime = QueryTime
        self.Context = Context
        
        
    def __str__(self):
        Status = str(self.Status)
        
        if self.Context is not None:
            Status += f" ({self.Context})"
        return Status