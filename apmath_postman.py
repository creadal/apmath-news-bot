import urllib.request
import hashlib
import telegram
from config import telegram_token
from html.parser import HTMLParser
import time

class NewsParser(HTMLParser):
    texts = []
    signatures = []
    msg = ''
    islink = False
    reading = False
    reading_signature = False
    link_text = ''
    link_address = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            if ('class', 'newsdate') in attrs:
                self.reading = True
            elif ('class', 'signature') in attrs:
                self.texts.append(self.msg)
                self.msg = ''
                self.reading = False
                self.reading_signature = True

        if tag == 'a' and self.reading:
            self.link_address = attrs[0][1]
            self.islink = True

    def handle_data(self, data):
        if self.reading or self.reading_signature:
            if not self.islink:
                self.msg += data
            else:
                self.link_text = data

    def handle_endtag (self, tag):
        if tag == 'a' and self.reading:
            self.islink = False
            self.msg += '[' + self.link_text + '](' + self.link_address + ')'
        
        if tag == 'p' and self.reading_signature:
            self.reading_signature = False
            self.signatures.append(self.msg)
            self.msg = ''

def post(text, signature):
    bot = telegram.Bot(token=telegram_token)
    status = bot.send_message(chat_id="@apmath_spbu_autonews", text=text+signature, parse_mode=telegram.ParseMode.MARKDOWN)

    print(status)

def bob_do_something():
    response = urllib.request.urlopen('http://www.apmath.spbu.ru/ru/')
    html = response.read()
    html = html.decode('utf-8')

    parser = NewsParser()
    parser.feed(html)

    news = parser.texts
    signatures = parser.signatures

    file_read = open("news", "r")

    news_notes = []

    for line in file_read:
        news_notes.append(line)

    file_read.close()

    for i in range(len(news)):
        h = hashlib.md5(bytes(news[-i-1], 'utf-8'))
        if (str(h.hexdigest()) + '\n') not in news_notes:
            file_append = open("news", "a+")

            file_append.write(str(h.hexdigest()) + '\n')
            print(str(h.hexdigest()) + ' posted\n')

            post(news[-i-1], signatures[-i-1])

            file_append.close()

    


while True:
    try:
        bob_do_something()
        time.sleep(10)
        print(time.clock())
    except:
        print("Unhandled exception. Restarting program.")

