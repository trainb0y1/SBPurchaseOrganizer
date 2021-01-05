#! python3

# Not really much in the way of a config file, just a place to put the API key
# and some other customizable stuff
# Just making it a py file for convinience.
# Type # before a line to comment it out

APIKey = "INSERT API KEY HERE"
# The skyblock api access key. Get one by running the 
# command /api in minecraft when logged onto hypixel
# THIS MAY NOT ACTUALLY BE NEEDED FOR THIS
# Try without, but if you get an API Error
# put one in.


useColor = True
# Either True or False, whether or not to attempt colorful text.
# If this program spits out a bunch of random characters, try disabling this.
# Not implemented for the gui verson yet, sorry!


ahSearch = True
# Either True or False, whether or not to attempt to search the Skyblock
# Auction House for prices


ahNum = 3
# The number of ending soon auctions to take the average item price from
# Setting this too high will result in non-ending soon auctions being averaged
# leading to an innacurate estimate

# Setting this negative will cause all sorts of problems, including
# possible getting the average of the ending latest items
# and having the end average be negative


binNum = 6
# The number of lowest price BIN auctions to take the average item price from
# Setting this too high will result in non-low price auctions being averaged
# leading to an innacurate estimate

# Setting this negative will cause all sorts of problems, including
# possible getting the average of the highest price items
# and having the end average be negative
