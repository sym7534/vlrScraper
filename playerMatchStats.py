import requests
# accessing sites

from bs4 import BeautifulSoup
from pathlib import Path

matchID = 498622
url = f"https://www.vlr.gg/{matchID}/"

outputPath = Path(f"vlrScraper/match{matchID}.html")        
# creates a new file named after the vlr index  

headers = {"User-Agent": "TEST"}

# resp stands for "response object" from the request
resp = requests.get(url, headers=headers, timeout =20) # 20 second timeout
resp.raise_for_status()
# raise for status raises a "requests.HTTPError" if response status is an error, simple indicator of failure

Path("vlrScraper/scraperpage.html").write_text(resp.text, encoding="utf-8")

htmlPage = Path("vlrScraper/scraperpage.html").read_text(encoding="utf-8", errors = "replace")
soupPage = BeautifulSoup(htmlPage, "html.parser")

# getting all players who participated

# select the first "node" for the html class beginning with the text 
# '.vm-stats-game[data-game-id="all"]'
# although we should specify it starts at <div and ends with </div,
# the text parameters already is enough, and we need all the data in the selected section anyways.
overall = soupPage.select_one('.vm-stats-game[data-game-id="all"]')

# now, for each row/"line" of html code in the overall selection, we select every
# instance of "table.wf-table..." and then NARROW the selection down to tbody tr
# contrary to the first selection, we do this because theres a bunch of junk elements
# in the overall selection that aren't useful.

outputRows = []

for row in overall.select("table.wf-table-inset.mod-overview tbody tr"):
    playerNameDiv = row.select_one("td.mod-player div.text-of")
    # new selection returns a tag object including the section starting from anything with "text-of" inside something starting with td with "mod-player"
    
    playerTeamDiv = row.select_one("td.mod-player div.ge-text-light")
    # similar logic but for the team text

    if playerNameDiv and playerTeamDiv: # idk, maybe this logic might break (?)

        # check if we actually found code for a name, then print that name.
        # print(playerNameDiv.get_text(strip=True))
        outputRows.append(f"{playerTeamDiv.get_text(strip=True)}\t{playerNameDiv.get_text(strip=True)}")

outputPath.write_text("\n".join(outputRows), encoding = "utf-8")