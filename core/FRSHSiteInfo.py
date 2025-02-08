import secrets


class FRSHSiteInformation:
    def __init__(self, name, url_home, url_username_format, username_claimed, information, is_nsfw, username_unclaimed=secrets.token_urlsafe(10)):
        self.name = name
        self.url_home = url_home
        self.url_username_format = url_username_format
        self.username_claimed = username_claimed
        self.username_unclaimed = secrets.token_urlsafe(32)
        self.information = information
        self.is_nsfw  = is_nsfw

        return

    def __str__(self):
        return f"{self.name} ({self.url_home})"