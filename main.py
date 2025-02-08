import sys, csv, signal, os, re, requests, pandas
from core.__init__ import __longname__, __shortname__, __version__, forge_api_latest_release
from argparse import ArgumentParser, RawDescriptionHelpFormatter, ArgumentTypeError
from json import loads
from colorama import init

from core.FRSHQueryStatus import FRSHQueryStatus
from core.FRSHQueryNotifyPrint import FRSHQueryNotifyPrint
from core.FRSHSitesInfo import FRSHSitesInfo
from core.Farasha import timeoutCheck, handler, checkForParameter, farasha, multipleUsername




def main():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description=f"{__longname__} (Version {__version__})")
    parser.add_argument("--version", action="version", version=f"{__shortname__} v{__version__}", help="Display version information and dependencies.")
    parser.add_argument("--verbose", "-v", "-d", "--debug", action="store_true",dest="verbose", default=False,help="Display extra debugging information and metrics.")
    parser.add_argument( "--folderoutput","-fo",dest="folderoutput", help="If using multiple usernames, the output of the results will be saved to this folder.", )
    parser.add_argument("--output","-o",dest="output",help="If using single username, the output of the result will be saved to this file.")
    parser.add_argument( "--tor","-t",action="store_true",dest="tor",default=False, help="Make requests over Tor; increases runtime; requires Tor to be installed and in system path." )
    parser.add_argument("--unique-tor","-u",action="store_true",dest="unique_tor",default=False,help="Make requests over Tor with new Tor circuit after each request; increases runtime; requires Tor to be installed and in system path.")
    parser.add_argument("--csv",action="store_true",dest="csv",default=False,help="Create Comma-Separated Values (CSV) File." )
    parser.add_argument( "--xlsx",action="store_true", dest="xlsx",default=False,help="Create the standard file for the modern Microsoft Excel spreadsheet (xlsx).", )
    parser.add_argument("--site",action="append",metavar="SITE_NAME",dest="site_list",default=[],help="Limit analysis to just the listed sites. Add multiple options to specify more than one site.",)
    parser.add_argument(  "--proxy",  "-p", metavar="PROXY_URL", action="store", dest="proxy", default=None,help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080")
    parser.add_argument(  "--dump-response",  action="store_true",  dest="dump_response",  default=False,  help="Dump the HTTP response to stdout for targeted debugging.")
    parser.add_argument(  "--json",  "-j",  metavar="JSON_FILE",  dest="json_file",  default=None,  help="Load data from a JSON file or an online, valid, JSON file. Upstream PR numbers also accepted.")
    parser.add_argument(  "--timeout",  action="store", metavar="TIMEOUT", dest="timeout", type=timeoutCheck, default=60, help="Time (in seconds) to wait for response to requests (Default: 60)")
    parser.add_argument( "--print-all", action="store_true", dest="print_all", default=False, help="Output sites where the username was not found.")
    parser.add_argument( "--print-found", action="store_true", dest="print_found", default=True, help="Output sites where the username was found (also if exported as file).")
    parser.add_argument( "--no-color", action="store_true", dest="no_color", default=False,  help="Don't color terminal output")
    parser.add_argument( "username", nargs="+", metavar="USERNAMES", action="store", help="One or more usernames to check with social networks. Check similar usernames using {?} (replace to '_', '-', '.').")
    parser.add_argument( "--browse", "-b", action="store_true", dest="browse",default=False,help="Browse to all results on default browser.")
    parser.add_argument( "--local", "-l", action="store_true", default=False,   help="Force the use of the local data.json file.")
    parser.add_argument("--nsfw",action="store_true", default=False, help="Include checking of NSFW sites from default list.")
    parser.add_argument("--no-txt",action="store_true", dest="no_txt",default=False,help="Disable creation of a txt file")

    args = parser.parse_args()
    signal.signal(signal.SIGINT, handler)
    
    try:
        latestReleaseRaw = requests.get(forge_api_latest_release).text
        latestReleaseJson = loads(latestReleaseRaw)
        latestRemoteTag = latestReleaseJson["tag_name"]
        
        if latestRemoteTag[1:] != __version__:
            print(f"Update available! {__version__} --> {latestRemoteTag[1:]}" f"\n{latestReleaseJson['html_url']}")
    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")
        
    if args.tor and (args.proxy is not None):
        raise Exception("Tor and Proxy cannot be set at the same time.")
    if args.proxy is not None:
        print("Using the proxy: " + args.proxy)
    if args.tor or args.unique_tor:
        print("Using Tor to make requests")
        print("Warning: some websites might refuse connecting over Tor, so note that using this option might increase connection errors.")
        
    if args.no_color:
        init(strip=True, convert=False)
    else:
        init(autoreset=True)
    
    if args.output is not None and args.folderoutput is not None:
        print("You can only use one of the output methods.")
        sys.exit(1)

    if args.output is not None and len(args.username) != 1:
        print("You can only use --output with a single username")
        sys.exit(1)
        
    try:
        if args.local:
            sites = FRSHSitesInfo(os.path.join(os.path.dirname(__file__), "resources/data.json"))
        else:
            jsonFileLocation = args.json_file
            
            if args.json_file:
                if args.jsonFile.isnumeric():
                    pullNumber = args.json_file
                    pullUrl = f"https://api.github.com/repos/AIAnsar1/Farasha/pulls/{pullNumber}"
                    pullRequestRaw = requests.get(pullUrl).text
                    pullRequestJson = loads(pullRequestRaw)
                    
                    if "message" in pullRequestJson:
                        print(f"ERROR: Pull request #{pullNumber} not found.")
                        sys.exit(1)
                    headCommitSha = pullRequestJson["head"]["sha"]
                    jsonFileLocation = f"https://raw.githubusercontent.com/AIAnsar1/Farasha/{headCommitSha}/resources/data.json"
            sites = FRSHSitesInfo(jsonFileLocation)
    except Exception as error:
        print(f"[ ERROR ]:  {error}")
        sys.exit(1)
        
    if not args.nsfw:
        sites.removeNsfwSites(doNotRemove=args.site_list)
    siteDataAll = {site.name: site.information for site in sites}
    
    if args.site_list == []:
        siteData = siteDataAll
    else:
        siteData = {}
        siteMissing = []
        
        for site in args.site_list:
            counter = 0
            
            for existingSite in siteDataAll:
                if site.lower() == existingSite.lower():
                    siteData[existingSite] = siteDataAll[existingSite]
                    counter += 1
            if counter == 0:
                siteMissing.append(f"'{site}'")
        if siteMissing:
            print(f"[ ERROR ]: Desired sites not found: {', '.join(siteMissing)}.")
            
        if not siteData:
            sys.exit(1)
    queryNotify = FRSHQueryNotifyPrint(result=None, verbose=args.verbose, print_all=args.print_all, browse=args.browse)
    allUsernames = []
    
    for username in args.username:
        if checkForParameter(username):
            for name in multipleUsername(username):
                allUsernames.append(name)
        else:
            allUsernames.append(username)
    for username in allUsernames:
        results = farasha(username,siteData,queryNotify,tor=args.tor,unique_tor=args.unique_tor,dump_response=args.dump_response,proxy=args.proxy, timeout=args.timeout)
        
        if args.output:
            resultFile = args.output
        elif args.folderoutput:
            os.makedirs(args.folderoutput, exist_ok=True)
            resultFile = os.path.join(args.folderoutput, f"{username}.txt")
        else:
            resultFile = f"{username}.txt"
        
        if not args.no_txt:
            with open(resultFile, "w", encoding="UTF-8") as file:
                existsCounter = 0
                
                for websiteName in results:
                    dictionary = results[websiteName]
                    
                    if dictionary.get("status").status == FRSHQueryStatus.CLAIMED:
                        existsCounter += 1
                        file.write(dictionary["url_user"] + "\n")
                file.write(f"Total Websites Username Detected On : {existsCounter}\n")
        if args.csv:
            resultFile = f"{username}.csv"
            
            if args.folderoutput:
                os.makedirs(args.folderoutput, exist_ok=True)
                resultFile = os.path.join(args.folderoutput, resultFile)
                
            with open(resultFile, "w", newline="", encoding="UTF-8") as csvReport:
                writer = csv.writer(csvReport)
                writer.writerow(["username", "name", "url_main", "url_user", "exists", "http_status", "response_time_s"])
                
                for site in results:
                    if (args.print_found and not args.print_all and results[site]["status"].status != FRSHQueryStatus.CLAIMED):
                        continue
                    responseTimeS = results[site]["status"].query_time
                    
                    if responseTimeS is None:
                        responseTimeS = ""
                    writer.writerow([username,site,results[site]["url_main"],results[site]["url_user"],str(results[site]["status"].status), results[site]["http_status"],responseTimeS])
                    
        if args.xlsx:
            usernames, names, urlmain, urlUser, exists, httpStatus, responseTimeS = [], [], [], [], [], [], []
            
            for site in results:
                if (args.print_found and not args.print_all and results[site]["status"].status != FRSHQueryStatus.CLAIMED):
                    continue
                
                if responseTimeS is None:
                    responseTimeS.append("")
                else: 
                    responseTimeS.append(results[site]["status"].query_time)
                usernames.append(username)
                names.append(site)
                urlmain.append(results[site]["url_main"])
                urlUser.append(results[site]["url_user"])
                exists.append(str(results[site]["status"].status))
                httpStatus.append(results[site]["http_status"])
            DataFrame = pandas.DataFrame({"username": usernames, "name": names, "url_main": urlmain, "url_user": urlUser,"exists": exists, "http_status": httpStatus,"response_time_s": responseTimeS,})
            DataFrame.to_excel(f"{username}.xlsx", sheet_name="sheet1", index=False)
            
        print() 
    queryNotify.finish()          





if __name__ == "__main__":
    main()