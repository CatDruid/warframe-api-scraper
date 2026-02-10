#region Imports
#Require manual install! TODO: requirements.txt
import requests # pip install requests

# in default pyhon. No need to install
import json 
from timeit import default_timer as timer
import time
from datetime import timedelta
from pathlib import Path
import psycopg2
import datetime

#endregion

#Docs https://warframe.market/api_docs
#Asserts https://warframe.market/static/assets/

#region Ansi Colors for terminal
cWhite = "\033[0;37m"
cRed = "\033[0;31m"
cGreen = "\033[0;32m"
cYellow = "\033[0;33m"
cBlue = "\033[0;34m"
cPurple = "\033[0;35m"
cCyan = "\033[0;36m"
#endregion

#region Database integration
#globals    


def dbInit():
    global cursor
    global conn
    try:
        conn = psycopg2.connect(
            dbname="warframe",
            user="postgres",
            password="*",
            host="192.168.0.110"
        )
        cursor = conn.cursor()
        print('connected sucessfully')
    except Exception as e:
        print(f'{cRed}Error: {cWhite}', e)

def db_execute(sql: str) -> bool:
    if conn is not None and cursor is not None:
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"{cRed}Error: {cWhite}", e) 

def dbInsertItems(dictionary: dict) -> None:
    if conn is not None and cursor is not None:
        megastring = ""
        for i in dictionary["data"]:
            key_string = ""
            value_string = ""
            for k in i.keys():
                match k:
                    case "id":
                        key_string += 'item_id'
                        value_string += f"'{i["id"]}'"
                    case "slug":
                        slug = i["slug"]
                        key_string += ', slug'
                        value_string += f",'{i["slug"]}'"
                    case "gameRef":
                        key_string += ', game_ref'
                        value_string += f",'{i["gameRef"]}'"
                    case "tags":
                            tag_string = ""
                            for tag in i["tags"]:
                                tag_string += tag + ","
                            key_string += ', item_tags'
                            value_string += f",'{{{tag_string[:-1]}}}'" 

                    case "bulkTradable":
                        key_string += ", bulk_tradable"
                        value_string += f',{i["bulkTradable"]}'
                    case "maxRank":
                        key_string += ', max_rank'
                        value_string += f',{i["maxRank"]}'
                    case "i18n":
                        key_string += ', item_name'
                        value_string += f",'{i["i18n"]["en"]["name"].replace("'","''")}'"

                        key_string += ', item_icon'
                        value_string += f",'{i["i18n"]["en"]["icon"]}'"

                        key_string += ', item_thumb'
                        value_string += f",'{i["i18n"]["en"]["thumb"]}'"
            #print(key_string)
            #print(value_string)
            #print(f"insert into items ({key_string}) values ({value_string});")
            megastring += f'insert into items ({key_string}) values ({value_string});'
            ''' try:
                cursor.execute(f'insert into items ({key_string}) values ({value_string});')
            except Exception as e:
                print(f"{cRed}Error: {cWhite}", e) 
            '''
            print(f"inserted: {slug}")
       # print(megastring)
        db_execute(megastring)

def db_insertItem(dictionary:dict):
     if conn is not None and cursor is not None:
        megastring = ""
        for i in dictionary["data"]:
            key_string = ""
            value_string = ""
            item_id = None
            slug = None
            game_ref = None
            item_tags = None
            setRoot = None
            set_parts = None
            ducats = None
            req_mastery_rank = None
            tradingTax = None
            tradable = None
            item_name = None
            item_description = None
            item_wiki = None
            item_icon = None
            item_thumb = None


def db_filterreturn(unf):
    return unf[0]

def db_insertROI(item_id: str, roi: int) -> None:
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    sqlString = f"insert into frame_roi(item_id,roi,fetch_date) values ('{item_id}',{roi},'{now}');"
    db_execute(sqlString)
#endregion

#region API Calls
API = "https://api.warframe.market/v2/"
ASSETS = "https://warframe.market/static/assets/"

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

    url = f"{API}orders/item/{itemURL}"
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

def testApi(iurl: str): 

    url = f'{API}{iurl}'
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

#endregion

#region Parsing / cleaning of dict/json
def parseWhiteList(sets: dict,whiteList: list) -> dict:    

    '''
    Deletes all keys and values from the dictionary that is not part of whiteList on items
    '''

    orderList = sets["data"]
    for k in orderList.copy():
        if k not in whiteList:
            orderList.pop(k)
    return sets

def parseOWhiteList(sets:dict ,whiteList: list) -> dict:    

    '''
    Deletes all keys and values from the dictionary that is not part of whiteList on orders
    '''

    orderList = sets["data"]
    for i in range(len(orderList)):
        for k in orderList[i].copy():
            if k not in whiteList:
                orderList[i].pop(k)
    return sets

