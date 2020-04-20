import json
import matplotlib.pyplot as plt
import numpy as np

# Import Minion/ID data
with open(r"Resources\minionDataDict.json", 'r') as file:
    mData = json.load(file)

# Import bazaar prices
with open(r"Resources\bazaarPrices.json", 'r') as file:
    prices = json.load(file)

# Import merchant prices
with open(r"Resources\merchantSellValues.json", 'r') as file:
    merchSellValues = json.load(file)

### MINION LEVEL SELECTION
# Set your desired minion level starting from 0
# So a level 5 minion has lvl=4
# (Note: you can set max level by setting lvl=-1)
lvl = -1 # Max level

### Fuel Multiplier Setup
fuel = 1.25 # Ench Lava Bucket

#### Compute yields from each minion
baseProfits = {}
enchProfits = {}
superEnchProfits = {}
merchProfits = {}
for m in mData.keys():
    curr = mData[m] # Current minion
    breaksPerH = (3600 / curr["minionData"]["delays"][lvl]) * fuel * 0.5

    # Compute Diamond Spreading profits (selling ench diamonds to Bazaar)
    if curr["minionData"]["diamondSpreading"]:
        diaBonus = 2 * breaksPerH * 0.1 * prices["ENCHANTED_DIAMOND"] / 160
        merchDiaBonus = 2 * breaksPerH * 0.1 * merchSellValues["DIAMOND"]["merchSellValue"]

    # Fish minion only has one type of action, (not break or place)
    if m == 'Fish':
        breaksPerH *= 2

    # Compute yields from minons which generate multiple items differently
    if not mData[m]["minionData"]["multiYield"]:
        basePerH = curr["items"]["0"]["actionYield"] * breaksPerH
        basePrice = prices.get(curr["items"]["0"]["gameID"], 0)
        baseProfits[m] = basePerH * basePrice + diaBonus

        # Compute Merchant Profits
        if curr["items"]["0"]["gameID"]:
            merchPrice = merchSellValues[curr["items"]["0"]["gameID"]]["merchSellValue"]
        else:
            merchPrice = 0
            print(f"[ERROR] Merchant Price for {m} Minion Not found")
        merchProfits[m] = basePerH * merchPrice + merchDiaBonus

        # Enchanted Item Profits
        if "1" in curr["items"]:
            enchPerH = basePerH / curr["items"]["1"]["craft"]["number"]
            enchPrice = prices.get(curr["items"]["1"]["gameID"], 0)
            enchProfits[m] = enchPerH * enchPrice + diaBonus

        # Super Enchanted Item Profits
        if "2" in curr["items"]:
            superEnchPerH = basePerH / curr["items"]["2"]["craft"]["number"]
            superEnchPrice = prices.get(curr["items"]["2"]["gameID"], 0)
            superEnchProfits[m] = superEnchPerH * superEnchPrice + diaBonus

    else:
        baseProfit = 0
        merchProfit = 0
        for i in range(len(curr["items"]["0"])):
            basePerH = curr["items"]["0"][i]["actionYield"] * breaksPerH
            basePrice = prices.get(curr["items"]["0"][i]["gameID"], 0)
            baseProfit += basePerH * basePrice

            if curr["items"]["0"][i]["gameID"]:
                merchPrice = merchSellValues[curr["items"]["0"][i]["gameID"]]["merchSellValue"]
            else:
                merchPrice = 0
                print(f"[ERROR] Merchant Price for {m} Minion Not found")
            merchProfit += merchPrice * basePerH

        baseProfits[m] = baseProfit + diaBonus
        merchProfits[m] = merchProfit + merchDiaBonus

        # Enchanted Item Profits
        if "1" in curr["items"]:
            enchProfit = 0
            for i in range(len(curr["items"]["1"])):
                enchPerH = curr["items"]["0"][i]["actionYield"] * breaksPerH / curr["items"]["1"][i]["craft"]["number"]
                enchPrice = prices.get(curr["items"]["1"][i]["gameID"], 0)
                enchProfit += enchPerH * enchPrice
            enchProfits[m] = enchProfit + diaBonus

        # Super Enchanted Item Profits
        if "2" in curr["items"]:
            superEnchProfit = 0
            for i in range(len(curr["items"]["2"])):
                superEnchPerH = curr["items"]["0"][i]["actionYield"] * breaksPerH / curr["items"]["2"][i]["craft"]["number"]
                superEnchPrice = prices.get(curr["items"]["2"][i]["gameID"], 0)
                superEnchProfit += superEnchPerH * superEnchPrice
            superEnchProfits[m] = superEnchProfit + diaBonus

### Output data to JSON file
typesOutput = {}
for k in mData.keys():
    typesOutput[k] = {
    "base": baseProfits.get(k, 0),
    "ench": enchProfits.get(k, 0),
    "superEnch": superEnchProfits.get(k, 0),
    "merch": merchProfits.get(k, 0)
    }

# Save to file
with open(r"JSON_Graph_Data\typesData.json", 'w') as file:
    json.dump(typesOutput, file, indent=3)
    print("Saved Types data to file")
