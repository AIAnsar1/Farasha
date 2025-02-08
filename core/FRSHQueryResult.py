


class FRSHQueryResult():
    def __init__(self, username, site_name, site_url_user, status, query_time=None, context=None):
        self.username      = username
        self.site_name     = site_name
        self.site_url_user = site_url_user
        self.status        = status
        self.query_time    = query_time
        self.context       = context

        return

    def __str__(self):
        status = str(self.status)
        if self.context is not None:
            status += f" ({self.context})"
        return status