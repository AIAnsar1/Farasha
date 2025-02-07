import sys



if __name__ == '__main__':
    python_version = sys.version.split()[0]
    
    if sys.version_info < (3, 9):
        print("[ INFO ]: Farisha Requires Python 3.12+\n You Are Using Python {python_version}, which is not supported by Farisha.")
        sys.exit(1)
        
    # from Farasha import farasha
    # farasha.main()