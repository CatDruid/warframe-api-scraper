import requests
import json
from timeit import default_timer as timer
from datetime import timedelta
from pathlib import Path

#Docs https://warframe.market/api_docs
#Asserts https://warframe.market/static/assets

#region Types

#endregion


#region API Calls
API = "https://api.warframe.market/v1/"

def getAllItems():

    '''
    Fetch all items
    '''

    url = f'{API}items'
    params = {'Language':'en'}
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def getItemOrder(itemURL: str):

    '''
    Fetch orders for itemURL 
    '''

    url = f"{API}items/{itemURL}/orders"
    params = {}
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print("Error:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def getItem(itemURL: str):

    '''
    Fetch item info of itemURL
    '''

    url = f"{API}items/{itemURL}"
    params = {}
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print("Error:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
#endregion


def parseWhiteList(sets: dict,whiteList: list) -> dict:    

    '''
    Deletes all keys and values from the dictionary that is not part of whiteList on items
    '''

    iv = 0
    for i in sets["payload"]["item"]["items_in_set"]:
        for k in sets["payload"]["item"]["items_in_set"][iv].copy():
            if k not in whiteList:
                sets["payload"]["item"]["items_in_set"][iv].pop(k)
        iv += 1
    return sets

def parseOWhiteList(sets:dict ,whiteList: list) -> dict:    

    '''
    Deletes all keys and values from the dictionary that is not part of whiteList on orders
    '''

    iv = 0
    for i in sets["payload"]["orders"]:
        for k in sets["payload"]["orders"][iv].copy():
            if k not in whiteList:
                sets["payload"]["orders"][iv].pop(k)
        iv += 1
    return sets

def checkOrderType(orderDict: dict, oType: str) -> dict:

    '''
    Checks if its a buy or a sell order on warframe.market
    '''

    newOrderDict = {"payload":{"orders": []}}
    try:
        for obj in orderDict["payload"]["orders"]:
            if obj["order_type"] == oType and obj["user"]["status"] == "ingame":
                newOrderDict["payload"]["orders"].append(obj)
    except:
        print("Error getting order type")

    return newOrderDict

def getLowestPlat(orderDict: dict) -> int:

    '''
    Takes the dictionary from getItemOrder and returns the lowest price of that item on warframe.market
    '''

    lowplat = 9000
    for i in orderDict["payload"]["orders"]:       
        if lowplat != 9000:
            if lowplat > i["platinum"]:
                lowplat = i["platinum"]
               # print(f"lowerd to {lowplat}")
        else:
            lowplat = i["platinum"]

    return int(lowplat)

def getHighestPlat(orderDict: dict) -> int:

    '''
    Takes the dictionary from getItemOrder and returns the lowest price of that item on warframe.market
    '''

    highplat = 9000
    for i in orderDict["payload"]["orders"]:       
        if highplat != 9000:
            if highplat < i["platinum"]:
                highplat = i["platinum"]
               # print(f"lowerd to {lowplat}")
        else:
            highplat = i["platinum"]

    return int(highplat)


#region Update Jsons
def updateSetsJson(whiteList: list) -> None:

    '''
    Takes a whiteList of keys to keep from the json
    Creates sets.json from all of the sets in items.json
    '''

    start = timer()
    amount = 0
    sets = 0
    itemDict = []
    tempsets = []
    with open("items.json", "r") as itemjson:
        itemDict = json.load(itemjson)

    for i in itemDict["payload"]["items"]:
        amount +=1
        #print(itemDict["payload"]["items"][i])
        urlName = i["url_name"]
        
        if urlName.find("set") != -1:
            sets += 1
            tempsets.append(parseWhiteList(getItem(urlName),whiteList))

    if tempsets:     
        with open("sets.json", "w") as setsjson:
            json.dump(tempsets, setsjson)
    else:
        print("Failed to fetch itemset")

    end = timer()
    delta = timedelta(seconds=end - start)
    print(f"Updating sets json took: \n {delta}")

def updateItemListJson():

    '''
    Fetches the itemlist from https://api.warframe.market/v1/items 
    and put it in items.json
    '''

    posts = getAllItems()
    if posts:
        with open('items.json', 'w') as f:
            json.dump(posts, f)
    else:
        print('Failed to fetch items from API.')


def updateBestPriceJson(iType: str,urlName: str, ROI: int = 0, trades: dict = None ,initialInvest: int = 0) -> None:
    '''
    Creates "best.json" with all information provided and json provided from grabbing url_name on api
    '''

    match iType:

        case "frame":
            file = "bestFrame.json"

        case "weapon":
            file = "bestWeapon.json"

        case _:
            print("ERROR: iType not 'frame' or 'weapon'")
            return None

    #Sets inital variables
    createDict = {"payload":{}}
    whiteList = ["set_root","thumb","icon","url_name","id","tags","trading_tax","en"]
    itemJson = getItem(urlName)
    parsedItemsJson = parseWhiteList(itemJson, whiteList)

    
    for item in parsedItemsJson["payload"]["item"]["items_in_set"]:
        if item["set_root"] == True:
            createDict["payload"].update(item)
            if ROI > 0:
                createDict["payload"]["Platinum ROI"] = ROI
            if initialInvest > 0:
                createDict["payload"]["Initial Invest"] = initialInvest
    
    with open(file, "w") as temp:
        json.dump(createDict, temp)
    


#endregion

#region ROI
def getROIFrame(itemURL: str, checkBuyorder = False) -> tuple[int, int]:

    '''
    Gets the ROI of the provided warframe itemURL
    '''

    #Vars
    itemSetJson = getItem(itemURL)
    setOrderJson = getItemOrder(itemURL)
    setId = itemSetJson["payload"]["item"]["id"]
    tempItemSet = {}
    itemPriceList = []
    #setsPrice = getLowestPlat(parseOWhiteList(checkOrderType(setOrderJson,"sell"),["platinum"]))

    


    #Json
    with open("sets.json", "r") as setsJson:
        setsDict = json.load(setsJson)
    #print(setId)

    for obj in setsDict:
        if obj["payload"]["item"]["id"] == setId:
            tempItemSet.update(obj["payload"]["item"])
            #print("added asset")
    
    for obj in tempItemSet["items_in_set"]:
        if obj["set_root"] == False:
            itemPriceList.append(getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder(obj["url_name"]),"sell"),["platinum"])))


    if checkBuyorder == True:
        price = getHighestPlat(parseOWhiteList(checkOrderType(setOrderJson,"buy"),["platinum"]))
    else:
        price = getLowestPlat(parseOWhiteList(checkOrderType(setOrderJson,"sell"),["platinum"]))

    rOI = price - sum(itemPriceList) - 2
   # print(f"Roi on {itemURL} is {rOI} platinum")
    return rOI, sum(itemPriceList)
   # print(sum(itemPriceList))

 #   print(setsPrice)

    #print(tempItemSet)

