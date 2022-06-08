#!/bin/env python3

from pathlib import Path
import queue
import requests
import threading
import sys
import requests
import argparse

# friendly user agent string
AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php', '.bak', '.orig', '.inc']
THREADS = 5

def dir_bruter(target, words):
    headers = {'User-Agent': AGENT}
    while not words.empty():
        url = f'{target}{words.get()}'
        try:
            r = requests.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            sys.stderr.write('x')
            sys.stderr.flush()
            continue

        if r.status_code == 200:
            print(f'\nSuccess ({r.status_code}: {url})')
        elif r.status_code == 404 or r.status_code == 403:
            sys.stderr.write('.')
            sys.stderr.flush()
        else: # any other status code we are not checking for
            print(f'{r.status_code} => {url}')


def get_words(resume=None, wordlist=None):
    words = queue.Queue()
    # apply extension to word
    def extend_words(word):
        if "." in word:
            words.put(f'/{word}')
        else: # a directory
            words.put(f'/{word}/')
        for extension in EXTENSIONS:
            words.put(f'/{word}{extension}')

    with open(wordlist) as f:
        raw_words = f.read()
    # if resume is not None, then we know that we want
    # to resume extending from the raw_words lists
    # where the word matches the resume
    # TODO: need to setup if connection fails retry
    found_resume = False
    for word in raw_words.split():
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f'Resuming wordlist from: {resume}')
        else:
            #print(word)
            extend_words(word)
    return words


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Brute force and find all the files accessible on the given webserver.')
    parser.add_argument('-target', help='url to bruteforce', required=True)
    parser.add_argument('-wordlist', help='wordlist for the files to check', default=Path(__file__).absolute().parent / 'resources' / 'all.txt', type=lambda p: Path(p).absolute())
    args = parser.parse_args()

    print('Prepping words...')
    words = get_words(wordlist=args.wordlist);
    print(f'Using {words.qsize()} words. Press return to continue with bruteforce...')
    sys.stdin.readline()
    for _ in range(THREADS):
        t = threading.Thread(target=dir_bruter, args=(args.target, words,))
        t.start()
