#! python3

import time, datetime, sys, json # Standard library modules
import tkinter as tk
from tkinter.ttk import Progressbar

import requests # Import other modules
from tabulate import tabulate # Prints data quite nicely

import config # The config file


helpText = """
Help for organizer.

When you first open this, make sure to click
"Update AH Data" or else you won't be able to add
items with Ah checking.

To use, just enter in a username in the username field.
Click "Load Data"
If the user exists, it will load the stored data,
but if not, it will create a new user.

Click "Add Item" to add a new item

This program tries to come up with a reasonable
estimate for item prices based off of the Skyblock
auction house. These prices may be innacurate for
less common items. 

Clicking "Update AH Data" will update the 
stored AH data.

The "Update AH Prices" and "Update BIN Prices"
update the prices for all the items already added.

Before closing, make sure to click "Save"

"""




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









class LoadWindow(tk.Toplevel):
    def __init__(self,master):
        super().__init__(master = master) 
        self.title("Downloading AH data") 
        self.create_widgets()
        self.grid()
    
    def create_widgets(self):
        self.progress_StringVar = tk.StringVar()
        self.progress_StringVar.set("Downloading Data Pages: 0/0")
        self.progress_label = tk.Label(self,textvariable=self.progress_StringVar)
        self.progress_label.grid(row=0,column=0)
        self.progress_bar = Progressbar(self, orient = tk.HORIZONTAL, 
            length = 100, mode = 'determinate') 
        self.progress_bar.grid(row=1,column=0)

        self.progress_bar['value'] = 0
        self.load()
    
    def load(self):
        data = [] # The list of individual auction items
        currentPage = 0 # The page to get
        while True:
            # get all pages of ah data
            self.update()
                        # this forces a refresh of the screen
                        # it DOES slow down the program, but I think its better to 
                        # have a progress bar instead of the program just seeming to hang
                      

            pageData = requests.get(f"https://api.hypixel.net/skyblock/auctions?key={config.APIKey}&page={currentPage}").text 
            # API Key might not be needed for this!

            # Sure, I could use requests.get().json() but im not.

            dec = json.JSONDecoder() #Create a json decoder
            pageData = dec.decode(pageData) # make data a workable python object list

            maxPage = pageData["totalPages"]

            self.progress_StringVar.set(f"Downloading Data Pages: {currentPage}/{maxPage}")

            self.progress_bar['value'] = self.progress_bar['value'] + 100/maxPage

            data.extend(pageData["auctions"]) # we don't care about the other stuff

            if currentPage == maxPage:
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

           


        self.destroy_button = tk.Button(self,text="OK",command=self.destroy)
        self.destroy_button.grid(row=3)











