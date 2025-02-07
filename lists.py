#!/usr/bin/env python


import os, json



DATA_REL_URI: str = "resources/data.json"


with open(DATA_REL_URI, "r", encoding="UTF-8") as dataF:
    data: dict = json.load(dataF)
    


socmed: dict = dict(data)
socmed.pop('$schema', None)
socmed: list = sorted(socmed.items())
os.mkdir("output")


with open("output/sites.mdx", "w") as siteF:
    siteF.write("---\ntitle: 'List of supported sites'\nsidebarTitle: 'Supported sites'\nicon: 'globe'\ndescription: 'Sherlock currently supports **400+** sites'\n---\n\n")
    
    for social, info in socmed:
        url = info["urlMain"]
        nsfw = "**(NSFW)**" if info.get("isNSFW") else ""
        siteF.write(f"1. [{social}]({url}) {nsfw}\n")
        
with open(DATA_REL_URI, "w") as dataF:
    sortedD = json.dumps(data, indent=2, sort_keys=True)
    dataF.write(sortedD)
    dataF.write("\n")
    
    
print("[ INFO ]: Finished Updating Supported Site Listing...")