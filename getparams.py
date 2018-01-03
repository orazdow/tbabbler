import os

class ParamsTxt:

	def __init__(self, path):
		self.streamParams = ''
		self.ignoreParams = []
		self.ignoreRetweets = False
		self.wrote_params = False
		self.auth_set = False
		self.auth = {}
		self.paramInit = '# put one or more search terms below:  ex: large cat, devito, scones\nhodl\n\n# put ignore terms below:  ex: offer, sale, newsletter\noffer, sale, newsletter\n\n# uncomment (#) to ignore retweets:\n#ignore-retweets'
		self.authinit = '\n\n#twitter authentication goes here:\nAPP_KEY = "..."\nAPP_SECRET = "..."\nOAUTH_TOKEN = "..." \nOAUTH_TOKEN_SECRET = "..."'
		self.get_params(path)

	def get_params(self, path):

		self.init_params(path)

		with open(path, 'r', encoding='utf-8') as f:
			for line in f:
				if not len(line.strip()) == 0:
					if not self.wrote_params:
						if not self.is_quote(line):
							if not self.streamParams:
								self.streamParams = line.rstrip()
							else:
								self.ignoreParams = self.split_params(line)
								self.wrote_params = True
					elif not self.is_quote(line):
						if line.find('ignore-retweets') > -1:
							self.ignoreRetweets = True
						elif line.find('APP_KEY') > -1:
							a = line[line.find('=')+1:].replace(' ', '').replace('"', '').replace('\'', '').rstrip()
							if a != '...':
								self.auth['APP_KEY'] = a

						elif line.find('APP_SECRET') > -1:
							a = line[line.find('=')+1:].replace(' ', '').replace('"', '').replace('\'', '').rstrip()
							if a != '...':
								self.auth['APP_SECRET'] = a

						elif line.find('OAUTH_TOKEN') > -1 and line.find('OAUTH_TOKEN_SECRET') == -1:
							a = line[line.find('=')+1:].replace(' ', '').replace('"', '').replace('\'', '').rstrip()
							if a != '...':							
								self.auth['OAUTH_TOKEN'] = a

						elif line.find('OAUTH_TOKEN_SECRET') > -1:
							a = line[line.find('=')+1:].replace(' ', '').replace('"', '').replace('\'', '').rstrip()
							if a != '...':
								self.auth['OAUTH_TOKEN_SECRET'] = a

		self.auth_set = len(self.auth) == 4

	def init_params(self, path):
		if not os.path.isfile(path):
			f = open(path, 'w', encoding='utf-8')
			f.write(self.paramInit)
			f.write(self.authinit)
			f.close()		

	def get_stream_params(self):
		return self.streamParams

	def get_ignore_params(self):
		return self.ignoreParams

	def get_ignore_retweets(self):
		return self.ignoreRetweets

	def is_quote(self, str):
		chars = False
		for c in str:
			if c != ' ' and c != '#' and c != '':
				chars = True
			if not chars and c == '#':
				return True
		return False


	def split_params(self, str):
		s = str.rstrip().replace(',','').split(' ')
		s = [x for x in s if x != '']
		return s

