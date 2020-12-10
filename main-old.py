#! python3

import time, datetime, sys, json # Standard library modules

import requests # Import other modules

from tabulate import tabulate # Prints data quite nicely

import config # The config file

from colorama import Style, Fore, Back, init
        # Allows us to use colored text
        # How to use:
        #    print(f"{Fore.RED}RED TEXT{Style.RESET_ALL}")
        #    would print RED TEXT in the color red. f-strings make this
        #    so much easier!

        # Options:
        # Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
        # Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
        # Style: DIM, NORMAL, BRIGHT, RESET_ALL

init(autoreset=True) # Should make this work for more windows use cases
                     # also will remove the need to reset color after each line.


if not config.useColor: # for some reason, the user doesn't want colored text.
                        # likely because the colors are not suppored on that system
                        # and it just looks like random ugly text

    class placeHolder(): # There has GOT to be a better way to do this
        """
        A placeholder class to replace colorama codes with.
        The entire idea of having to make this just rubs me the wrong
        way. 
        """
        def __init__(self):
            self.BLACK, self.RED, self.GREEN, self.YELLOW = '','','',''
            self.BLUE, self.MAGENTA, self.CYAN, self.WHITE, self.RESET = '','','','',''
            self.DIM, self.NORMAL, self.BRIGHT, self.RESET_ALL = '','','',''
    Style, Fore, Back = placeHolder(), placeHolder(), placeHolder()


############################## ALERT ###############################
# if you hate camelCase, look no further, lest your brain explode. #
# camelCaseIsTrulyGreat                                            #
# snake_case_really_sucks                                          #
############################## ALERT ###############################


# Hypixel API documentation: https://github.com/HypixelDev/PublicAPI


#  datetime.datetime.fromtimestamp(milliseconds // 1000.0) should turn time into something legible


# To get bazaar data:
# https://api.hypixel.net/skyblock/bazaar/product?key=APIKEY&productId=ITEMID
# (PYTHON) requests.get(f"https://api.hypixel.net/skyblock/bazaar/product?key={config.APIKey}&productId={itemID}")
# According to the wiki, it is deprecated and will soon be removed
# but it says nothing of the sort on the github page
# Info:
# https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/bazaar.md


# To get auctions data:
# https://api.hypixel.net/skyblock/auctions?key=APIKEY&page=Page
# (PYTHON) requests.get(f"https://api.hypixel.net/skyblock/auctions?key={config.APIKey}")
# Info: 
# https://github.com/HypixelDev/PublicAPI/blob/master/Documentation/methods/skyblock/auctions.md


# An itemlist should look like 
# [
# {
# "Name": str name,
# "Priority": int priority, 
# "Rarity": int rarity (common=0,uncommon=1,rare=2,epic=3,legendary=4,mythic=5,supreme=6,special=7,very special=8),
# ^^^ Used for coloration when printing out ^^^
# "UserPrice": int user override price, default -1,
# "AHCost": int AH cost as of when it was created, default -1,
# "AHUpdateTime": int update timestamp, default -1,
# "BINCost": int AH BIN cost as of when it was created, default -1
# "BINUpdateTime": int update timestamp, default -1,
# },{
# "Name": str name,
# "Priority": int priority, 
# "Rarity": int rarity (common=0,uncommon=1,rare=2,epic=3,legendary=4,mythic=5,supreme=6,special=7,very special=8),
# ^^^ Used for coloration when printing out ^^^
# "UserPrice": int user override price, default -1,
# "AHCost": int AH cost as of when it was created, default -1,
# "AHUpdateTime": int update timestamp, default -1,
# "BINCost": int AH BIN cost as of when it was created, default -1
# "BINUpdateTime": int update timestamp, default -1,
# }
# ]


def updateAH():
    """Update the AH data stored in AHData.json"""
    print(f"{Fore.GREEN} Updating AH...")
    data = [] # The list of individual auction items
    currentPage = 0 # The page to get
    while True:
        # get all pages of ah data

        pageData = requests.get(f"https://api.hypixel.net/skyblock/auctions?key={config.APIKey}&page={currentPage}").text 
        # API Key might not be needed for this!

        # Sure, I could use requests.get().json() but im not.

        dec = json.JSONDecoder() #Create a json decoder
        pageData = dec.decode(pageData) # make data a workable python object list

        maxPage = pageData["totalPages"]

        print(f"{Fore.GREEN}Got data for page {currentPage} of {maxPage}")

        data.extend(pageData["auctions"]) # we don't care about the other stuff

        if currentPage == maxPage:
            print(f"{Fore.GREEN}Finished getting data.")
            break


        # time.sleep(0.6) # We don't wan't to go over the throttle limit, so just in case
                        # Let's also make it a bit larger than it needs to be, again, just in case
                        # though really, this is so slow, I doubt it matters.
        # Commented out because you don't actually need to supply a valid
        # api key, therefore you don't need to be worried about getting it banned.

        currentPage += 1 # get a new page next time

    with open("auctionHouse/AHData.json","w") as f: # Overwrite old data
        json.dump(data, f) # Dump all of the data, as json again, into a file
    with open("auctionHouse/AHLastUpdate.txt","w") as f:
        f.write(time.asctime())
    print("Stored auction house data sucessfully")


