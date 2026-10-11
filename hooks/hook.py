from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import json
import re
import os
import time
import dotenv
import datetime

sentlogs = "./hooks/hook/contentlist.log"
errlogs = "./hooks/hook/err.log"
if not os.path.exists(sentlogs):
    with open(sentlogs, "w") as ff:
        pass
if not os.path.exists(errlogs):
    with open(errlogs, "w") as ff:
        pass


def rawshowtitle(title):
    return "".join(a for a in title if a.isalnum())


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
try:
    idexclude = eval(os.environ["Showswatching"])
    rune = os.environ["Rune"]
    hooklink = os.environ["Hooksecret"]
    showid = eval(os.environ["Getlistonline"])
except Exception as ee:
    with open(errlogs, "a+") as ff:
        err = f"{datetime.datetime.today()}||Err A: {ee}\n"
        ff.write(err)
        exit()
query = """
query ($idname: String) {
  Page {
    pageInfo {
      hasNextPage
    }
    mediaList(userName: $idname, type: ANIME, status_in: [CURRENT, REPEATING]) {
      media {
        title {
          romaji
   english
        }
        siteUrl
        episodes
        nextAiringEpisode {
          episode
      }
      coverImage{large}
    }
  }
}
}
"""
try:
    if showid:
        ids = eval(os.environ["Idlist"])
        #print(ids, type(ids))
        url = "https://graphql.anilist.co"
        showlist = {"eng": [], "romaji": [], "romajii": [],"epno":[]}
        showlist2=[]
        for idd in ids:
            variables = {"idname": idd}
            requestdata = requests.post(
                url, json={"query": query, "variables": variables}
            ).json()
            for show in requestdata["data"]["Page"]["mediaList"]:
                print("yes")
                nam = [
                    show["media"]["title"]["romaji"],
                    show["media"]["title"]["english"],
                ]
                if nam[0] is None:
                    nam[0] = ""
                if nam[1] is None:
                    nam[1] = ""
                if nam[0] not in showlist["romaji"]:
                    showlist["romajii"].append(rawshowtitle(nam[0].upper()))
                    showlist["eng"].append(rawshowtitle(nam[1].upper()))
                    showlist["romaji"].append(nam[0])
                    showlist["epno"].append(show["media"]["nextAiringEpisode"]["episode"])
                    showlist2.append([nam[0],show["media"]["nextAiringEpisode"]["episode"],show["media"]["coverImage"]["large"]])
                    print(showlist2)

        idexclude = showlist2
except Exception as ee:
    with open(errlogs, "a+") as ff:
        err = f"{datetime.datetime.today()}||Err B: {ee}\n"
        ff.write(err)


def hookgenerate(contentlist):
    with open(sentlogs, "+r") as ff:
        sentshows = ff.readlines()
    for show in contentlist:
        if f"{show[0]} - Episode {show[1]}\n" in sentshows:
            continue
        try:
            text = f"# {rune}  |  [{show[0]} - Episode {show[1]}]\n[Pic]({show[2]})"
            webhook = DiscordWebhook(url=hooklink, content=text)
            webhook.execute()
            entrno = len(sentshows)
            title = f"{show[2]} - Episode {show[1]}\n"
            if entrno > 18:
                with open(sentlogs, "w") as ff:
                    newsshow = "".join(sentshows[8:])
                    ff.write(newsshow)
                with open(errlogs, "w") as ff:
                    pass

            with open(sentlogs, "a+") as ff:
                ff.write(title)
        except Exception as ee:
            with open(errlogs, "a+") as ff:
                err = f"{datetime.datetime.today()}||Webhook Err: {ee}\n"
                ff.write(err)


try:
    hookgenerate(idexclude)
except Exception as ee:
    with open(errlogs, "a+") as ff:
        err = f"{datetime.datetime.today()}||Err C: {ee}\n"
        ff.write(f"{idexclude} {showlist} {err}")
