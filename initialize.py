import os
from subprocess import PIPE


class InitializeShellScript:
    # default constructor
    def __init__(self, backend, base):
        # Running comands manually to the terminal
        os.system('chmod u+x initialize.sh')
        os.system(f'sh initialize.sh {backend} {base}')
