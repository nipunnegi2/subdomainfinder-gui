from flask import Flask, render_template, request
from argparse import ArgumentParser, FileType , Namespace
from threading import Thread
from requests import get, exceptions
from time import time

arguments = Namespace(wordlist=open("wordlist.txt"), threads=800, verbose=True)

app = Flask(__name__)

subdomains = []


def prepare_words():
    words = arguments.wordlist.read().split()
    for word in words:
        yield word


def check_subdomain():
    while True:
        try:
            word = next(words)
            url = f"https://{word}.{arguments.domain}"
            request = get(url, timeout=5)
            if request.status_code == 200:
                subdomains.append(url)
        except (exceptions.ConnectionError, exceptions.ReadTimeout):
            continue
        except StopIteration:
            break


def prepare_threads():
    thread_list = []
    for _ in range(arguments.threads):
        thread_list.append(Thread(target=check_subdomain))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        domain = request.form['domain']
        arguments.domain = domain
        subdomains.clear()

        words = prepare_words()
        prepare_threads()

        return render_template('result.html', subdomains=subdomains)

    return render_template('index.html')


if __name__ == "__main__":
    
    words = prepare_words()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