def getROIWeapon(itemURL: str, oType: str) -> tuple[int, int]:

    '''
    Get the ROI from the provided weapon itemURL
    '''

    #Vars
    itemSetJson = getItem(itemURL)
    setOrderJson = getItemOrder(itemURL)
    setId = itemSetJson["payload"]["item"]["id"]
    setsPrice = getLowestPlat(parseOWhiteList(checkOrderType(setOrderJson,oType),["platinum"]))
    tempItemSet = {}
    itemPriceList = [0]

    #Json
    with open("sets.json", "r") as setsJson:
        setsDict = json.load(setsJson)
    #print(setId)

    #get Set ID
    for obj in setsDict:
        if obj["payload"]["item"]["id"] == setId:
            tempItemSet.update(obj["payload"]["item"])
            #print("added asset")
    
    #Make Shopping list
    for obj in tempItemSet["items_in_set"]:
        urlName = str(obj["url_name"])
        if obj["set_root"] == False:
            if obj["quantity_for_set"] > 1:
                totPrice = int(obj["quantity_for_set"]) * getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder(obj["url_name"]),"sell"),["platinum"]))
                print(f"More than one{urlName}")
                itemPriceList.append(totPrice)
            else:
                itemPriceList.append(getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder(obj["url_name"]),"sell"),["platinum"])))

    rOI = setsPrice - sum(itemPriceList) - 2
   # print(f"Roi on {itemURL} is {rOI} platinum")
    return rOI, sum(itemPriceList)
   # print(sum(itemPriceList))

 #   print(setsPrice)

    #print(tempItemSet)

