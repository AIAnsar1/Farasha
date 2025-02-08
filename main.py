#!/usr/bin/venv python3
import sys, csv, signal, os, re, requests
import pandas as pd
from json import loads as json_loads
from core.__init__ import (__longname__, __shortname__, __version__, forge_api_latest_release)
from argparse import ArgumentParser, RawDescriptionHelpFormatter, ArgumentTypeError
from json import loads
from colorama import init
from core.FRSHQueryStatus import FRSHQueryStatus
from core.FRSHQueryNotifyPrint import FRSHQueryNotifyPrint
from core.FRSHSitesInfo import FRSHSitesInformation
from core.FRSHSitesInfo import FRSHSiteInformation
from core.Farasha import timeout_check, handler, check_for_parameter, farasha, multiple_usernames




def main():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description=f"{__longname__} (Version {__version__})")
    parser.add_argument("--version", action="version", version=f"{__shortname__} v{__version__}", help="Display version information and dependencies.")
    parser.add_argument("--verbose", "-v", "-d", "--debug", action="store_true",dest="verbose", default=False,help="Display extra debugging information and metrics.")
    parser.add_argument("--folderoutput","-fo",dest="folderoutput", help="If using multiple usernames, the output of the results will be saved to this folder.", )
    parser.add_argument("--output","-o",dest="output",help="If using single username, the output of the result will be saved to this file.")
    parser.add_argument("--tor","-t",action="store_true",dest="tor",default=False, help="Make requests over Tor; increases runtime; requires Tor to be installed and in system path." )
    parser.add_argument("--unique-tor","-u",action="store_true",dest="unique_tor",default=False,help="Make requests over Tor with new Tor circuit after each request; increases runtime; requires Tor to be installed and in system path.")
    parser.add_argument("--csv",action="store_true",dest="csv",default=False,help="Create Comma-Separated Values (CSV) File." )
    parser.add_argument("--xlsx",action="store_true", dest="xlsx",default=False,help="Create the standard file for the modern Microsoft Excel spreadsheet (xlsx).", )
    parser.add_argument("--site",action="append",metavar="SITE_NAME",dest="site_list",default=[],help="Limit analysis to just the listed sites. Add multiple options to specify more than one site.",)
    parser.add_argument("--proxy",  "-p", metavar="PROXY_URL", action="store", dest="proxy", default=None,help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080")
    parser.add_argument("--dump-response",  action="store_true",  dest="dump_response",  default=False,  help="Dump the HTTP response to stdout for targeted debugging.")
    parser.add_argument("--json",  "-j",  metavar="JSON_FILE",  dest="json_file",  default=None,  help="Load data from a JSON file or an online, valid, JSON file. Upstream PR numbers also accepted.")
    parser.add_argument("--timeout",  action="store", metavar="TIMEOUT", dest="timeout", type=timeout_check, default=60, help="Time (in seconds) to wait for response to requests (Default: 60)")
    parser.add_argument("--print-all", action="store_true", dest="print_all", default=False, help="Output sites where the username was not found.")
    parser.add_argument("--print-found", action="store_true", dest="print_found", default=True, help="Output sites where the username was found (also if exported as file).")
    parser.add_argument("--no-color", action="store_true", dest="no_color", default=False,  help="Don't color terminal output")
    parser.add_argument("username", nargs="+", metavar="USERNAMES", action="store", help="One or more usernames to check with social networks. Check similar usernames using {?} (replace to '_', '-', '.').")
    parser.add_argument("--browse", "-b", action="store_true", dest="browse",default=False,help="Browse to all results on default browser.")
    parser.add_argument("--local", "-l", action="store_true", default=False,   help="Force the use of the local data.json file.")
    parser.add_argument("--nsfw",action="store_true", default=False, help="Include checking of NSFW sites from default list.")
    parser.add_argument("--no-txt",action="store_true", dest="no_txt",default=False,help="Disable creation of a txt file")

    args = parser.parse_args()
    signal.signal(signal.SIGINT, handler)
    
    try:
        latest_release_raw = requests.get(forge_api_latest_release).text
        latest_release_json = json_loads(latest_release_raw)
        latest_remote_tag = latest_release_json["tag_name"]

        if latest_remote_tag[1:] != __version__:
            print(f"Update available! {__version__} --> {latest_remote_tag[1:]}" f"\n{latest_release_json['html_url']}")

    except Exception as error:
        print(f"A problem occurred while checking for an update: {error}")

    # Argument check
    # TODO regex check on args.proxy
    if args.tor and (args.proxy is not None):
        raise Exception("Tor and Proxy cannot be set at the same time.")

    # Make prompts
    if args.proxy is not None:
        print("Using the proxy: " + args.proxy)

    if args.tor or args.unique_tor:
        print("Using Tor to make requests")

        print(
            "Warning: some websites might refuse connecting over Tor, so note that using this option might increase connection errors."
        )

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
            sites = FRSHSitesInformation(os.path.join(os.path.dirname(__file__), "resources/data.json"))
        else:
            json_file_location = args.json_file
            if args.json_file:
                if args.json_file.isnumeric():
                    pull_number = args.json_file
                    pull_url = f"https://api.github.com/repos/sherlock-project/sherlock/pulls/{pull_number}"
                    pull_request_raw = requests.get(pull_url).text
                    pull_request_json = json_loads(pull_request_raw)

                    # Check if it's a valid pull request
                    if "message" in pull_request_json:
                        print(f"ERROR: Pull request #{pull_number} not found.")
                        sys.exit(1)

                    head_commit_sha = pull_request_json["head"]["sha"]
                    json_file_location = f"https://raw.githubusercontent.com/sherlock-project/sherlock/{head_commit_sha}/sherlock_project/resources/data.json"

            sites = FRSHSitesInformation(json_file_location)
    except Exception as error:
        print(f"ERROR:  {error}")
        sys.exit(1)

    if not args.nsfw:
        sites.remove_nsfw_sites(do_not_remove=args.site_list)

    # Create original dictionary from SitesInformation() object.
    # Eventually, the rest of the code will be updated to use the new object
    # directly, but this will glue the two pieces together.
    site_data_all = {site.name: site.information for site in sites}
    if args.site_list == []:
        # Not desired to look at a sub-set of sites
        site_data = site_data_all
    else:
        # User desires to selectively run queries on a sub-set of the site list.
        # Make sure that the sites are supported & build up pruned site database.
        site_data = {}
        site_missing = []
        for site in args.site_list:
            counter = 0
            for existing_site in site_data_all:
                if site.lower() == existing_site.lower():
                    site_data[existing_site] = site_data_all[existing_site]
                    counter += 1
            if counter == 0:
                # Build up list of sites not supported for future error message.
                site_missing.append(f"'{site}'")

        if site_missing:
            print(f"Error: Desired sites not found: {', '.join(site_missing)}.")

        if not site_data:
            sys.exit(1)

    # Create notify object for query results.
    query_notify = FRSHQueryNotifyPrint(
        result=None, verbose=args.verbose, print_all=args.print_all, browse=args.browse
    )

    # Run report on all specified users.
    all_usernames = []
    for username in args.username:
        if check_for_parameter(username):
            for name in multiple_usernames(username):
                all_usernames.append(name)
        else:
            all_usernames.append(username)
    for username in all_usernames:
        results = farasha(username, site_data, query_notify, tor=args.tor, unique_tor=args.unique_tor,dump_response=args.dump_response,proxy=args.proxy,timeout=args.timeout)

        if args.output:
            result_file = args.output
        elif args.folderoutput:
            os.makedirs(args.folderoutput, exist_ok=True)
            result_file = os.path.join(args.folderoutput, f"{username}.txt")
        else:
            result_file = f"{username}.txt"

        if not args.no_txt:
            with open(result_file, "w", encoding="utf-8") as file:
                exists_counter = 0
                for website_name in results:
                    dictionary = results[website_name]
                    if dictionary.get("status").status == FRSHQueryStatus.CLAIMED:
                        exists_counter += 1
                        file.write(dictionary["url_user"] + "\n")
                file.write(f"Total Websites Username Detected On : {exists_counter}\n")

        if args.csv:
            result_file = f"{username}.csv"
            if args.folderoutput:
                os.makedirs(args.folderoutput, exist_ok=True)
                result_file = os.path.join(args.folderoutput, result_file)

            with open(result_file, "w", newline="", encoding="utf-8") as csv_report:
                writer = csv.writer(csv_report)
                writer.writerow(
                    [
                        "username",
                        "name",
                        "url_main",
                        "url_user",
                        "exists",
                        "http_status",
                        "response_time_s",
                    ]
                )
                for site in results:
                    if (args.print_found and not args.print_all and results[site]["status"].status != FRSHQueryStatus.CLAIMED):
                        continue
                    response_time_s = results[site]["status"].query_time
                    if response_time_s is None:
                        response_time_s = ""
                    writer.writerow(
                        [
                            username,
                            site,
                            results[site]["url_main"],
                            results[site]["url_user"],
                            str(results[site]["status"].status),
                            results[site]["http_status"],
                            response_time_s,
                        ]
                    )
        if args.xlsx:
            usernames = []
            names = []
            url_main = []
            url_user = []
            exists = []
            http_status = []
            response_time_s = []

            for site in results:
                if (args.print_found and not args.print_all and results[site]["status"].status != FRSHQueryStatus.CLAIMED):
                    continue
                if response_time_s is None:
                    response_time_s.append("")
                else:
                    response_time_s.append(results[site]["status"].query_time)
                usernames.append(username)
                names.append(site)
                url_main.append(results[site]["url_main"])
                url_user.append(results[site]["url_user"])
                exists.append(str(results[site]["status"].status))
                http_status.append(results[site]["http_status"])

            DataFrame = pd.DataFrame(
                {
                    "username": usernames,
                    "name": names,
                    "url_main": url_main,
                    "url_user": url_user,
                    "exists": exists,
                    "http_status": http_status,
                    "response_time_s": response_time_s,
                }
            )
            DataFrame.to_excel(f"{username}.xlsx", sheet_name="sheet1", index=False)

        print()
    query_notify.finish()         





if __name__ == "__main__":
    main()