def ahSearch(item):
    """
    Searches the stored Auction House data for an item,
    and returns the average of the 10 auctions
    closest to ending. Returns an integer of
    price, and a timestamp
    """
    # Open AHData file and make the data a list
    with open("auctionHouse/AHData.json","r") as f:
        data = json.load(f)

    # We now have a list of all the data. Now, search all entries for item
    matchedAuctions = []
    for auction in data:
        if item.lower() in auction["item_name"].lower():
            try:
                auction["bin"] # make sure its not BIN
                # This will raise an error if it's not BIN

            except KeyError: matchedAuctions.append(auction)

    # We now have a list of all the auctions who's name matches the desired item
    # Now, find the <num> auctions closest to ending

    matchedAuctions.sort(key=lambda x: x["end"]) # First time using lambda! 
    matchedAuctions = matchedAuctions[:config.ahNum] # Get the first <num>

    # Get average of highest bids, and return it

    price = 0
    for auction in matchedAuctions:
        price += auction["highest_bid_amount"]

    return price // config.ahNum # Return the average



def binSearch(item):
    """
    Searches the stored BIN catagoty of the Auction 
    House data for an item, and returns the average
    of the 10 lowest prices. Returns an integer of
    price, and a timestamp
    """
    # Open AHData file and make the data a list
    with open("auctionHouse/AHData.json","r") as f:
        data = json.load(f)

    # We now have a list of all the data. Now, search all entries for item
    matchedAuctions = []
    for auction in data:
        if item.lower() in auction["item_name"].lower():
            try:
                auction["bin"] # make sure its not BIN
                # This will raise an error if it's not BIN
                matchedAuctions.append(auction)

            except KeyError: pass

    # We now have a list of all the BIN auctions who's name matches the desired item
    # Now, find the <num> auctions with the lowest price

    matchedAuctions.sort(key=lambda x: x["starting_bid"]) # First time using lambda! 
    matchedAuctions = matchedAuctions[:config.binNum] # Get the first <num>

    # Get average of price, and return it

    price = 0
    for auction in matchedAuctions:
        price += auction["starting_bid"]

    return price // config.binNum # Return the average



