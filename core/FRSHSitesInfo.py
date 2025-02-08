import requests, json
from .FRSHSiteInfo import FRSHSiteInformation




class FRSHSitesInformation:
    def __init__(self, data_file_path=None):
        if not data_file_path:
            data_file_path = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json"

        if not data_file_path.lower().endswith(".json"):
            raise FileNotFoundError(f"[ ERROR ]: Incorrect JSON file extension for data file '{data_file_path}'.")

        if data_file_path.lower().startswith("http"):
            try:
                response = requests.get(url=data_file_path)
            except Exception as error:
                raise FileNotFoundError(f"[ ERROR ]: Problem while attempting to access data file URL '{data_file_path}':  {error}")

            if response.status_code != 200:
                raise FileNotFoundError(f"[ ERROR ]: Bad response while accessing " f"data file URL '{data_file_path}'.")
            try:
                site_data = response.json()
            except Exception as error:
                raise ValueError( f"[ ERROR ]: Problem parsing json contents at '{data_file_path}':  {error}.")

        else:
            try:
                with open(data_file_path, "r", encoding="utf-8") as file:
                    try:
                        site_data = json.load(file)
                    except Exception as error:
                        raise ValueError(f"[ ERROR ]: Problem parsing json contents at '{data_file_path}':  {error}.")

            except FileNotFoundError:
                raise FileNotFoundError(f"[ ERROR ]: Problem while attempting to access " f"data file '{data_file_path}'.")
        
        site_data.pop('$schema', None)
        self.sites = {}
        
        for site_name in site_data:
            try:
                self.sites[site_name] = FRSHSiteInformation(site_name, site_data[site_name]["urlMain"], site_data[site_name]["url"], site_data[site_name]["username_claimed"], site_data[site_name], site_data[site_name].get("isNSFW",False))
            except KeyError as error:
                raise ValueError(f"[ ERROR ]: Problem parsing json contents at '{data_file_path}':  Missing attribute {error}.")
            except TypeError:
                print(f"[ ERROR ]: Encountered TypeError parsing json contents for target '{site_name}' at {data_file_path}\nSkipping target.\n")

        return

    def remove_nsfw_sites(self, do_not_remove: list = []):
        sites = {}
        do_not_remove = [site.casefold() for site in do_not_remove]
        for site in self.sites:
            if self.sites[site].is_nsfw and site.casefold() not in do_not_remove:
                continue
            sites[site] = self.sites[site]  
        self.sites =  sites

    def site_name_list(self):
        return sorted([site.name for site in self], key=str.lower)

    def __iter__(self):
        for site_name in self.sites:
            yield self.sites[site_name]

    def __len__(self):
        return len(self.sites)