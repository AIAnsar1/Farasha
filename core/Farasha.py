import sys, re, requests

from core.__init__ import __longname__, __shortname__, __version__
from argparse import ArgumentTypeError
from typing import Optional
from colorama import init
from core.FRSHQueryStatus import FRSHQueryStatus
from core.FRSHQueryResult import FRSHQueryResult
from core.FRSHQueryNotify import FRSHQueryNotify
from core.FRSHFuturesSession import FRSHFuturesSession



try:
    from core.__init__ import import_error_test_var
except ImportError:
    print("Did you run Farasha with `python3 Farasha/farasha.py ...`?")
    sys.exit(1)
    
    
    
def get_response(request_future, error_type, social_network):
    # Default for Response object if some failure occurs.
    response = None

    error_context = "General Unknown Error"
    exception_text = None
    try:
        response = request_future.result()
        if response.status_code:
            # Status code exists in response object
            error_context = None
    except requests.exceptions.HTTPError as errh:
        error_context = "HTTP Error"
        exception_text = str(errh)
    except requests.exceptions.ProxyError as errp:
        error_context = "Proxy Error"
        exception_text = str(errp)
    except requests.exceptions.ConnectionError as errc:
        error_context = "Error Connecting"
        exception_text = str(errc)
    except requests.exceptions.Timeout as errt:
        error_context = "Timeout Error"
        exception_text = str(errt)
    except requests.exceptions.RequestException as err:
        error_context = "Unknown Error"
        exception_text = str(err)

    return response, error_context, exception_text


def interpolate_string(input_object, username):
    if isinstance(input_object, str):
        return input_object.replace("{}", username)
    elif isinstance(input_object, dict):
        return {k: interpolate_string(v, username) for k, v in input_object.items()}
    elif isinstance(input_object, list):
        return [interpolate_string(i, username) for i in input_object]
    return input_object


def check_for_parameter(username):
    return "{?}" in username


checksymbols = ["_", "-", "."]


def multiple_usernames(username):
    allUsernames = []
    for i in checksymbols:
        allUsernames.append(username.replace("{?}", i))
    return allUsernames


