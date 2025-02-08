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
    
    
    
checkSymbols = ["_", "-", "."]
    
def getResponse(requestFuture, errorType, socialNetwork):
    response = None
    errorContext = "General Unknown Error"
    exceptionText = None
    
    try:
        response = requestFuture.result()
        
        if response.status_code:
            errorContext = None
    except requests.exceptions.HTTPError as errh:
        errorContext = "[ ERROR ]: HTTP!"
        exceptionText = str(errh)
    except requests.exceptions.ProxyError as errp:
        errorContext = "[ ERROR ]: Proxy!"
        exceptionText = str(errp)
    except requests.exceptions.ConnectionError as errc:
        errorContext = "[ ERROR ]: Connecting!"
        exceptionText = str(errc)
    except requests.exceptions.Timeout as errt:
        errorContext = "[ ERROR ]: Timeout!"
        exceptionText = str(errt)
    except requests.exceptions.RequestException as err:
        errorContext = "[ ERROR ]: Unknown!"
        exceptionText = str(err)
    return response, errorContext, exceptionText


def interpolateString(inputObject, username):
    if isinstance(inputObject, str):
        return inputObject.replace("{}", username)
    elif isinstance(inputObject, dict):
        return {k: interpolateString(v, username) for k, v in inputObject.items()}
    elif isinstance(inputObject, list):
        return [interpolateString(i, username) for i in inputObject]
    return inputObject

def checkForParameter(username):
    return "{?}" in username


def multipleUsername(username):
    allUsernames = []
    for i in checkSymbols:
        allUsernames.append(username.replace("{?}", i))
    return allUsernames

