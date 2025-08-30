from discord_webhook import DiscordWebhook,DiscordEmbed
import requests
import json
import re
import os
import dotenv
import datetime
from selenium import webdriver as wdr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

sentlogs="./hooks/hook/contentlist.log"
errlogs="./hooks/hook/err.log"
if not os.path.exists(sentlogs):
  with open(sentlogs,"w") as ff:
    pass
if not os.path.exists(errlogs):
    with open(errlogs,"w") as ff:
        pass
def rawshowtitle(title):
    return ''.join(a for a in title if a.isalnum())

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
try:
  idexclude=eval(os.environ['Showswatching'])
  print(idexclude)
  rune=os.environ['Rune']
  print(rune)
  hooklink=os.environ['Hooksecret']
  print(hooklink)
  showid=eval(os.environ['Getlistonline'])
  print(showid)
except Exception as ee:  
  with open(errlogs,"a+") as ff:
    err=f"{datetime.datetime.today()}||Err: {ee}\n"
    ff.write(err)
    exit()

query = '''
query ($id: Int) {
  Page {
    pageInfo {
      hasNextPage
    }
    mediaList(userId: $id, type: ANIME, status_in: [CURRENT, REPEATING]) {
      media {
        title {
          romaji
	  english
        }
        siteUrl
      }
    }
  }
}
'''
try:
	if showid:
		ids=eval(os.environ['Idlist'])
		url = 'https://graphql.anilist.co'
		showlist={'eng':[],'romaji':[],'romajii':[]}
		for idd in ids:
			variables = {'id': idd }
			requestdata = requests.post(url, json={'query': query, 'variables': variables}).json()
			for show in requestdata['data']['Page']['mediaList']:
				nam=[show['media']['title']['romaji'],show['media']['title']['english']]
				if nam[0] is None:
					nam[0]=""
				if nam[1] is None:
					nam[1]=""
				if nam[0] not in showlist['romaji']:
					showlist['romajii'].append(rawshowtitle(nam[0].upper()))
					showlist['eng'].append(rawshowtitle(nam[1].upper()))
					showlist['romaji'].append(nam[0])
			
					
		idexclude=showlist
except Exception as ee:  
  with open(errlogs,"a+") as ff:
    err=f"{datetime.datetime.today()}||Err: {ee}\n"
    ff.write(err)
def news():
	link="https://xcancel.com/umamusume_eng"
	options=Options()
	options.add_argument("--headless")
	pageviewer=wdr.Firefox(options=options)
	pageviewer.get(link)
	WebDriverWait(pageviewer,10)
	pageviewer.refresh()
	rawcontent=pageviewer.page_source
	with open(sentlogs,"w") as ff:
		ff.write("\n")
		ff.write(str(rawcontent))
	
def new():
    link = 'https://animepahe.com/api?m=airing&page=1'
    options = Options()
    options.add_argument("--headless")
    pageviewer = wdr.Firefox(options=options)
    pageviewer.get(link)
    WebDriverWait(pageviewer, 8)
    pageviewer.refresh()
    rawcontent=pageviewer.page_source
	print(rawcontent)
    jsoncontent=re.findall('<div id="json">(.*?)</div></div>', rawcontent, re.DOTALL)[0]
    response =json.loads(jsoncontent)
    allshowsreleased=[
        [
            '{}/{}'.format(x['anime_session'], x['session']),
            x['episode'],
            x['anime_title'],x['snapshot']
        ] for x in response['data']
    ]
	
    showsreleased=[]
    for entry in allshowsreleased:
	    title=rawshowtitle(entry[2].upper())
	    if title in idexclude['romajii']:
		    showsreleased.append(entry)
		    continue
			
	    if title in idexclude['eng']:
		    entry[2]=idexclude['romaji'][idexclude['eng'].index(title)] #aovid eng
		    showsreleased.append(entry)
			
    return showsreleased

def hookgenerate(contentlist):
  with open(sentlogs,"+r") as ff:
    sentshows=ff.readlines()
  for show in contentlist:
    if f"{show[2]} - Episode {show[1]}\n" in sentshows:
      continue
    try:
      text=f"# {rune}  |  [{show[2]} - Episode {show[1]}](<https://animepahe.com/play/{show[0]}>)\n[Main Page](https://animepahe.com/play/{show[0]}*)"
      webhook = DiscordWebhook(url=hooklink,content=text)
      webhook.execute()
      entrno=len(sentshows)
      title=f"{show[2]} - Episode {show[1]}\n"
      if entrno>18:
        with open(sentlogs,"w") as ff:
          newsshow=''.join(sentshows[8:])
          ff.write(newsshow)
        with open(errlogs,"w") as ff:
          pass
        
      with open(sentlogs,"a+") as ff:
        ff.write(title)
    except Exception as ee:
      with open(errlogs,"a+") as ff:
                err=f"{datetime.datetime.today()}||Webhook Err: {ee}\n"
                ff.write(err)



try:
  hookgenerate(new())
  news()
except Exception as ee:
  print(ee)
  with open(errlogs,"a+") as ff:
    err=f"{datetime.datetime.today()}||Err: {ee}\n"
    ff.write(err)
