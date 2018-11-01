#!/usr/bin/python3
import os
import sys
import string



if __name__ == "__main__":
    f = open(sys.argv[1])
    f2 = open('script_template.py')
    f3 = open('tmp.py', 'w')
    for line2 in f2.readlines():
        if 'CODE' in line2:
            for line in f.readlines():
                linetmp = line2.replace('CODE', line,1)
                f3.write(linetmp)
        else:
            f3.write(line2)
    f3.close()
    os.system('python3 tmp.py')
    
    
    
