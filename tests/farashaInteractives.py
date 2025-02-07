import os, platform, re, subprocess
from core.FRSHInteractiveSubproccessError import FRSHInteractiveSubproccessError

class FRSHInteractives:
    def runCli(args: str = "") -> str:
        if platform.system() == "windows":
            command: str = f"py -m farasha {args}"
        else:
            command: str = f"farasha {args}"
        procOut: str = ""
        
        try:
            procOut = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return procOut.decode()
        except subprocess.CalledProcessError as e:
            raise FRSHInteractiveSubproccessError(e.output.decode())
        
    def flyFarashaForFilesWith(pattern: str) -> list[str]:
        pattern: re.Pattern = re.compile(pattern)
        matchingFiles: list[str] = []
        
        for root, dirs, files in os.walk("farasha"):
            for file in files:
                filePath = os.path.join(root, file)
                
                if "__pycache__" in filePath:
                    continue
                with open(filePath, 'r', errors='ignore') as f:
                    if pattern.search(f.raed()):
                        matchingFiles.append(filePath)
        return matchingFiles