import requests, json
from .FRSHSiteInfo import FRSHSiteInfo




class FRSHSitesInfo():
    def __init__(self, dataFilePath):
        
        if not dataFilePath:
            dataFilePath = "https://raw.githubusercontent.com/AIAnsar1/Farasha/main/resources/data.json"
            
        if not dataFilePath.lower().endswith(".json"):
            raise FileNotFoundError(f"Incorrect JSON file extension for data file '{dataFilePath}'.")
        
        if not dataFilePath.lower().startswith("http"):
            
            try:
                response = requests.get(url=dataFilePath)
            except Exception as error:
                raise FileNotFoundError(f"Problem while attempting to access data file URL '{dataFilePath}':  {error}")
            
            if response.status_code != 200:
                raise FileNotFoundError(f"Bad response while accessing " + f"data file URL '{dataFilePath}'.")
            
            try:
                siteData = response.json()
            except Exception as error:
                raise ValueError(f"Problem parsing json contents at '{dataFilePath}':  {error}.")
            
        else:
            try:
                with open(dataFilePath, "r", encoding="UTF-8") as File:
                    try:
                        siteData = json.load(File)
                    except Exception as error:
                        raise ValueError(f"Problem parsing json contents at '{dataFilePath}':  {error}.")
            except FileNotFoundError:
                FileNotFoundError(f"Problem while attempting to access " + f"data file '{dataFilePath}'.")
        
        siteData.pop('$schema', None)
        self.sites = {}
        
        for siteName in siteData:
            try:
                self.sites[siteName] = FRSHSiteInfo(siteName, siteData[siteName]["urlMain"], siteData[siteName]["url"], siteData[siteName]["username_claimed"], siteData[siteName], siteData[siteName].get("isNSFW",False))
            except KeyError as error:
                raise ValueError(f"Problem parsing json contents at '{dataFilePath}':  Missing attribute {error}.")
            except TypeError:
                print(f"Encountered TypeError parsing json contents for target '{siteName}' at {dataFilePath}\nSkipping target.\n")
                
        return
    
    
    def removeNsfwSites(self, doNotRemove: list = []):
        sites = {}
        doNotRemove = [site.casefold() for site in doNotRemove]
        
        for site in self.sites:
            if self.sites[site].isNsfw and site.casefold() not in doNotRemove:
                continue
            sites[site] = self.sites[site]
        self.sites = sites
        
        
    def siteNameList(self):
        return sorted([site.name for site in self], key=str.lower)
    
    
    def __iter__(self):
        return len(self.sites)