def rOICheckAllWeapons() -> None:

    '''
    Checks all of the ROI on all weapons in sets.json
    '''

    start = timer()
    currentMP = ""
    currentROI = 0
    framecount = 0
    with open("sets.json", "r") as setsJson:
        sets = json.load(setsJson)

    for i in sets:
        if "weapon" in i["payload"]["item"]["items_in_set"][0]["tags"]:
            for items in i["payload"]["item"]["items_in_set"]:
                if items["set_root"] == True:
                    x = getROIWeapon(items["url_name"],"sell")
                    urlName = str(items["url_name"])
                    if currentMP == "":                        
                        currentROI = x
                        currentMP = items["url_name"]
                    #    print("init roi")
                        print(f"New best is {urlName} with roi of {x}")
                    elif x > currentROI:
                        currentROI = x
                        currentMP = items["url_name"]
                        print(f"New best is {urlName} with roi of {x}")
                    else:
                        print(f"{urlName} is worse, Roi was {x}")
                        continue

                    framecount += 1
    resultString = f"{currentMP} is most profitable with an ROI of {currentROI} platinum"
    print("-" * len(resultString))
    print(resultString)
    print("-" * len(resultString)) 
    #print(framecount)
    end = timer()
    delta = timedelta(seconds=end - start)
    print(f"Getting best weapon trade took: \n {delta}")
    return None


def rOICheckAllFrames() -> None:

    '''
    Checks the ROI on all of the warframes in "sets.json" 
    Calls updateBestPriceJson with flag "frame" to generate "bestFrame.json"   
    '''
    
    start = timer()
    currentMP = ""
    currentROI = 0
    framecount = 0
    with open("sets.json", "r") as setsJson:
        sets = json.load(setsJson)

    for i in sets:
        if "warframe" in i["payload"]["item"]["items_in_set"][0]["tags"]:
            for items in i["payload"]["item"]["items_in_set"]:
                if items["set_root"] == True:
                    x = getROIFrame(items["url_name"])[0]
                    urlName = str(items["url_name"])
                    if currentMP == "":                        
                        currentROI = x
                        currentMP = items["url_name"]
                    #    print("init roi")
                        print(f"New best is {urlName} with roi of {x}")
                    elif x > currentROI:
                        currentROI = x
                        currentMP = items["url_name"]
                        print(f"New best is {urlName} with roi of {x}")
                    else:
                        print(f"{urlName} is worse, Roi was {x}")
                        continue

                    framecount += 1

    end = timer()
    
    fastreturn = getROIFrame(str(currentMP), True)[0]
    initialInvest = getROIFrame(str(currentMP), False)[1]
    resultString = f"{currentMP} is most profitable with an ROI of {currentROI} platinum"
    updateBestPriceJson("frame",currentMP,currentROI,None,initialInvest)
    print("-" * len(resultString))
    print(resultString)
    print(f"Fast return:{fastreturn}")
    print("-" * len(resultString))
    delta = timedelta(seconds=end - start)
    print(f"Getting best frame trade took: \n {delta}") 
    #print(framecount)
    return resultString
#endregion

#region Main
def main():

    #Check if items.json and sets.json are present
    itemJsonPath = Path("items.json")
    setsJsonPath = Path("sets.json")
    if itemJsonPath.is_file() == False:
        updateItemListJson()
    
    if setsJsonPath.is_file() == False:
        updateSetsJson()

    #Warn if bestFrame.json and bestWeapon is not present
    bestFrameJsonPath = Path("bestFrame.json")
    if bestFrameJsonPath.is_file() == False:
        print(f"ERROR:{bestFrameJsonPath} not found, Recomended to run rOICheckAllFrames()")

    bestWeaponJsonPath = Path("bestWeapon.json")
    if bestWeaponJsonPath.is_file() == False:
        print(f"ERROR:{bestWeaponJsonPath} not found, Recomended to run rOICheckAllWeapons() ")

    #whiteList = ["url_name","tags","id","ducats","mastery_level","set_root","trading_tax", "quantity_for_set"]
    #updateItemListJson()
    #rOICheckAllWeapons()
    rOICheckAllFrames()
    #updateSetsJson(whiteList)
    #updateBestPriceJson("frame","mag_prime_set",getROIFrame("mag_prime_set")[0], None, getROIFrame("mag_prime_set")[1])
    #oWhiteList = ["platinum"]
   # print(getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder("mag_prime_set"),"sell"),oWhiteList)))
   # with open("temp.json", "w") as tempJson:
   #    json.dump(checkOrderType(getItemOrder("quassus_prime_set"),"sell"), tempJson)
   # getROIFrame("wukong_prime_set")
   # tmp = getItemOrder("guandao_prime_set")
    #with open("temp.json", "w") as tmpJson:
    #    json.dump(tmp, tmpJson)

#endregion

if __name__ == '__main__':
    main()