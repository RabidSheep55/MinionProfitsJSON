import json
import matplotlib.pyplot as plt
import numpy as np

# Import Minion/ID data
with open(r"Resources\minionDataDict.json", 'r') as file:
    mData = json.load(file)

# Import bazaar prices
with open(r"Resources\bazaarPrices.json", 'r') as file:
    prices = json.load(file)

### MINION LEVEL SELECTION
# Set your desired minion level starting from 0
# So a level 5 minion has lvl=4
# (Note: you can set max level by setting lvl=-1)
lvl = -1 # Max level

#### Compute yields from each minion
enchProfits = {}
# Iterate through every minion
for m in mData.keys():
    curr = mData[m]
    breaksPerH = (3600 / curr["minionData"]["delays"][lvl]) * 0.5

    # Compute Diamond Spreading profits (selling ench diamonds)
    if curr["minionData"]["diamondSpreading"]:
        diaBonus = 2 * breaksPerH * 0.1 * prices["ENCHANTED_DIAMOND"] / 160

    # Fish minion only has one type of action, (not break or place)
    if m == "Fish":
        breaksPerH *= 2

    # Compute yields from minons which generate multiple items differently
    # Only concerned with the enchanted type sold here
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

#### Sort minons by profit
# keys = list(enchProfits.keys())
profits = [[key, value] for key, value in enchProfits.items()]
# for k in keys:
#     profits += [(k, enchProfits.get(k, 0))]

profits.sort(key= lambda a: a[1], reverse=True)
newKeys = [profit[0] for profit in profits]
ench = np.array([profit[1] for profit in profits])

#### Compute effect of Fuel Bonuses
wheelPricePerH = prices.get("HAMSTER_WHEEL", 0)/24
wheelBonus = 0.5
wheelProfit = ench*(wheelBonus+1) - wheelPricePerH

catalystPricePerH = prices.get("CATALYST", 0)/5
catalystBonus = 3
catalystProfit = ench*catalystBonus - catalystPricePerH

fleshPricePerH = prices.get("FOUL_FLESH", 0)/3
fleshBonus = 0.9
fleshProfit = ench*(fleshBonus+1) - fleshPricePerH

lavaBonus = 0.25
lavaProfit = ench*(lavaBonus+1)

#### Output data to JSON file
fuelsOutput = {}
for i in range(len(newKeys)):
    fuelsOutput[newKeys[i]] = {
        "base": ench[i],
        "wheel": wheelProfit[i],
        "catalyst": catalystProfit[i],
        "flesh": fleshProfit[i],
        "bucket": lavaProfit[i]
    }

# Save to file
with open(r"JSON_Graph_Data\fuelsData.json", 'w') as file:
    json.dump(fuelsOutput, file, indent=3)
    print("Saved Fuel data to file")
