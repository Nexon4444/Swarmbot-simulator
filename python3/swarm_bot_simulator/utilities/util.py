import math


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def log_flush(message, start, stop):
    import logging, sys
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s',
                        )
    time = stop - start

    # logging.debug('wat wat')
    sys.stdout.write(str(message) + str(time))
    # logging.debug((str(message) + str(time)))
    sys.stdout.write('\r')
    sys.stdout.flush()

def restart_line():
    import sys
    sys.stdout.write('\r')
    sys.stdout.flush()


# import time, sys
#
# t = 0
# while True:
#     print('Seconds passed:', t, end='')
#     sys.stdout.flush()
#     time.sleep(1)
#     t += 1
#     # print('\b'*20, end='')