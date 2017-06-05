from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import NameForm
import requests
import json
import httplib, urllib, base64

# Create your views here.

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

