import requests
# accessing sites

from bs4 import BeautifulSoup
from pathlib import Path

matchID = 498627
url = f"https://www.vlr.gg/{matchID}/"

outputPath = Path(f"match{matchID}.html")        
# creates a new file named after the vlr index  

headers = {"User-Agent": "TEST"}

# resp stands for "response object" from the request
resp = requests.get(url, headers=headers, timeout =20) # 20 second timeout
resp.raise_for_status()
# raise for status raises a "requests.HTTPError" if response status is an error, simple indicator of failure

Path("scraperpage.html").write_text(resp.text, encoding="utf-8")

htmlPage = Path("scraperpage.html").read_text(encoding="utf-8", errors = "replace")
soupPage = BeautifulSoup(htmlPage, "html.parser")

# getting all players who participated

# select the first "node" for the html class beginning with the text 
# '.vm-stats-game[data-game-id="all"]'
# although we should specify it starts at <div and ends with </div,
# the text parameters already is enough, and we need all the data in the selected section anyways.
overall = soupPage.select_one('div.vm-stats-game.mod-active[data-game-id="all"]')
if not overall:
    raise ValueError("overall stats block not found")

# now, for each row/"line" of html code in the overall selection, we select every
# instance of "table.wf-table..." and then NARROW the selection down to tbody tr
# contrary to the first selection, we do this because theres a bunch of junk elements
# in the overall selection that aren't useful.

outputRows = []
headerWritten = False
statLabels = []

for table in overall.select("table.wf-table-inset.mod-overview"):
    if not headerWritten:
        headerLabels = ("Rating", "ACS", "Kills", "Deaths", "Assists", "+/-", "KAST", "ADR", "HS%", "FK", "FD", "+/-")
        headerLine = "\t\t".join(headerLabels)
        outputRows.append(headerLine)
        headerWritten = True

    for row in table.select("tbody tr"):
        playerNameDiv = row.select_one("td.mod-player div.text-of")
        # new selection returns a tag object including the section starting from anything with "text-of" inside something starting with td with "mod-player"

        playerTeamDiv = row.select_one("td.mod-player div.ge-text-light")
        # similar logic but for the team text

        if not (playerNameDiv and playerTeamDiv):
            continue

        statValues = []
        for cell in row.select("td.mod-stat"):
            # for the current selection, get each cell in the table starting wtih td and including "mod-stat"
            valueSpan = cell.select_one(".side.mod-both") or cell.select_one(".side.mod-side.mod-both")
            # get the value at that cell corresponding to the player's combined stats from both attack/defending sies

            value = valueSpan.get_text(strip=True) if valueSpan else cell.get_text(" ", strip=True)
            # strip that tag of all the unnessary stuff
            # like <span class="side mod-side mod-both">1.28</span> becomes 1.28

            statValues.append(value)
            # add to list of all the stats for a player

        # create a "line" of text first with player name/team, then with their stats
        playerLine = f"{playerTeamDiv.get_text(strip=True)}\t\t{playerNameDiv.get_text(strip=True)}"
        statsLine = "\t\t".join(statValues)

        # add lines of text to the output file
        outputRows.append(playerLine)
        outputRows.append(statsLine)


outputPath.write_text("\n".join(outputRows), encoding="utf-8")
