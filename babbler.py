from twython import TwythonStreamer
from getparams import ParamsTxt 
from queue import Queue
from threading import Thread
import win32api, pyttsx3, signal, time


class MyStreamer(TwythonStreamer):

    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, _log):
        super().__init__(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        self.q = Queue()
        self.logpath = _log
        self.go = True
        self.waitTime = 0
        self.maxNum = 0
        self.ignoreUserName = False
        self.skipRT = False
        self.rmvAt = False
        self.rmvHt = False
        self.ignores = []
        signal.signal(signal.SIGTERM, self.exit_pgm)
        signal.signal(signal.SIGINT, self.exit_pgm)
        # signal.signal(signal.SIGHUP, self.exit_pgm)
        self.t = Thread(target=self.speak)
        self.t.daemon = True
        self.t.start()

    def on_success(self, data):
        try:           
            if 'text' in data:
                if data['truncated']:
                    str = data['extended_tweet']['full_text']
                else:
                    str = data['text']

                if self.ignore(str):
                    return

                print(str+'\n')

                if self.maxNum <= 0:
                    self.q.put(self.edit(str))
                elif self.q.qsize() < self.maxNum:
                    self.q.put(self.edit(str))

                self.log_tweet(str+'\n\n')    
        except Exception as e:
            print(e)

    def speak(self):
        self.engine = pyttsx3.init()
        while self.go:
            if not self.q.empty():
                self.engine.say(self.q.get())
                self.engine.runAndWait()
                self.q.task_done()
                if self.waitTime > 0:
                    time.sleep(0.3)

    def on_error(self, status_code, data):
        if(status_code == 430):
            print('twitter status code 420: user rate limited. too many requests')
        elif(status_code == 401):
            print('twitter status code 401: missing or incorrect authentication')
        else:
            print('twitter error status code: '+str(status_code))
        print('exiting...')
        self.go = False
        self.engine.stop()
        self.disconnect()
        self.t.join()

    def log_tweet(self, text):
        self.log = open(self.logpath, 'a+', encoding='utf-8')
        self.log.write(text)
        self.log.close()

    def edit(self, str):
        t = ''
        l = str.split(' ')
        l = [x for x in l if x != 'RT' and x[:4] != 'http']
        for w in l:
            if w == '&amp':
                w = '&'
            t += w+' '
        if self.rmvAt:
            t = t.replace('@', '')
        if self.rmvHt:
            t = t.replace('#', '')
        t = t.replace('$', '')
        return t

    def ignore(self, str):
        if self.skipRT and str[:3] == 'RT ':
            print('skipped retweet: '+str+'\n')
            return True
        s = str.lower()
        for w in self.ignores:
            if s.find(w.lower()) > -1:
                print('ignored: '+w+'\n')
                return True
        return False

    def exit_pgm(self, signum, frame):
        self.go = False
        self.log.close()
        self.engine.stop()
        self.disconnect()
        self.t.join()

    def set_waitTime(self, t):
        self.waitTime = t

    def set_maxNum(self, n):
        self.maxNum = n

    def set_rmvAt(self, bool):
        self.rmvAt = bool

    def set_rmvHt(self, bool):
        self.rmvHt = bool

    def set_skipRt(self, bool):
        self.skipRT = bool

    def addIgnore(self, inpt):
        if isinstance(inpt, str):
            self.ignores.append(inpt)
        elif isinstance(inpt, list):
            self.ignores = self.ignores + inpt


def main():
	p = ParamsTxt('params.txt')

	if(not p.auth_set):
		print('authentication not found in params.txt\nexiting...')
		input()
		return

	print('stream keywords: '+p.streamParams)
	s = ''
	for w in p.ignoreParams:
		s += w + ' '
	print('ignore keywords: '+s)
	if(p.ignoreRetweets):	
		print('ignore retweets\n')

	stream = MyStreamer(p.auth['APP_KEY'], p.auth['APP_SECRET'], p.auth['OAUTH_TOKEN'], p.auth['OAUTH_TOKEN_SECRET'], 'tweetlog.txt')
	# stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, 'tweetlog.txt')

	stream.addIgnore(p.ignoreParams)
	stream.set_rmvHt(True)
	stream.set_skipRt(p.ignoreRetweets)
	stream.set_waitTime(1)
	stream.set_maxNum(200)

	print('\nstarted stream...\n')
	stream.statuses.filter(track=p.streamParams, tweet_mode='extended')

main()
