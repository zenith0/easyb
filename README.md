# Goal
Easy-bank allows to scrape data from obk (c src for more details) ebanking extracting transaction data.
Data is stored in a seperate database. 
While scraping a web dashboard is opened showing statistics.

# Backlog
## 1st iteration - account viewer
1. Reasearch How to access banking in general, specifically banking-oberbank.at :white_check_mark:

2. establish secure read connecting to ebanking portal :white_check_mark:\
2.a. NF: As little logins as possible :white_check_mark:\
2.b. Check feasibility of oAuth/Web :white_check_mark:
3. store data (somewhere), db comes later 

## 2nd iteration - UI for banking records
1. Based on outcome of #1 build a mockup in react
2. Table view showing relevant info (amount, recipient/sender, )
3. Fetch stored banking records for given timeframe \
3.a. Last month (01-31 of last month) should be supported \
3.b. Last n month should be supported \
3.c View: Group by month \
3.d current month (01-now) \

## 3nd iteration - balance observability
This iteration will focus on the monitoring of financial plans vs actuals. Specificially it should allow the user to define a household plan. The household plan can be compared with the actuals from the account viewer.
In a second step dashboarding and alerting should come into play
