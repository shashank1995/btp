from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import NameForm
import requests
import json
import httplib, urllib, base64

# Create your views here.

def tokenize(text): return re.findall('[a-z]+', text.lower()) 

Freq = {
	'does':1, 'it':1, 'use':1,
	'i':1, 'know':1, 'right':1,
	'fuck':1,
	'conduct':2, 'research':2, 'search':2, 'con':1, 'duct':1,
	'hi':3, 'there':2, 'hit':2, 'here':2, 'how':3, 'are':3, 'you':3,
	'ho':1,
	'a':3, 'them':2, 'anathema':1,
}

def joins(toks):
	if len(toks) < 2:
		yield toks
	else:
		for i in range(len(toks)):
			for j in range(i+1, len(toks)-i+1):
				pref = toks[:i] + [''.join(toks[i:i+j])]
				for suf in joins(toks[i+j:]):
					yield pref + suf

def nextword(str, ng1, l=1):
	for i in range(len(str)):
		for j in range(i+l, min(i+18, len(str))):
			if str[i:j] in ng1:
				return (str[:i], str[i:j], str[j:])
	return (str,'','')

def spl(str, ng1):
	if len(str) < 2:
		yield [str]
	else:
		i = 0
		while i <= len(str):
			pref,word,suf = nextword(str, ng1, i)
			if not word:
				yield [pref]
				break
			else:
				w = []
				if pref: w.append(pref)
				w.append(word)
				for sufx in spl(suf, ng1):
					if sufx:
						yield w + sufx
				i += len(word) + 1

def splits(toks, freq, g):
	score = dict()
	str = ''.join(toks)
	for i in range(len(str)+1):
		for j in range(i+1, len(str)+1):
			w = str[i:j]
			sc = freq.get(w, 0)
			if sc > 0:
				score[w] = sc
	print('  splits score=',score)
	ngrams = []
	for x,y in product(score.keys(), score.keys()):
		xi = str.index(x) + len(x)
		if str[xi:xi+len(y)] != y:
			continue
		ng = (x,y)
		sc = g.freq(ng)
		if sc > 0:
			ngrams.append(ng)
	print('  splits ngrams=',ngrams)

	ng1 = set([x for x,y in ngrams])
	ng2 = set([y for x,y in ngrams])

	def toks2ngrams(toks, size):
		size = min(len(toks), size)
		for ng in zip(*[toks[i:] for i in range(size)]):
			yield ng
	pop = []
	for s in spl(str, ng1):
		freq = sum([g.freq(x) for x in toks2ngrams(s, 3)])
		if freq:
			pop.append((tuple(s), freq))
	pop = sorted(pop, key=lambda x:x[1], reverse=True)
	print('  splits() pop=',pop)
	for p,_ in pop:
		yield p

def weight(tok):
	factor = 1 + len(tok)
	return round(Freq.get(tok,0) * factor, 1)

def correct(str):
	toks = tokenize(str)
	s = list(splits(toks, Freq))
	print('s=',s[:4])
	js0 = list(s)# + list(j)
	js1 = [(k, sum(map(weight, k))) for k in js0]
	js2 = sorted(js1, key=lambda x:x[1], reverse=True)
	print('js=',js2[:5])
	guess = str
	if js2 != []:
		guess,gscore = js2[0]
		oscore = sum(map(weight, toks))
		print('gscore=',gscore,'oscore=',oscore)
		if gscore > oscore * 2:
			guess = ' '.join(guess)
		else:
			guess = str
	return guess

if __name__ == '__main__':
	Tests = [
		'iknowright : i know right',
		'f u c k y o u : fuck you',
		'xxxhowareyouxxx : xxx how are you xxx',
		'con duct re search : conduct research',
		'hitherehowareyou : hi there how are you',
		'hithe re : hi there',
		'anathema : anathema'
	]
	passcnt = 0
	for t in Tests:
		str,exp = t.strip().split(' : ')
		print(str)
		res = correct(str)
		if res == exp:
			passcnt += 1
		else:
			print('*** FAIL: %s -> %s (%s)' % (str,res,exp))
	print('Tests %u/%u.' % (passcnt, len(Tests)))

def index(request):
	if request.method == 'GET':
		return render(request,'recommendation/btp_template.html')
	if request.method == 'POST':
		form = NameForm(request.POST)
		if form.is_valid():
			search_query = form.cleaned_data['search_query']
			var1 = "http://api.bing.com/osjson.aspx?query="
			var2 = var1 + search_query
			response = requests.get(var2)
			list1 = response.json()
			list2 = list1[1]
			headers = {
    				'Ocp-Apim-Subscription-Key': 'e2456c67477e480d9eba999fe5b49c34',
					}

			params = urllib.urlencode({
			    'q': search_query,
			    'count': '5',
			    'offset': '0',
			    'mkt': 'en-us',
			    'safesearch': 'Moderate',
			})

			try:
			    conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
			    conn.request("GET", "/bing/v5.0/search?%s" % params, "{body}", headers)
			    response = conn.getresponse()
			    data = response.read()
			    list3 = json.loads(data)
			    list4 = list3['webPages']
			    list5 = list4['value']
			    conn.close()
			except Exception as e:
				print("[Errno {0}] {1}".format(e.errno, e.strerror))
    		context = { 'list2' : list2 , 'list5' : list5}
		return render(request, 'recommendation/search_results_template.html', context)
	else:
		form = NameForm()

	return render(request, 'recommendation/btp_template.html', {'form': form})


def related(request, related_string):
		search_query = related_string
		var1 = "http://api.bing.com/osjson.aspx?query="
		var2 = var1 + search_query
		response = requests.get(var2)
		list1 = response.json()
		list2 = list1[1]
		headers = {
    			'Ocp-Apim-Subscription-Key': 'e2456c67477e480d9eba999fe5b49c34',
				}

		params = urllib.urlencode({
			'q': search_query,
			'count': '5',
			'offset': '0',
			'mkt': 'en-us',
			'safesearch': 'Moderate',
		})
		try:
			conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
			conn.request("GET", "/bing/v5.0/search?%s" % params, "{body}", headers)
			response = conn.getresponse()
			data = response.read()
			list3 = json.loads(data)
			list4 = list3['webPages']
			list5 = list4['value']
			conn.close()
		except Exception as e:
			print("[Errno {0}] {1}".format(e.errno, e.strerror))
		return render(request, 'recommendation/search_results_template.html', { 'list2' : list2 , 'list5' : list5})