def farasha(username: str,site_data: dict,query_notify: FRSHQueryNotify,tor: bool = False,unique_tor: bool = False,dump_response: bool = False,proxy: Optional[str] = None,timeout: int = 60):
    query_notify.start(username)
    if tor or unique_tor:
        try:
            from torrequest import TorRequest
        except ImportError:
            print("[ INFO ]: Important!")
            print("[ INFO ]: > --tor and --unique-tor are now DEPRECATED, and may be removed in a future release of Sherlock.")
            print("[ INFO ]: > If you've installed Sherlock via pip, you can include the optional dependency via `pip install 'sherlock-project[tor]'`.")
            print("[ INFO ]: > Other packages should refer to their documentation, or install it separately with `pip install torrequest`.\n")
            sys.exit(query_notify.finish())

        print("[ INFO ]: Important!")
        print("[ INFO ]: > --tor and --unique-tor are now DEPRECATED, and may be removed in a future release of Sherlock.")

        try:
            underlying_request = TorRequest()
        except OSError:
            print("Tor not found in system path. Unable to continue.\n")
            sys.exit(query_notify.finish())
        underlying_session = underlying_request.session
    else:
        underlying_session = requests.session()
        underlying_request = requests.Request()

    if len(site_data) >= 20:
        max_workers = 20
    else:
        max_workers = len(site_data)
    session = FRSHFuturesSession(max_workers=max_workers, session=underlying_session)
    results_total = {}
    
    for social_network, net_info in site_data.items():
        results_site = {"url_main": net_info.get("urlMain")}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        }

        if "headers" in net_info:
            headers.update(net_info["headers"])
        url = interpolate_string(net_info["url"], username.replace(' ', '%20'))
        regex_check = net_info.get("regexCheck")
        
        if regex_check and re.search(regex_check, username) is None:
            results_site["status"] = FRSHQueryResult(username, social_network, url, FRSHQueryStatus.ILLEGAL)
            results_site["url_user"] = ""
            results_site["http_status"] = ""
            results_site["response_text"] = ""
            query_notify.update(results_site["status"])
        else:
            results_site["url_user"] = url
            url_probe = net_info.get("urlProbe")
            request_method = net_info.get("request_method")
            request_payload = net_info.get("request_payload")
            request = None

            if request_method is not None:
                if request_method == "GET":
                    request = session.get
                elif request_method == "HEAD":
                    request = session.head
                elif request_method == "POST":
                    request = session.post
                elif request_method == "PUT":
                    request = session.put
                else:
                    raise RuntimeError(f"Unsupported request_method for {url}")

            if request_payload is not None:
                request_payload = interpolate_string(request_payload, username)
            if url_probe is None:
                url_probe = url
            else:
                url_probe = interpolate_string(url_probe, username)
            if request is None:
                if net_info["errorType"] == "status_code":
                    request = session.head
                else:
                    request = session.get

            if net_info["errorType"] == "response_url":
                allow_redirects = False
            else:
                allow_redirects = True
            if proxy is not None:
                proxies = {"http": proxy, "https": proxy}
                future = request(url=url_probe, headers=headers,proxies=proxies,allow_redirects=allow_redirects,timeout=timeout,json=request_payload)
            else:
                future = request(url=url_probe,headers=headers,allow_redirects=allow_redirects,timeout=timeout,json=request_payload)
            net_info["request_future"] = future
            
            if unique_tor:
                underlying_request.reset_identity()
        results_total[social_network] = results_site
        
    for social_network, net_info in site_data.items():
        results_site = results_total.get(social_network)
        url = results_site.get("url_user")
        status = results_site.get("status")
        if status is not None:
            continue
        error_type = net_info["errorType"]
        future = net_info["request_future"]
        r, error_text, exception_text = get_response(request_future=future, error_type=error_type, social_network=social_network)

        try:
            response_time = r.elapsed
        except AttributeError:
            response_time = None

        try:
            http_status = r.status_code
        except Exception:
            http_status = "?"
        try:
            response_text = r.text.encode(r.encoding or "UTF-8")
        except Exception:
            response_text = ""
        query_status = FRSHQueryStatus.UNKNOWN
        error_context = None
        WAFHitMsgs = [
            r'.loading-spinner{visibility:hidden}body.no-js .challenge-running{display:none}body.dark{background-color:#222;color:#d9d9d9}body.dark a{color:#fff}body.dark a:hover{color:#ee730a;text-decoration:underline}body.dark .lds-ring div{border-color:#999 transparent transparent}body.dark .font-red{color:#b20f03}body.dark',
            r'<span id="challenge-error-text">',
            r'AwsWafIntegration.forceRefreshToken',
            r'{return l.onPageView}}),Object.defineProperty(r,"perimeterxIdentifiers",{enumerable:' 
        ]

        if error_text is not None:
            error_context = error_text
        elif any(hitMsg in r.text for hitMsg in WAFHitMsgs):
            query_status = FRSHQueryStatus.WAF
        elif error_type == "message":
            error_flag = True
            errors = net_info.get("errorMsg")
           
            if isinstance(errors, str):
                if errors in r.text:
                    error_flag = False
            else:
                for error in errors:
                    if error in r.text:
                        error_flag = False
                        break
            if error_flag:
                query_status = FRSHQueryStatus.CLAIMED
            else:
                query_status = FRSHQueryStatus.AVAILABLE
        elif error_type == "status_code":
            error_codes = net_info.get("errorCode")
            query_status = FRSHQueryStatus.CLAIMED

            if isinstance(error_codes, int):
                error_codes = [error_codes]
            if error_codes is not None and r.status_code in error_codes:
                query_status = FRSHQueryStatus.AVAILABLE
            elif r.status_code >= 300 or r.status_code < 200:
                query_status = FRSHQueryStatus.AVAILABLE
        elif error_type == "response_url":
            if 200 <= r.status_code < 300:
                query_status = FRSHQueryStatus.CLAIMED
            else:
                query_status = FRSHQueryStatus.AVAILABLE
        else:
            # It should be impossible to ever get here...
            raise ValueError(f"[ ERROR ]: Unknown Error Type '{error_type}' for " f"site '{social_network}'")

        if dump_response:
            print("[ INFO ]: +++++++++++++++++++++")
            print(f"[ INFO ]: TARGET NAME   : {social_network}")
            print(f"[ INFO ]: USERNAME      : {username}")
            print(f"[ INFO ]: TARGET URL    : {url}")
            print(f"[ INFO ]: TEST METHOD   : {error_type}")
            try:
                print(f"[ INFO ]: STATUS CODES  {net_info['errorCode']}")
            except KeyError:
                pass
            print("[ INFO ]: Results...")
            try:
                print(f"[ INFO ]:  RESPONSE CODE  {r.status_code}")
            except Exception:
                pass
            try:
                print(f"[ ERROR ]: TEXT    {net_info['errorMsg']}")
            except KeyError:
                pass
            print("[ INFO ]: >>>>> BEGIN RESPONSE TEXT")
            try:
                print(r.text)
            except Exception:
                pass
            print("[ INFO ]: <<<<< END RESPONSE TEXT")
            print("[ INFO ]:  VERDICT       : " + str(query_status))
            print("[ INFO ]: +++++++++++++++++++++")
        result = FRSHQueryResult(username=username,site_name=social_network,site_url_user=url,status=query_status, query_time=response_time, context=error_context)
        query_notify.update(result)
        results_site["status"] = result
        results_site["http_status"] = http_status
        results_site["response_text"] = response_text
        results_total[social_network] = results_site
    return results_total


def timeout_check(value):
    float_value = float(value)

    if float_value <= 0:
        raise ArgumentTypeError(f"[ ERROR ]: Invalid timeout value: {value}. Timeout must be a positive number.")
    return float_value


def handler(signal_received, frame):
    sys.exit(0)