def farasha(username: str, siteData: dict, queryNotify: FRSHQueryNotify, tor: bool = False, uniqueTor: bool = False, dumpResponse: bool = False, proxy: Optional[str] = None, timeout: int = 60):
    queryNotify.start(username)
    
    if tor or uniqueTor:
        try:
            from torrequest import TorRequest
        except ImportError:
            print("Important!")
            print("> --tor and --unique-tor are now DEPRECATED, and may be removed in a future release of Farasha.")
            print("> Other packages should refer to their documentation, or install it separately with `pip install torrequest`.\n")
            sys.exit(queryNotify.finish())
            
        print("Important!")
        print("> --tor and --unique-tor are now DEPRECATED, and may be removed in a future release of Farasha.")
        
        try:
            underlyingRequest = TorRequest()
        except OSError:
            print("Tor not found in system path. Unable to continue.\n")
            sys.exit(queryNotify.finish())
        underlyingSession = underlyingRequest.session
    else:
        underlyingSession = requests.session()
        underlyingRequest = requests.Request()
        
    if len(siteData) >= 20:
        maxWorkers = 20
    else:
        maxWorkers = len(siteData)
        
    session = FRSHFuturesSession(maxWorkers=maxWorkers, session=underlyingSession)
    resultsTotal = {}
    
    for socialNetwork, netInfo in siteData.items():
        resultsSite = {"url_main": netInfo.get("urlMain")}
        headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"}
        
        if "headers" in netInfo:
            headers.update(netInfo["headers"])
        url = interpolateString(netInfo["url"], username.replace(' ', '%20'))
        regexCheck = netInfo.get("regexCheck")
        
        if regexCheck and re.search(regexCheck, username) is None:
            resultsSite["status"] = FRSHQueryResult(username, socialNetwork, url, FRSHQueryStatus.ILLEGAL)
            resultsSite["url_user"] = ""
            resultsSite["http_status"] = ""
            resultsSite["response_status"] = ""
            queryNotify.update(resultsSite["status"])
        else:
            resultsSite["url_user"] = url
            urlProbe = netInfo.get("urlProbe")
            requestMethod = netInfo.get("request_method")
            requestPayload= netInfo.get("request_payload")
            request = None
            
            if requestMethod is not None:
                if requestMethod == "GET":
                    request = session.get
                elif requestMethod == "HEAD":
                    request = session.head
                elif requestMethod == "POST":
                    request = session.post
                elif requestMethod == "PUT":
                    request = session.put
                else:
                    raise RuntimeError(f"Unsupported request_method for {url}")
                
            if requestPayload is not None:
                requestPayload = interpolateString(requestPayload, username)
                
            if urlProbe is None:
                urlProbe = url
            else:
                urlProbe = interpolateString(urlProbe, username)
                
            if request is None:
                if netInfo["errorType"] == "statis_code":
                    request = session.head
                else:
                    request = session.get
                    
            if netInfo["errorType"] == "response_url":
                allowRedirects = False
            else:
                allowRedirects = True
            
            if proxy is not None:
                proxies = {"http": proxy, "https": proxy}
                future = request(url=urlProbe, headers=headers, proxies=proxies, allowRedirects=allowRedirects, timeout=timeout, json=requestPayload)
            else:
                future = request(urlProbe=urlProbe, headers=headers, allowRedirects=allowRedirects, timeout=timeout, json=requestPayload)
            netInfo["request_future"] = future
            
            if uniqueTor:
                underlyingRequest.reset_identity()
        resultsTotal[socialNetwork] = resultsSite
    
    for socialNetwork, netInfo in siteData.items():
        resultsSite = resultsTotal.get(socialNetwork)
        url = resultsSite.get("url_user")
        status = resultsSite.get("status")
        
        if status is not None:
            continue
        errorType = netInfo["errorType"]
        future = netInfo["request_future"]
        r, errorText, exceptionText = getResponse(requestFuture=future, errorType=errorType, socialNetwork=socialNetwork)
        
        try:
            responseTime = r.elapsed
        except AttributeError:
            responseTime = None
            
        try:
            http_status = r.status_code
        except Exception:
            http_status = "7"
        
        try:
            responseText = r.text.encode(r.encoding or "UTF-8")
        except Exception:
            responseText = ""
            
        queryStatus = FRSHQueryStatus.UNKNOWN
        errorContext = None
        
        WafHitMsgs = [
            r'.loading-spinner{visibility:hidden}body.no-js .challenge-running{display:none}body.dark{background-color:#222;color:#d9d9d9}body.dark a{color:#fff}body.dark a:hover{color:#ee730a;text-decoration:underline}body.dark .lds-ring div{border-color:#999 transparent transparent}body.dark .font-red{color:#b20f03}body.dark',
            r'<span id="challenge-error-text">',
            r'AwsWafIntegration.forceRefreshToken',
            r'{return l.onPageView}}),Object.defineProperty(r,"perimeterxIdentifiers",{enumerable:'
        ]
        
        if errorText is not None:
            errorContext = errorText
        elif any(hitMsg in r.text for hitMsg in WafHitMsgs):
            queryStatus = FRSHQueryStatus.WAF
        elif errorType == "message":
            errorFlag = True
            errors = netInfo.get("errorMsg")
            
            if isinstance(errors, str):
                if errors in r.text:
                    errorFlag = False
            else:
                for error in errors:
                    if error in r.text:
                        errorFlag = False
                        break
            if errorFlag:
                queryStatus = FRSHQueryStatus.CLAIMED
            else:
                queryStatus = FRSHQueryStatus.AVIALABLE
        elif errorType == "status_code":
            errorCodes = netInfo.get("errorCode")
            queryStatus = FRSHQueryStatus.CLAIMED
            
            if isinstance(errorCodes, int):
                errorCodes = [errorCodes]
            if errorCodes is not None and r.status_code in errorCodes:
                queryStatus = FRSHQueryStatus.AVIALABLE
            elif r.status_code >= 300 or r.status_code < 200:
                queryStatus = FRSHQueryStatus.AVIALABLE
        elif errorType == "response_url":
            if 200 <= r.status_code < 300:
                queryStatus = FRSHQueryStatus.CLAIMED
            else:
                queryStatus = FRSHQueryStatus.AVIALABLE
        else:
            raise ValueError(f"Unknown Error Type '{errorType}' for " f"site '{socialNetwork}'")
        
        if dumpResponse:
            print("[ INFO ]: +++++++++++++++++++++")
            print(f"[ INFO ]: TARGET NAME   : {socialNetwork}")
            print(f"[ INFO ]: USERNAME      : {username}")
            print(f"[ INFO ]: TARGET URL    : {url}")
            print(f"[ INFO ]: TEST METHOD   : {errorType}")
            
            try:
                print(f"STATUS CODES  : {netInfo['errorCode']}")
            except KeyError:
                pass
            print("[ INFO ]: Results...")
            
            try:
                print(f"ERROR TEXT    : {netInfo['errorMsg']}")
            except KeyError:
                pass
            print("[ INFO ]: -> BEGIN RESPONSE TEXT")
            
            try:
                print(r.text)
            except Exception:
                pass
            print("[ INFO ]: END RESPONSE TEXT")
            print("[ INFO ]: VERDICT       : " + str(queryStatus))
            print("[ INFO ]: +++++++++++++++++++++")
        result = FRSHQueryResult(username=username, siteName=socialNetwork, SiteUrlUser=url, status=queryStatus, QueryTime=responseTime, context=errorContext)
        queryNotify.update(result)
        resultsSite["status"] = result
        resultsSite["http_status"] = http_status
        resultsSite["response_text"] = responseText
        resultsTotal[socialNetwork] = resultsSite
        
        return resultsTotal
            


def timeoutCheck(value):
    floatValue = float(value)
    
    if floatValue <= 0:
        raise ArgumentTypeError(f"Invalid timeout value: {value}. Timeout must be a positive number.")
    return floatValue


def handler(signalReceived, frame):
    sys.exit(0)

