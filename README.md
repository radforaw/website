# Website

This file represents the source code for my demonstration website at http://www.bcctraffic.co.uk/

The site is my play space for creating prototype for potential traffic analysis service, largely making use of existing open data.The aim is to show how simple it can be to pick up on a new (open) data source and use it. There are also some novel examples of how open data can be analysed and visualised.

# Data sources

Currently the data is sourced from a limited number of existing data open sources:-
* bcc.opendata.onl - This is a site that provides real time data from Birmingham City Council's traffic managment systems
* realjourneytime.co.uk - This site analysese bus departure information to determine whether buses are on time or running late
* opendata.bristol.gov.uk - open traffic data from Bristol City Council (not currently in use)
* www.openstreetmap.org - base mapping + data from the OSM database
* info from Birmingham City Council's streetworks register (not currently an open data source)

# Applications

The main screen shows a number of bus route links in Birmingham City Centre, when you click on these, it shows graphs of the current bus journey time on the various routes.

The other links do the following:
* 20 mph - site that takes data from open treatment and turned it into hey symbol checker to find out if your road has a 20 mile hour speed limit or not. Currently this is not pretty well laid out but that is on the to do list.
* buses - currently, this only identifies the route that goes to Holloway Circus Island and provides a graph for that. The rest of it is the same as is shown on the main screen.
* wi-Fi map - this shows journey times on links that have been enabled for Wi-Fi. This involves analysing the mac address of vehicles passing each section of road and calculating how long it takes for them to get between two for example junctions. When you click on each link it shows a graph that compares the current journey time with a historic journey time calculation by aggregating data from the last four weeks.
* GLOSA map - this provides amount of information from the West Midlands GLOSA project. This provides information from traffic lights showing their current state(I.e. red amber and green) both historically and also by predicting ahead by about minute. This site goes to a number of different features of showing what the raw data looks like how the data is processed and also then links to the website that.
* arrows - this is not an open data service. This takes data from the stats 19 accident information service and processes it to show which direction the vehicles moving in when the accident occurred. It basically provides two arrows so you can see if it was a head-on collision side collision or a rear end shunt.
* Street works - this shows a simple graph of the Street Works register showing the number of works that are due to take place within Birmingham city centre over the next 56 days.

# worst junctions. The worst  junctions link on the right-hand side provides a list of the worst junctions for bus delays calculated based on the length of the delay and intensity. A handy five-star rating system is provided.
