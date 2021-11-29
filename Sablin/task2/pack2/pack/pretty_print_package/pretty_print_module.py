from datetime import datetime
from pack.get_time_package.get_time_module import get_time

def print_time_pretty(unixtime):
    formated_time = datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')
    print(formated_time)

def main():
    unixtime = get_time()
    print_time_pretty(unixtime)

if __name__ == '__main__':
    main()