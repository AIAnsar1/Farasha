import secrets


class FRSHSiteInfo:
    def __init__(self, name, urlHome, urlUsernameFormat, usernameClaimed, information, isNsfw, usernameUnclaimed=secrets.token_urlsafe(10)):
        self.name = name
        self.urlHome = urlHome
        self.urlUsernameFormat = urlUsernameFormat
        self.usernameClaimed = usernameClaimed
        self.information = information
        self.isNsfw = isNsfw
        self.usernameUnclaimed = usernameUnclaimed.token_urlsafe(10)
        
        return
    
    
    def __str__(self):
        return f"{self.name} ({self.urlHome})"