class MainWindow(tk.Frame):

    def __init__(self,master=None):
        super().__init__(master) # Yes, I know someone is like "use super()!" NO.
        self.master = master
        self.master.title("Skyblock Purchase Organizer")
        self.initWindow() # Create Widgets
        self.grid()
        self.master.itemList = []

    def initWindow(self): # Create the wiggets

        self.usernameStrVar = tk.StringVar() # The text of the username input field
        self.usernameStrVar.set("")
        self.messageStrVar = tk.StringVar()
        self.messageStrVar.set("")


        self.usernameInLabel = tk.Label(self, text="Username: ") # The thing that says "Username: "
        self.usernameInLabel.grid(row=0,column=0)

        self.usernameEntry = tk.Entry(self,width=15,textvariable=self.usernameStrVar) # Where the user inputs the username to load
        self.usernameEntry.grid(row=0,column=1)

        self.dataLoadButton = tk.Button(self, text="Load Data", command=self.loadUserData) 
        self.dataLoadButton.grid(row=0,column=2)
        self.dataLoadButton = tk.Button(self, text="Save", command=self.saveUserData) 
        self.dataLoadButton.grid(row=0,column=3)

        self.addItemButton = tk.Button(self,text="Add Item",command = self.addItem)
        self.addItemButton.grid(row=0,column=4)

        self.delItemButton = tk.Button(self,text="Delete Item",command = self.delItem)
        self.delItemButton.grid(row=0,column=5)

        self.messageLabel = tk.Label(self, textvariable=self.messageStrVar) # Where the output messages go
        self.messageLabel.grid(row=0,column=6,columnspan=2)

        self.helpButton = tk.Button(self, text="Help",command = self.openHelp)
        self.helpButton.grid(row=1,column=0)

        self.updateAHButton = tk.Button(self,text="Update AH Data",command=self.updateAH)
        self.updateAHButton.grid(row=1,column=1)

        self.updateAHPricesButton = tk.Button(self,text="   Update AH Prices   ",command=self.updateAHPrices)
        self.updateAHPricesButton.grid(row=1,column=2,columnspan=2)

        self.updateBINPricesButton = tk.Button(self,text="    Update BIN Prices   ",command=self.updateBINPrices)
        self.updateBINPricesButton.grid(row=1,column=4,columnspan=2,padx=10)


        # Now for the hard part: displaying all of the user's data

        # First, we have to figure out what to sort by, so lets make a dropdown for that
        self.sortByLabel = tk.Label(self,text="Sort By: ")
        self.sortByLabel.grid(row=1,column=6)
        self.sortByStrVar = tk.StringVar()
        self.sortByStrVar.set("Alphabetical")
        self.sortByMenu = tk.OptionMenu(self, self.sortByStrVar, "Alphabetical","BIN Price","AH Price","User Price","Priority",command=self.updateList)
        self.sortByMenu.grid(row=1,column=7)
    

        self.outputArea = tk.Text(self,width=50,height=15,wrap="none")
        self.verticalBar = tk.Scrollbar(self,orient="vertical",command=self.outputArea.yview)
        self.horizontalBar = tk.Scrollbar(self,orient="horizontal",command=self.outputArea.xview)

        self.outputArea.configure(yscrollcommand=self.verticalBar.set, xscrollcommand=self.horizontalBar.set)

        self.outputArea.grid(row=3,pady=10,padx=10,columnspan=8, sticky="nsew")
        self.verticalBar.grid(row=3, column=8, sticky="ns")
        self.horizontalBar.grid(row=4, column=0, columnspan=8, sticky="ew")

        self.master.updateList = self.updateList # So that other windows can use it through the shared master


    def updateList(self,*args):
        conversionDict = {"Alphabetical":"Name","BIN Price":"BINCost","AH Price":"AHCost","User Price":"UserCost","Priority":"Priority"}
        sortBy = conversionDict[self.sortByStrVar.get()] # Just for readability of options


        with open("auctionHouse/AHLastUpdate.txt","r") as f:
            data = f"Last AH Data Update: {f.read()}\n"

        #try:
        newList = sorted(self.master.itemList, key=lambda k: k[sortBy]) 
        data += tabulate(newList,headers="keys")
        self.outputArea.configure(state ='normal')
        self.outputArea.delete("1.0",tk.END)
        self.outputArea.insert(tk.INSERT, data)
        self.outputArea.configure(state ='disabled')
           



       # except: self.messageStrVar.set("Invalid sort term")


    def openHelp(self):
        HelpWindow(self.master)
     
    def addItem(self):
        AddItemWindow(self.master)
   

    def delItem(self):
        DeleteItemWindow(self.master)
     

    def updateAHPrices(self):
        if config.ahSearch:
            output = ""
            for item in self.master.itemList:
                output += "\n\n"
                if str(item["AHUpdateTime"]) != "-1": # Make sure the user wants it to be checked
                                                     # Better safe than sorry with the Str stuff
                    newCost = ahSearch(item["Name"])
                    output += f"Got new cost for {item['Name']} of {newCost}\n"
                    output += f"Old cost was {item['AHCost']}\n"
                    if item["AHCost"] - newCost > 0: # Positive = price went down
                        verb = "decreased"
                        difference = item['AHCost'] - newCost
                    else:
                        verb = "increased"
                        difference = newCost - item['AHCost']
                    output += f"Difference: {verb} {difference} coins\n"
                        
                    item["AHCost"] = newCost
                    item["AHUpdateTime"] = time.asctime()

                else: output += f"Did not update AH for {item['Name']}\n"
            PriceResultWindow(output, self.master)
        else: self.messageStrVar.set("AH Searching is disabled!")
        self.updateList()



    def updateBINPrices(self):
        if config.ahSearch:
            output = ""
            for item in self.master.itemList:
                output += "\n\n"
                if str(item["BINUpdateTime"]) != "-1": # Make sure the user wants it to be checked
                                                        # Better safe than sorry with the Str stuff
                    newCost = binSearch(item["Name"])
                    output += f"Got new BIN cost for {item['Name']} of {newCost}\n"
                    output += f"Old cost was {item['BINCost']}\n"
                    if item["BINCost"] - newCost > 0: # Positive = price went down
                        verb = "decreased"
                        difference = item['BINCost'] - newCost
                    else:
                        verb = "increased"
                        difference = newCost - item['BINCost']
                    output += f"Difference: {verb} {difference} coins\n"
                        
                    item["BINCost"] = newCost
                    item["BINUpdateTime"] = time.asctime()
                    
                else: output += f"Did not update BIN for {item['Name']}\n"
            PriceResultWindow(output, self.master)
        else: self.messageStrVar.set("AH Searching is disabled!")
        self.updateList()


    def updateAH(self):
        """Update the AH data stored in AHData.json"""
        self.messageStrVar.set("Updating Auction House (this may take a while)")
        LoadWindow(self.master)

        self.messageStrVar.set("Stored auction house data sucessfully")
        self.updateList()

    def saveUserData(self):
        with open(f"userSaves/items{self.usernameStrVar.get()}.json","w") as f:
                json.dump(self.master.itemList, f)
        self.messageStrVar.set("Saved data successfuly!")

    def loadUserData(self):
        """Load the data for the username specified in
            the username entry"""
        if self.usernameStrVar.get() == "":
            self.messageStrVar.set("No username specified. Please enter a username.")
        else:
            try:
                with open(f"userSaves/items{self.usernameStrVar.get()}.json","r") as f:
                    itemList = json.load(f)
                    self.messageStrVar.set(f"Loaded itemlist for ID: {self.usernameStrVar.get()}")
            

            except FileNotFoundError:
                self.messageStrVar.set("User not found. Created new.")
                # Create a new user ID
                itemList = [] 

                with open(f"userSaves/items{self.usernameStrVar.get()}.json","w") as f: # Create a new items file for this user.
                    json.dump([],f) # Just in case the user doesn't save, they don't need to create a new ID again 

            
            try: 
                itemList # This will raise an error if no actual list was loaded
                self.master.itemList = itemList

            except: self.messageStrVar.set("No valid item list was loaded.")
        self.updateList()