def checkOrderType(orderDict: dict, oType: str) -> dict:

    '''
    Checks if its a buy or a sell order on warframe.market
    '''

    orderlist = []
    try:
        for obj in orderDict["data"]:
            if obj["type"] == oType and obj["user"]["status"] == "ingame":
                orderlist.append(obj)
    except:
        print("Error getting order type")

    newOrderDict = {"data":[]}
    newOrderDict["data"] = orderlist
    return newOrderDict

def getLowestPlat(orderDict: dict) -> int:

    '''
    Takes the dictionary from getItemOrder and returns the lowest price of that item on warframe.market
    '''

    lowplat = 9000
    
    for i in orderDict["data"]:       
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
    for i in orderDict["data"]:       
        if highplat != 9000:
            if highplat < i["platinum"]:
                highplat = i["platinum"]
               # print(f"lowerd to {lowplat}")
        else:
            highplat = i["platinum"]

    return int(highplat)

def itemIDToSlug(itemID: str) -> str:
    '''
    Docstring for itemIDToSlug
    
    :param itemID: Takes item ID
    :type itemID: string
    :return: Item Slug
    :rtype: string
    '''
    try:
        with open ("items.json", "r") as f:
            dict = json.load(f)
    except Exception as e:
        print("{cRed}Error: {cWhite}" + e)

    for i in dict["data"]:
        if i["id"] == itemID:
            return i["slug"]
    return None

def slugToItemID(slug: str) -> str:
    '''
    Docstring for itemIDToSlug
    
    :param itemID: Takes item ID
    :type itemID: string
    :return: Item Slug
    :rtype: string
    '''
    try:
        with open ("items.json", "r") as f:
            dict = json.load(f)
    except Exception as e:
        print("{cRed}Error: {cWhite}" + e)

    for i in dict["data"]:
        if i["slug"] == slug:
            return i["id"]
    return None

#endregion

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
    print("Making sets.json from items.json")
    with open("items.json", "r") as itemjson:
        itemDict = json.load(itemjson)

    for v in itemDict["data"]:
        amount +=1
        #print(itemDict["data"]["items"][i])
        urlName = v["slug"]
        
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
    Creates "best.json" with all information provided and json provided from grabbing slug on api
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
    createDict = {"data":[]}
    whiteList = ["setRoot","thumb","icon","slug","id","tags","tradingTax","i18n", "setParts"]
    itemJson = getItem(urlName)
    parsedItemsJson = parseWhiteList(itemJson, whiteList)

    
    for item in parsedItemsJson["data"]["setParts"]:
        if item == parsedItemsJson["data"]["id"]:
            createDict["data"].update(item)
            if ROI > 0:
                createDict["data"]["Platinum ROI"] = ROI
            if initialInvest > 0:
                createDict["data"]["Initial Invest"] = initialInvest
    
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
    setId = itemSetJson["data"]["id"]
    tempItemSet = {}
    itemPriceList = []
    #setsPrice = getLowestPlat(parseOWhiteList(checkOrderType(setOrderJson,"sell"),["platinum"]))

    


    #Json
    with open("sets.json", "r") as setsJson:
        setsDict = json.load(setsJson)
    #print(setId)

    for obj in setsDict:
        if obj["data"]["id"] == setId:
            tempItemSet.update(obj["data"])
            #print("added asset")
    
    for item in tempItemSet["setParts"]:
        if item != setId:
            itemPriceList.append(getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder(itemIDToSlug(item)),"sell"),["platinum"])))


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

def getROIWeapon(itemURL: str, checkBuyorder = False) -> tuple[int, int]:

    '''
    Get the ROI from the provided weapon itemURL
    checkBuyorder = False == Sell
    checkBuyorder = True == Buy
    '''

    #Vars
    itemSetJson = getItem(itemURL)
    setOrderJson = getItemOrder(itemURL)
    setId = itemSetJson["data"]["id"]
    tempItemSet = {}
    itemPriceList = [0]

    #Json
    with open("sets.json", "r") as setsJson:
        setsDict = json.load(setsJson)
    #print(setId)

    #get Set ID
    for obj in setsDict:
        if obj["data"]["id"] == setId:
            tempItemSet.update(obj["data"])
            #print("added asset")
    
    #Make Shopping list
    for obj in tempItemSet["setParts"]:
        urlName = str(obj["slug"])
        if obj["setRoot"] == False:
            if obj["quantityInSet"] > 1:
                totPrice = int(obj["quantityInSet"]) * getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder(obj["slug"]),"sell"),["platinum"]))
                print(f"{cBlue}More than one{urlName}{cWhite}")
                itemPriceList.append(totPrice)
            else:
                itemPriceList.append(getLowestPlat(parseOWhiteList(checkOrderType(getItemOrder(obj["slug"]),"sell"),["platinum"])))

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

