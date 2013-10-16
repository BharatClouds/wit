#!/usr/bin/env python
import pycurl
import cStringIO
import json
from pygsr import Pygsr
import os
import wolframalpha


def witAI():
	#loading pygsr Python google speach recognition
	speech = Pygsr()
	raw_input("Ready ?")
	speech.record(5) # duration in seconds (3)
	try:
		phrase, complete_response = speech.speech_to_text('en_US') # select the language
	except:
		phrase = "Tell me a joke !"
	print phrase
	
	phrase = phrase.strip().replace(" ","%20").encode('ascii') #if not ascii, curl crashes

	#Wit.ai curl URL
	curl_url = "https://api.wit.ai/message?q=%s"%phrase
	#Auth headers
	curl_header = ["Authorization: Bearer YW3P2YITCYYXGHVLMIE7R7G7BBJODBG4"]
	#debug
	print curl_url
	answer = get_curl(curl_url,curl_header)
	print answer
	result = json.loads(answer) #parse answer
	return result

def get_curl(Url,Header=None,UserAgent=None):
	"Send a curl request and return the output."
	#create a buffer to get the anwser
	buf = cStringIO.StringIO()
	#loading Curl
	c = pycurl.Curl()
	c.setopt(c.URL, Url) #set URL
	c.setopt(c.WRITEFUNCTION, buf.write) #set answer buffer
	if Header:
		c.setopt(c.HTTPHEADER,Header) #set auth headers
	if UserAgent:
		c.setopt(pycurl.USERAGENT, UserAgent)
	c.perform() #perform request
	answer = buf.getvalue() #read anwser
	buf.close()
	return answer
	
def get_joke():
	"Get a random Joke"
	url = "http://api.icndb.com/jokes/random"
	answer = get_curl(url)
	result = json.loads(answer)
	print result
	return result

def get_intent(result):
	"This function taketh a result from Wit.AI and take action according to the result"
	intent = result['outcome']['intent']
	if intent == "music_and_mood":
		if result['outcome']['entities'].has_key('mood'):
			mood = result['outcome']['entities']['mood']['body']
		else:
			print "I did not get the mood you are in, please repeat !"
			speak_google("I did not get the mood you are in, please repeat !")
			return True
		print "opening StereoMood"
		url = "http://www.stereomood.com/mood/%s"%mood
		os.system("chromium-browser %s"%url)
	elif intent=="joking":
		result = get_joke()
		joke = result['value']['joke']
		category = ""
		if len(category) > 0:
			category = result['value']['categories'][0]
		speak_google("Here is a %s joke for you !"%category)
		speak_google(joke)
		return True
	elif intent=="questions":
		if result['outcome']['entities'].has_key('wolfram_search_query'):
			WA_query = result['outcome']['entities']['wolfram_search_query']['value']
		else:
			print "I did not get your question, could you please repeat !"
			speak_google("I did not get your question, could you please repeat !")
			return True
		answer = query_wolframalpha(WA_query)
		speak_google(answer)
		return True
	
def speak(text,voice="mb/mb-us1"):
	"Send text to be spoken by espeak"
	os.system('espeak -v %s "%s"'%(voice,text))

def speak_google(text,language="en"):
	text = text.strip().replace(" ","+").replace("&quot;","quote").replace(';','')
	texts = []
	imax = len(text)/100
	i=0
	if len(text) > 100:
		while i <= imax:
			texts.append(text[i*100:(i+1)*100])
			i+=1
	else:
		texts.append(text)
	print texts
	for i in range(len(texts)):
		url = "http://translate.google.com/translate_tts?tl=%s&q=%s"%(language,text)
		url = url.encode('ascii')
		print url
		anwser = get_curl(url,UserAgent='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
		f = open("audio-%s.mp3"%i,'w')
		f.write(anwser)
		f.close()
	for i in range(len(texts)):
		os.system("play audio-%s.mp3"%i)
	#curl -A "Mozilla" "http://translate.google.com/translate_tts?tl=en&q=hello+world" > audio.mp3

def text_to_google_tts(text):
	"May no be of use ..."

def query_wolframalpha(text):
	app_id = "8L7T9J-72ALWV56VJ"
	client = wolframalpha.Client(app_id)
	res = client.query(text)
	if len(res.pods)>1:
		result = res.pods[1].text.replace('|',' is ').replace('\n','. ').replace('  ',' ')
	else:
		result = "I could not find an answer to your question. I am sorry. may you can retry ?"
	return result

result = witAI()

while get_intent(result):
	result = witAI()