class HelpWindow(tk.Toplevel): 
    def __init__(self, master = None): 
          
        super().__init__(master = master) 
        self.title("Purchase Organizer Help") 
        self.geometry("360x500") 
        self.grid()
        
        self.initWindow()
    
    def initWindow(self):
        """Creates the widgets"""
        self.quitButton = tk.Button(self,text="Exit",width=50,command=self.destroy)
        self.quitButton.grid(row=0,column=0)
        self.helpLabel = tk.Label(self,text=helpText)
        self.helpLabel.grid(row=1,column=0)




class PriceResultWindow(tk.Toplevel):
    def __init__(self, results, master = None): 
          
        super().__init__(master = master) 
        self.title("Price Update Results") 
        self.geometry("460x400") 
        self.grid()
        self.results = results
        self.initWindow()
    
    def initWindow(self):
        """Creates the widgets"""
        self.quitButton = tk.Button(self,text="Exit",width=50,command=self.destroy)
        self.quitButton.grid(row=0,column=0)
        self.outputArea = st.ScrolledText(self,  
                                      wrap = tk.WORD,  
                                      width = 50,  
                                      height = 20) 
        self.outputArea.grid(row=1,pady=10,padx=10)
        self.outputArea.insert(tk.INSERT, self.results)
        self.outputArea.configure(state ='disabled') # Read-only


class DeleteItemWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master = master) 
        self.title("Delete Item") 
        self.geometry("200x100") 
        self.grid()
        self.initWindow()
    
    def initWindow(self):
        """Creates the widgets"""
        self.deleteLabel = tk.Label(self,text="Item: ")
        self.deleteLabel.grid(row=0,column=0)

        self.nameStrVar = tk.StringVar()
        self.nameStrVar.set("")

        self.statusStrVar = tk.StringVar()
        self.statusStrVar.set("")

        self.nameEntry = tk.Entry(self,textvariable=self.nameStrVar)
        self.nameEntry.grid(row=0,column=1)

        self.submitButton = tk.Button(self,text="Submit",command=self.submitClicked)
        self.submitButton.grid(row=1,column=0)

        self.cancelButton = tk.Button(self,text="Cancel",command=self.destroy)
        self.cancelButton.grid(row=1,column=1)

        self.statusLabel = tk.Label(self,textvariable=self.statusStrVar)
        self.statusLabel.grid(row=2,columnspan=2)

    def submitClicked(self):
        itemName = self.nameStrVar.get().lower()
        for item in self.master.itemList:
            if itemName in item["Name"].lower():
                self.master.itemList.pop(self.master.itemList.index(item))
                self.master.updateList()
                self.destroy()

        # If it makes it here the item wasn't found. Alert the user
        print(itemName)
        self.statusStrVar.set("Not Found")


class AddItemWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master = master) 
        self.title("Add Item") 
        self.geometry("200x175") 
        self.grid()
        self.initWindow()

    def initWindow(self):
        """Creates the widgets"""
        # We need Name, Priority, Cost, Search Ah? Search BIN?
        self.nameStrVar = tk.StringVar()
        self.nameStrVar.set("")

        self.priorityStrVar = tk.StringVar()
        self.priorityStrVar.set("")

        self.costStrVar = tk.StringVar()
        self.costStrVar.set("")

        self.nameLabel = tk.Label(self,text="Name: ")
        self.nameLabel.grid(row=0,column=0)

        self.nameEntry = tk.Entry(self,textvariable=self.nameStrVar)
        self.nameEntry.grid(row=0,column=1)

        self.costLabel = tk.Label(self,text="Cost: ")
        self.costLabel.grid(row=1,column=0)

        self.costEntry = tk.Entry(self,textvariable=self.costStrVar)
        self.costEntry.grid(row=1,column=1)

        self.priorityLabel = tk.Label(self,text="Priority: ")
        self.priorityLabel.grid(row=2,column=0)
        self.priorityStrVar = tk.StringVar()
        self.priorityStrVar.set("0")
        self.priorityMenu = tk.OptionMenu(self, self.priorityStrVar, "0","1","2","3","4","5","6","7","8","9","10")
        self.priorityMenu.grid(row=2,column=1)


        self.searchAHLabel = tk.Label(self,text="Search AH: ")
        self.searchAHLabel.grid(row=3,column=0)
        self.searchAHStrVar = tk.StringVar()
        self.searchAHStrVar.set("Yes")
        self.searchAHMenu = tk.OptionMenu(self, self.searchAHStrVar, "Yes","No")
        self.searchAHMenu.grid(row=3,column=1)

        self.searchBINLabel = tk.Label(self,text="Search BIN: ")
        self.searchBINLabel.grid(row=4,column=0)
        self.searchBINStrVar = tk.StringVar()
        self.searchBINStrVar.set("Yes")
        self.searchBINMenu = tk.OptionMenu(self, self.searchBINStrVar, "Yes","No")
        self.searchBINMenu.grid(row=4,column=1)

        self.submitButton = tk.Button(self,text="Submit",command=self.submitClicked)
        self.submitButton.grid(row=5,column=0)

        self.cancelButton = tk.Button(self,text="Cancel",command=self.destroy)
        self.cancelButton.grid(row=5,column=1)
    
    def submitClicked(self):

        if self.searchBINStrVar.get() == "Yes":
            BINPrice = binSearch(self.nameStrVar.get())
            BINUpdateTime = time.asctime()
        else: BINPrice, BINUpdateTime = -1,-1
        if self.searchAHStrVar.get() == "Yes":
            AHPrice = binSearch(self.nameStrVar.get())
            AHUpdateTime = time.asctime()
        else: AHPrice, AHUpdateTime = -1,-1

        if AHPrice == 0: # Impossible, bad data
            AHPrice, AHUpdateTime = -1,-1
        
        if BINPrice == 0: # Impossible, bad data
            BINPrice, BINUpdateTime = -1,-1

        self.master.itemList.append({
                "Name":self.nameStrVar.get(),
                "Priority":int(self.priorityStrVar.get()),
                "UserCost":int(self.costStrVar.get()),
                "AHCost":AHPrice,
                "AHUpdateTime":AHUpdateTime,
                "BINCost":BINPrice,
                "BINUpdateTime":BINUpdateTime
                })
        self.master.updateList()
        self.destroy() # close the window
        


if __name__ == "__main__": # as if it would never not be
    
    root = tk.Tk()
    root.geometry('')
    app = MainWindow(root)
    app.mainloop()