def main():
    # So, first we need to load the user's saved purchase list from the shelve file.

    try:
        userID = input("User ID: ") # Used later while saving
        with open(f"userSaves/items{userID}.json","r") as f:
            itemList = json.load(f)
            print(f"{Fore.GREEN} Loaded itemlist for ID: {userID}")


    except FileNotFoundError:
        if "y" in input(f"{Fore.YELLOW}User ID not found. Create new one? (y/n) ").lower():
            # Create a new user ID
            itemList = [] 

            with open(f"userSaves/items{userID}.json","w") as f: # Create a new items file for this user.
                json.dump([],f) # Just in case the user doesn't save, they don't need to create a new ID again

            print(f"{Fore.GREEN} Created new user ID {userID}")


    try: itemList # This will raise an error if no actual list was loaded
    except: sys.exit(f"{Fore.RED}No valid item list loaded") # Quit the program

    # By now we should have a valid itemlist
    print(f"{Fore.GREEN}Press ? for a list of commands")
    while True:
        cmd = input("> ")
        if cmd == "?":
            print("""
Commands:
Add                           : Add an item to the purchase list
Save                          : Save the purchase list
UpdateAH                      : Update the AH data (Do this before Update)
Update                        : Update AH and BIN prices for all items
Remove                        : Remove an item from the purchase list
List (param)                  : List the items by (param)
    params: UserCost, AHCost, BINCost, Priority (case sensitive)
Quit                          : Quit this program
            """)
        if "list" in cmd.lower():
            with open("auctionHouse/AHLastUpdate.txt","r") as f:
                print(f"{Fore.CYAN}Last AH Data Update: {f.read()}")
            cmd = cmd.replace("list","").strip() # Not in a regexy mood today
                                                 # It needs to match both "list" and "list " 
            if not cmd:
                print(tabulate(itemList,headers="keys")) # Order doesn't matter

            else:
                try:
                    newList = sorted(itemList, key=lambda k: k[cmd]) 
                    print(tabulate(newList,headers="keys"))
                except: print(f"{Fore.YELLOW}Invalid argument for command.")
            continue

        cmd = cmd.strip().lower()

        if cmd == "quit": sys.exit(f"{Fore.GREEN}Program Exited.")

        elif cmd == "updateah":
            if config.ahSearch:
                if "y" in input(f"Really update AH data? (y/n) {Fore.YELLOW} (This may take a while) ").lower():
                    updateAH()
            else: print(f"{Fore.YELLOW}AH searching is disabled!")

        elif cmd == "update":
            if config.ahSearch:
                for item in itemList:
                    print("\n\n")
                    if str(item["AHUpdateTime"]) != "-1": # Make sure the user wants it to be checked
                                                        # Better safe than sorry with the Str stuff
                        newCost = ahSearch(item["Name"])
                        print(f"Got new cost for {item['Name']} of {newCost}")
                        print(f"Old cost was {item['AHCost']}")
                        if item["AHCost"] - newCost > 0: # Positive = price went down
                            verb = "decreased"
                            color = Fore.GREEN
                            difference = item['AHCost'] - newCost
                        else:
                            verb = "increased"
                            color = Fore.RED
                            difference = newCost - item['AHCost']
                        print(f"Difference: {color}{verb} {difference} coins")

                        item["AHCost"] = newCost
                        item["AHUpdateTime"] = time.asctime()

                    else: print(f"{Fore.YELLOW}Did not update AH for {item['Name']}")


                    if str(item["BINUpdateTime"]) != "-1": # Make sure the user wants it to be checked
                                                        # Better safe than sorry with the Str stuff
                        newCost = binSearch(item["Name"])
                        print(f"Got new BIN cost for {item['Name']} of {newCost}")
                        print(f"Old cost was {item['BINCost']}")
                        if item["BINCost"] - newCost > 0: # Positive = price went down
                            verb = "decreased"
                            color = Fore.GREEN
                            difference = item['BINCost'] - newCost
                        else:
                            verb = "increased"
                            color = Fore.RED
                            difference = newCost - item['BINCost']
                        print(f"Difference: {color}{verb} {difference} coins")

                        item["BINCost"] = newCost
                        item["BINUpdateTime"] = time.asctime()

                    else: print(f"{Fore.YELLOW}Did not update BIN for {item['Name']}")

            else: print(f"{Fore.YELLOW}AH searching is disabled!")


        elif cmd == "save":
            with open(f"userSaves/items{userID}.json","w") as f:
                json.dump(itemList, f)

        elif cmd == "remove":
            done = False
            itemName = input("Item to remove: ").lower()
            for item in itemList:
                if itemName in item["Name"].lower():
                    itemList.pop(itemList.index(item))
                    print(f"{Fore.GREEN}Removed item {itemName} from purchase list")
                    done = True

            if not done: print(f"{Fore.YELLOW}No item with that name found.") # It won't make it here if all went well


        elif cmd == "add":
            name = input("Item name: ")
            while True:
                priority = input("Priority: (0-10) ")
                try:
                    if int(priority) > 10 or int(priority) < 0:
                        print(f"{Fore.YELLOW}Number not in valid range")
                    else: 
                        priority = int(priority)
                        break # There is an integer in the range, leave the loop
                except: print(f"{Fore.YELLOW}Invalid Integer")

            AHPrice, BINPrice = -1,-1 # Set defaults
            AHUpdateTime, BINUpdateTime = -1, -1

            while True:
                userCost = input("Estimated Item Cost: ")
                try:
                    userCost = int(userCost)
                    break # There is an integer, leave loop
                except: print(f"{Fore.YELLOW}Invalid Integer")

            if config.ahSearch: # Can be disabled
                if "y" in input("Update AH records? (may take a while) (y/n) "):
                    updateAH()
                if "y" in input("Search AH for average price? (y/n) ").lower():
                    AHPrice = ahSearch(name)
                    AHUpdateTime = time.asctime()
                    print(f"{Fore.GREEN} Got AH price average of {AHPrice} coins.")
                    if AHPrice == 0: # Useless data
                        print(f"{Fore.YELLOW}Discarding AH Price")
                        AHPrice = -1
                        AHUpdateTime = -1

                if "y" in input("Search BIN for average price? (y/n) ").lower():
                    BINPrice = binSearch(name)
                    BINUpdateTime = time.asctime()
                    print(f"{Fore.GREEN} Got BIN price average of {BINPrice} coins.")
                    if BINPrice == 0: # Useless data
                        print(f"{Fore.YELLOW}Discarding BIN Price")
                        BINPrice = -1
                        BINUpdateTime = -1

            itemList.append({
                "Name":name,
                "Priority":priority,
                "UserCost":userCost,
                "AHCost":AHPrice,
                "AHUpdateTime":AHUpdateTime,
                "BINCost":BINPrice,
                "BINUpdateTime":BINUpdateTime
                }) # Actually add the item to the itemlist           

if __name__ == "__main__": main() # Unless someone is importing this, run main() 
