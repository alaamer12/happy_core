from sys import argv

try:
    # For Python 3.0 and later
    from urllib.error import URLError
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import URLError, urlopen


def checkInternetConnectivity():
    try:
        url = argv[1]
        print(url)
        protocols = ["https://", "http://"]
        if not any(x for x in protocols if x in url):
            url = "https://" + url
        print("URL:" + url)
    except BaseException:
        url = "https://google.com"
    try:
        urlopen(url, timeout=2)
        print(f'Connection to "{url}" is working')

    except URLError as E:
        print("Connection error:%s" % E.reason)


checkInternetConnectivity()


def bandwidth_check():
    pass


"""
Shaurya Pratap Singh 
@shaurya-blip

Shows loading message while doing something.
"""

import itertools
import threading
import time
import sys

# The task is not done right now
done = False


def animate(message="loading", endmessage="Done!"):
    for c in itertools.cycle(["|", "/", "-", "\\"]):
        if done:
            break
        sys.stdout.write(f"\r {message}" + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"\r {endmessage} ")


t = threading.Thread(
    target=lambda: animate(message="installing..", endmessage="Installation is done!!!")
)
t.start()

# Code which you are running

"""
program.install()
"""

time.sleep(10)

# Then mark done as true and thus it will end the loading screen.
done = True