def rOICheckAllWeapons() -> None:

    '''
    Checks all of the ROI on all weapons in sets.json
    '''

    start = timer()
    currentMP = ""
    currentROI = 0
    with open("sets.json", "r") as setsJson:
        sets = json.load(setsJson)

    for i in sets:
        if "weapon" in i["data"]["setParts"][0]["tags"]:
            for items in i["data"]["setParts"]:
                if items["setRoot"] == True:
                    x = getROIWeapon(items["slug"])[0]
                    urlName = str(items["slug"])
                    if currentMP == "":                        
                        currentROI = x
                        currentMP = items["slug"]
                    #    print("init roi")
                        print(f"Initial best is {urlName} with roi of {x}")
                    elif x > currentROI:
                        currentROI = x
                        currentMP = items["slug"]
                        print(f"{cGreen}New best is {urlName} with roi of {x}{cWhite}")
                    elif x < -1000:
                        print(f"{cRed}ERROR: {urlName} Out of Bounds, No one online selling?{cWhite} {x}")
                    else :
                        print(f"{cYellow}{urlName} is worse, Roi was {x}{cWhite}")
                        continue
    resultString = f"{currentMP} is most profitable with an ROI of {currentROI} platinum"
    initialInvest = getROIWeapon(currentMP)[1]
    updateBestPriceJson("weapon",currentMP,currentROI,None,initialInvest)    
    print("-" * len(resultString))
    print(resultString)
    print("-" * len(resultString)) 
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
        if "warframe" in i["data"]["tags"]:
            #print(i)
            if i["data"]["setRoot"] == True:
                x = getROIFrame(i["data"]["slug"])[0]
                urlName = str(i["data"]["slug"])
                if currentMP == "":                        
                    currentROI = x
                    currentMP = i["data"]["slug"]
                #    print("init roi")
                    print(f"initial best is {urlName} with roi of {x}")
                elif x > currentROI:
                    currentROI = x
                    currentMP = i["data"]["slug"]
                    print(f"{cGreen}New best is {urlName} with roi of {x}{cWhite}")
                else:
                    print(f"{cYellow}{urlName} is worse, Roi was {x}{cWhite}")

                db_insertROI(slugToItemID(urlName),x)
                framecount += 1

    end = timer()
    
    fastreturn = getROIFrame(str(currentMP), True)[0]
    initialInvest = getROIFrame(str(currentMP), False)[1]
    resultString = f"{currentMP} is most profitable with an ROI of {currentROI} platinum"
    #updateBestPriceJson("frame",currentMP,currentROI,None,initialInvest)
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

    SETSWHITELIST = ["slug","tags","id","ducats","mastery_level","setRoot","tradingTax", "quantityInSet","setParts"] # Whitelist for the getsets

    #Check if items.json and sets.json are present
    itemJsonPath = Path("items.json")
    setsJsonPath = Path("sets.json")
    if itemJsonPath.is_file() == False:
        updateItemListJson()
    
    if setsJsonPath.is_file() == False:
        updateSetsJson(SETSWHITELIST)

    #Warn if bestFrame.json and bestWeapon is not present
    bestFrameJsonPath = Path("bestFrame.json")
    if bestFrameJsonPath.is_file() == False:
        print(f"{cRed}ERROR: {bestFrameJsonPath} not found,{cWhite}Recomended to run rOICheckAllFrames()")
        check = input(f"{cGreen}Do you want to fetch current best Frame?(eta: ~1-2min): [Y/n]{cWhite}")
        match check.lower():

            case "n":
                return
            case "y":
                rOICheckAllFrames()
            case "":
                rOICheckAllFrames()
            case _:
                print("Unknown input. Skipping")
                return

    bestWeaponJsonPath = Path("bestWeapon.json")
    if bestWeaponJsonPath.is_file() == False:
        print(f"{cRed}ERROR: {bestWeaponJsonPath} not found, {cWhite}Recomended to run rOICheckAllWeapons()")
        check = input(f"{cGreen}Do you want to fetch current best Frame?(eta: ~1-2min): [Y/n]{cWhite}")
        match check.lower():

            case "n":
                return
            case "y":
                rOICheckAllWeapons()
            case "":
                rOICheckAllWeapons()
            case _:
                print("Unknown input. Skipping")
                return
    #
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

def test():
    '''

    '''
    dbInit()
    if conn is not None and cursor is not None:
        with open ("items.json", "r") as f:
            dictionary = json.load(f)
        #dbInsertItems(dictionary)
        cursor.execute("select set_parts from items where 'set'=any(item_tags) and 'warframe'=any(item_tags)")
        res = cursor.fetchall()
        for i in res:
            print(db_filterreturn(i))
        inp = input("commit? N/y\n").lower()
        match inp:
            case "y":
                conn.commit()

        conn.close()

def download_test_orders():
    with open("ordertest.json", "r") as f:
        setOrderJson = json.load(f)
    
    print(getHighestPlat(parseOWhiteList(checkOrderType(setOrderJson,"buy"),["platinum"])))
    
if __name__ == '__main__':
    dbInit()
    rOICheckAllFrames()
    conn.commit()
    conn.close()