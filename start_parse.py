from parse_queued import *

if __name__ == '__main__':
    start_parse.apply_async(queue='parse')