# scrapetube code, moved from juypter

# !pip install scrapetube

import scrapetube

videos = scrapetube.get_playlist("PLaMHyq8hhBW35Z9ZP0LjJp0M80Ndz3rE_")

ids = []

for video in videos:
    ids.append(video['videoId'])

print(ids)