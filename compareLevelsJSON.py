import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# Import Minion/ID data
with open(r"Resources\minionDataDict.json", 'r') as file:
    mData = json.load(file)

# Import bazaar prices
with open(r"Resources\bazaarPrices.json", 'r') as file:
    prices = json.load(file)

### Fuel Multiplier Setup
fuel = 1.25 # Ench Lava Bucket

#### Find each minion's profit rank based on level
# Init output dict
ranks = dict(zip(list(mData.keys()), [{"ranks":[], "values":[]} for m in mData.keys()]))

# Iterate for each minion level
for lvl in range(0, 11, 1):
    enchProfits = {}
    # Iterate for each minion
    for m in mData.keys():
        curr = mData[m] # Current minion
        breaksPerH = (3600 / curr["minionData"]["delays"][lvl]) * fuel * 0.5

        # Compute Diamond Spreading profits (selling ench diamonds to Bazaar)
        if curr["minionData"]["diamondSpreading"]:
            diaBonus = 2 * breaksPerH * 0.1 * prices["ENCHANTED_DIAMOND"] / 160

        # Fish minion only has one type of action, (not break or place)
        if m == "Fish":
            breaksPerH *= 2

        # Compute yields from minons which generate multiple items differently
        # We only consider selling enchanted items at the Bazaar
        if not curr["minionData"]["multiYield"]:
            if "1" in curr["items"]:
                enchPerH = curr["items"]["0"]["actionYield"] * breaksPerH / curr["items"]["1"]["craft"]["number"]
                enchPrice = prices.get(curr["items"]["1"]["gameID"], 0)
                enchProfits[m] = enchPerH * enchPrice + diaBonus

        else:
            if "1" in curr["items"]:
                enchProfit = 0
                for i in range(len(curr["items"]["1"])):
                    enchPerH = curr["items"]["0"][i]["actionYield"] * breaksPerH / curr["items"]["1"][i]["craft"]["number"]
                    enchPrice = prices.get(curr["items"]["1"][i]["gameID"], 0)
                    enchProfit += enchPerH * enchPrice
                enchProfits[m] = enchProfit + diaBonus

    # Now that all profits have been computed, sort them and find each minon's rank
    # keys = list(enchProfits.keys())
    profits = [[key, value] for key, value in enchProfits.items()]
    # for k in keys:
    #     profits += [(k, enchProfits.get(k, 0))]

    profits.sort(key= lambda a: a[1], reverse=True)
    newKeys = [profit[0] for profit in profits]

    # Save rank values in lists within the minion dict
    for i in range(len(newKeys)):
        ranks[newKeys[i]]["ranks"] += [i+1]
        ranks[newKeys[i]]["values"] += [enchProfits[newKeys[i]]]

# Save to file
with open(r"JSON_Graph_Data\levelData.json", 'w') as file:
    json.dump(ranks, file, indent=3)
    print("Saved Level data to file")
