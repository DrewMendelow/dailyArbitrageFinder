import requests
import pytz
from datetime import datetime

import smtplib
from email.mime.text import MIMEText

import os

apiKey1 = os.getenv("API_KEY_1")
apiKey2 = os.getenv("API_KEY_2")
apiKey3 = os.getenv("API_KEY_3")
apiKey4 = os.getenv("API_KEY_4")

appSpecificPass = os.getenv("APP_SPECIFIC_PASS")
emailAddress = os.getenv("EMAIL_ADDRESS")

ept = pytz.timezone('US/Eastern')
def americanToDecimal(val):
        val = str(val)
        num = int(val)
        if val[0] == '-':
            num = int(val[1:])
            return (100/num) + 1
        return (num/100) + 1

def decimalToAmerican(val):
    num = 0
    if val < 2:
        num = -100/(val - 1)
    else:
        num = (val - 1) * 100
    return num

def getROI(num1, num2, total):
    profit = total / (1/num1 + 1/num2) - total
    return (profit / total) * 100
    # actual profit not %:
    # return total / (1/num1 + 1/num2) - total

def getFreeROI(total, betterAmount, betterOdd):
    profit = (betterAmount * betterOdd) - total
    result = (profit / total) * 100
    return result

def getROI3(val1, val2, val3, total):
    profit = (total/((1/val1) + (1/val2) + (1/val3))) - total
    roi = (profit / total) * 100
    return roi
    # actual profit not %:
    # val = (total/((1/val1) + (1/val2) + (1/val3))) - total
    # return val

def getAmount(val, totalPerc, total):
    perc = 1/val
    amount = (total*perc)/totalPerc
    return round(amount,2)

def getFreeAmountsWithTotal(total, minusOdd, plusOdd):
    even = total/minusOdd
    profit = total - even
    result = [profit, even]
    return result

def isGood3(val1, val2, val3):
    if ((1/val1) + (1/val2) + (1/val3)) < 1:
        return True
    return False

def getOddSign(home, away):
    if home[0] == '-' and away[0] != '-':
        return 1
    elif home[0] != '-' and away[0] == '-':
        return 2
    elif home[0] != '-' and away[0] != '-':
        return 3
    else:
        return 0

def run(Sport, Books, Totals, Moneyline, Spreads, Live, Pregame, Arbitrage, SearchAll, Roi, FreeBet, TotalAmount):
    output = ''
    sportBooks = ['DraftKings', 'FanDuel', 'BetMGM', 'ESPN BET', 'Caesars']
    bookList = ['DraftKings', 'FanDuel', 'BetMGM', 'ESPN BET', 'Caesars', 'BetOnline.ag', 'BetRivers', 'BetUs', 'Bovada', 'LowVig.ag', 'MyBookie.ag', 'PointsBet (US)', 'SuperBook', 'Unibet', 'WynnBET', 'betPARX', 'Fliff', 'Hard Rock Bet', 'SI Sportsbook', 'Tipico']
    bookKeyList = ['draftkings', 'fanduel', 'betmgm', 'espnbet', 'caesars', 'betonlineag', 'betrivers', 'betus', 'bovada', 'lowvig', 'mybookieag', 'pointsbetus', 'superbook', 'unibet_us', 'wynnbet', 'betparx', 'fliff', 'hardrockbet', 'sisportsbook', 'tipico_us']
    sport = Sport
    # upcoming
    # icehockey_nhl
    # basketball_nba
    # basketball_ncaab
    # soccer_epl
    # baseball_ncaa
    # basketball_euroleague
    # soccer_uefa_champs_league

    # ADD sports if you want:
    # americanfootball_ncaaf
    # soccer_spain_la_liga
    # soccer_france_ligue_one
    # basketball_wncaab
    # soccer_netherlands_eredivisie
    # boxing_boxing
    # soccer_usa_mls
    # icehockey_ahl

    # allBooks = False
    # totals = False
    # moneyline = True
    # spreads = False
    # live = True
    # pregame = True
    # arbitrage = True
    # searchAll = False

    # allBooks = AllBooks
    totals = Totals
    moneyline = Moneyline
    spreads = Spreads
    live = Live
    pregame = Pregame
    arbitrage = Arbitrage
    freeBet = FreeBet
    searchAll = SearchAll
    totalAmount = TotalAmount
    # searchAll takes 165 with 3 markets - (53 for moneyline)
    roi = Roi
    
    markets = ''
    if totals:
        markets += ',totals'
    if moneyline:
        markets += ',h2h'
    if spreads:
        markets += ',spreads'
    if markets != '':
        if markets[0] == ',':
            markets = markets[1:]

    # books = ''
    # for book in Books:
    #     books += f',{book}'
    # if books[0] == ',':
    #     books = books[1:]
    resquestsRemaining = 500
    jsons: list[dict] = []
    apiKeyNum = 1
    continueApiKeyCycle = True
    while (continueApiKeyCycle):
        apiKey = apiKey1
        if apiKeyNum == 2:
            apiKey = apiKey2
        elif apiKeyNum == 3:
            apiKey = apiKey3
        elif apiKeyNum == 4:
            apiKey = apiKey4
                
        if (totals or moneyline or spreads) and Books != '':
            params = {'apiKey': apiKey, 'markets': markets, 'bookmakers': Books, 'oddsFormat': 'american', 'dateFormat': 'unix'}

            sportKeys = [sport]
            if searchAll:
                sportList = requests.get('https://api.the-odds-api.com/v4/sports/?apiKey=' + apiKey).json()
                sportKeys = []
                for sport in sportList:
                    if not(sport['has_outrights']):
                        sportKeys.append(sport['key'])

            # print('2 way Moneyline')
            # for sport in sportKeys:
                # url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/'
            # url = f'https://api.the-odds-api.com/v4/sports/upcoming/odds/'
            for sportKey in sportKeys:
                # url = f'https://api.the-odds-api.com/v4/sports/{sport}/odds/'
                url = f'https://api.the-odds-api.com/v4/sports/{sportKey}/odds/'
                response = requests.get(url, params)
                json = response.json()
                if response.status_code < 400:
                    jsons = jsons + [json]
                    for bet in json:
                        if (live and bet['commence_time'] < datetime.now().astimezone().timestamp()) or (pregame and bet['commence_time'] > datetime.now().astimezone().timestamp()):
                            betLive = 'Pre-game'
                            if bet['commence_time'] < datetime.now().astimezone().timestamp():
                                betLive = 'Live'
                            date: datetime = bet['commence_time']
                            date = datetime.fromtimestamp(date).strftime('%m/%d/%Y %-I:%M%p')
                            for book in bet['bookmakers']:
                                # if allBooks or sportBooks.count(book['title']) > 0: 
                                    for i in range(len(book['markets'])):
                                        if (len(book['markets'][i]['outcomes']) == 2):
                                            if book['markets'][i]['key'] == 'totals': 
                                                overOdds = book['markets'][i]['outcomes'][0]['price']
                                                underOdds = book['markets'][i]['outcomes'][1]['price']
                                                for otherBook in bet['bookmakers']:
                                                    # if allBooks or sportBooks.count(otherBook['title']) > 0:
                                                        for j in range(len(otherBook['markets'])):
                                                            if otherBook['markets'][j]['key'] == 'totals':
                                                                if otherBook['title'] != book['title']:
                                                                    if otherBook['markets'][j]['outcomes'][0]['point'] == book['markets'][i]['outcomes'][0]['point']:
                                                                        underOtherOdd = otherBook['markets'][j]['outcomes'][1]['price']
                                                                        oddsSign = getOddSign(str(overOdds), str(underOtherOdd))
                                                                        if oddsSign != 0:
                                                                            firstOdd = overOdds
                                                                            secondOdd = underOtherOdd
                                                                            if oddsSign == 1:
                                                                                firstOdd = int(str(overOdds)[1:])
                                                                                secondOdd = underOtherOdd
                                                                            elif oddsSign == 2:
                                                                                firstOdd = int(str(underOtherOdd)[1:])
                                                                                secondOdd = overOdds
                                                                            if ((not(arbitrage) and not(freeBet)) or ((arbitrage or freeBet) and (firstOdd < secondOdd or oddsSign == 3))):
                                                                                currentRoi = 0.0
                                                                                totalPercent = 0.0
                                                                                overAmount = 0.0
                                                                                underAmount = 0.0
                                                                                if not(freeBet):
                                                                                    currentRoi = getROI(americanToDecimal(str(underOtherOdd)), americanToDecimal(str(overOdds)), total=totalAmount)
                                                                                    totalPercent = 1/americanToDecimal(str(underOtherOdd)) + 1/americanToDecimal(str(overOdds))
                                                                                    overAmount = getAmount(americanToDecimal(str(overOdds)),totalPercent,totalAmount)
                                                                                    underAmount = getAmount(americanToDecimal(str(underOtherOdd)),totalPercent,totalAmount)
                                                                                else:
                                                                                    betterOdd = 0
                                                                                    if americanToDecimal(str(overOdds)) > americanToDecimal(str(underOtherOdd)):
                                                                                        results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(overOdds)),minusOdd=americanToDecimal(str(underOtherOdd)))
                                                                                        overAmount = round(results[0],2)
                                                                                        underAmount = round(results[1],2)
                                                                                        betterOdd = americanToDecimal(str(overOdds))
                                                                                    else:
                                                                                        results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(underOtherOdd)),minusOdd=americanToDecimal(str(overOdds)))
                                                                                        underAmount = round(results[0],2)
                                                                                        overAmount = round(results[1],2)
                                                                                        betterOdd = americanToDecimal(str(underOtherOdd))
                                                                                    currentRoi = getFreeROI(total=totalAmount,betterAmount=results[0], betterOdd=betterOdd)
                                                                                if  ((not(arbitrage) and not(freeBet)) or currentRoi > roi):
                                                                                    print(f'{bet['sport_title']} - {betLive}')
                                                                                    print(f'Total - {bet['home_team']} v {bet['away_team']}  {book['markets'][i]['outcomes'][0]['point']} - {date} ET')
                                                                                    print(f'{book['title']}: ->{book['markets'][i]['outcomes'][0]['name']}({overOdds})<- v {book['markets'][i]['outcomes'][1]['name']}({underOdds})   ${overAmount}')
                                                                                    print(f'{otherBook['title']}: {otherBook['markets'][j]['outcomes'][0]['name']}({otherBook['markets'][j]['outcomes'][0]['price']}) v ->{otherBook['markets'][j]['outcomes'][1]['name']}({underOtherOdd})<-   ${underAmount}')
                                                                                    print(f'ROI: {round(currentRoi, 2)}%')
                                                                                    print(f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}')
                                                                                    print(' ')
                                                                                    output += f'{bet['sport_title']} - {betLive}\n'
                                                                                    output += f'Total - {bet['home_team']} v {bet['away_team']}  {book['markets'][i]['outcomes'][0]['point']} - {date} ET\n'
                                                                                    output += f'{book['title']}: ->{book['markets'][i]['outcomes'][0]['name']}({overOdds})<- v {book['markets'][i]['outcomes'][1]['name']}({underOdds})   ${overAmount}\n'
                                                                                    output += f'{otherBook['title']}: {otherBook['markets'][j]['outcomes'][0]['name']}({otherBook['markets'][j]['outcomes'][0]['price']}) v ->{otherBook['markets'][j]['outcomes'][1]['name']}({underOtherOdd})<-   ${underAmount}\n'
                                                                                    output += f'ROI: {round(currentRoi, 2)}%\n'
                                                                                    output += f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}''\n\n'
                                            else:
                                                homeOdds = 0
                                                awayOdds = 0
                                                homeSpread = 0
                                                awaySpread = 0
                                                if (book['markets'][i]['outcomes'][0]['name'] == bet['home_team']):
                                                    homeOdds = book['markets'][i]['outcomes'][0]['price']
                                                    awayOdds = book['markets'][i]['outcomes'][1]['price']
                                                    if book['markets'][i]['key'] == 'spreads':
                                                        homeSpread = book['markets'][i]['outcomes'][0]['point']
                                                        awaySpread = book['markets'][i]['outcomes'][1]['point']
                                                else:
                                                    homeOdds = book['markets'][i]['outcomes'][1]['price']
                                                    awayOdds = book['markets'][i]['outcomes'][0]['price']
                                                    if book['markets'][i]['key'] == 'spreads':
                                                        homeSpread = book['markets'][i]['outcomes'][1]['point']
                                                        awaySpread = book['markets'][i]['outcomes'][0]['point']
                                                
                                                for otherBook in bet['bookmakers']:
                                                    # if allBooks or sportBooks.count(otherBook['title']) > 0:
                                                        for j in range(len(otherBook['markets'])):
                                                            if book['markets'][i]['key'] == otherBook['markets'][j]['key']:
                                                                if otherBook['title'] != book['title']:
                                                                    awayOdd = 0
                                                                    homeIndex = 0
                                                                    if otherBook['markets'][j]['outcomes'][1]['name'] == bet['away_team']:
                                                                        awayOdd = otherBook['markets'][j]['outcomes'][1]['price']
                                                                        homeIndex = 0
                                                                    else:
                                                                        awayOdd = otherBook['markets'][j]['outcomes'][0]['price']
                                                                        homeIndex = 1
                                                                    if otherBook['markets'][j]['key'] == 'h2h' or otherBook['markets'][j]['outcomes'][homeIndex]['point'] == homeSpread:
                                                                        oddsSign = getOddSign(str(homeOdds), str(awayOdd))
                                                                        if oddsSign != 0:
                                                                            firstOdd = homeOdds
                                                                            secondOdd = awayOdd
                                                                            if oddsSign == 1:
                                                                                firstOdd = int(str(homeOdds)[1:])
                                                                                secondOdd = awayOdd
                                                                            elif oddsSign == 2:
                                                                                firstOdd = int(str(awayOdd)[1:])
                                                                                secondOdd = homeOdds

                                                                            if ((not(arbitrage) and not(freeBet)) or ((arbitrage or freeBet) and (firstOdd < secondOdd or oddsSign == 3))):
                                                                                currentRoi = 0.0
                                                                                totalPercent = 0.0
                                                                                homeAmount = 0.0
                                                                                awayAmount = 0.0
                                                                                if not(freeBet):
                                                                                    currentRoi = getROI(americanToDecimal(str(awayOdd)), americanToDecimal(str(homeOdds)), total=totalAmount)
                                                                                    totalPercent = 1/americanToDecimal(str(awayOdd)) + 1/americanToDecimal(str(homeOdds))
                                                                                    homeAmount = getAmount(americanToDecimal(str(homeOdds)),totalPercent,totalAmount)
                                                                                    awayAmount = getAmount(americanToDecimal(str(awayOdd)),totalPercent,totalAmount)
                                                                                else:
                                                                                    if americanToDecimal(str(homeOdds)) > americanToDecimal(str(awayOdd)):
                                                                                        results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(homeOdds)),minusOdd=americanToDecimal(str(awayOdd)))
                                                                                        homeAmount = round(results[0], 2)
                                                                                        awayAmount = round(results[1], 2)
                                                                                        betterOdd = americanToDecimal(str(homeOdds))
                                                                                    else:
                                                                                        results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(awayOdd)),minusOdd=americanToDecimal(str(homeOdds)))
                                                                                        awayAmount = round(results[0],2)
                                                                                        homeAmount = round(results[1],2)
                                                                                        betterOdd = americanToDecimal(str(awayOdd))
                                                                                    currentRoi = getFreeROI(total=totalAmount,betterAmount=results[0], betterOdd=betterOdd)
                                                                                if (not(arbitrage) and not(freeBet)) or currentRoi > roi:
                                                                                    print(f'{bet['sport_title']} - {betLive}')
                                                                                    output += f'{bet['sport_title']} - {betLive}\n'
                                                                                    if book['markets'][i]['key'] == 'spreads': 
                                                                                        print(f'Spread {bet['home_team']}({homeSpread}) v {bet['away_team']}({awaySpread}) - {date} ET')
                                                                                        output += f'Spread - {bet['home_team']}({homeSpread}) v {bet['away_team']}({awaySpread}) - {date} ET\n'
                                                                                    elif book['markets'][i]['key'] == 'h2h':
                                                                                        print(f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET')
                                                                                        output += f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET\n'
                                                                                    print(f'{book['title']}: ->{bet['home_team']}({homeOdds})<- v {bet['away_team']}({awayOdds})   ${homeAmount}')
                                                                                    print(f'{otherBook['title']}: {bet['home_team']}({otherBook['markets'][j]['outcomes'][homeIndex]['price']}) v ->{bet['away_team']}({awayOdd})<-   ${awayAmount}')
                                                                                    print(f'ROI: {round(currentRoi, 2)}%')
                                                                                    print(f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}')
                                                                                    print(' ')
                                                                                    output += f'{book['title']}: ->{bet['home_team']}({homeOdds})<- v {bet['away_team']}({awayOdds})   ${homeAmount}\n'
                                                                                    output += f'{otherBook['title']}: {bet['home_team']}({otherBook['markets'][j]['outcomes'][homeIndex]['price']}) v ->{bet['away_team']}({awayOdd})<-   ${awayAmount}\n'
                                                                                    output += f'ROI: {round(currentRoi, 2)}%\n'
                                                                                    output += f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}''\n\n'
                                        elif (len(book['markets'][0]['outcomes']) == 3 and not(freeBet)):
                                            homeOdds = 0
                                            awayOdds = 0
                                            drawOdds = 0
                                            hIndex = 0
                                            aIndex = 0
                                            dIndex = 0
                                            if (book['markets'][0]['outcomes'][0]['name'] == bet['home_team']):
                                                homeOdds = book['markets'][0]['outcomes'][0]['price']
                                                hIndex = 0
                                                if book['markets'][0]['outcomes'][1]['name'] == bet['away_team']:
                                                    awayOdds = book['markets'][0]['outcomes'][1]['price']
                                                    drawOdds = book['markets'][0]['outcomes'][2]['price']
                                                    aIndex = 1
                                                    dIndex = 2
                                                else:
                                                    drawOdds = book['markets'][0]['outcomes'][1]['price']
                                                    awayOdds = book['markets'][0]['outcomes'][2]['price']
                                                    aIndex = 2
                                                    dIndex = 1
                                            else:
                                                awayOdds = book['markets'][0]['outcomes'][0]['price']
                                                aIndex = 0
                                                if book['markets'][0]['outcomes'][1]['name'] == bet['home_team']:
                                                    homeOdds = book['markets'][0]['outcomes'][1]['price']
                                                    drawOdds = book['markets'][0]['outcomes'][2]['price']
                                                    hIndex = 1
                                                    dIndex = 2
                                                else:
                                                    drawOdds = book['markets'][0]['outcomes'][1]['price']
                                                    homeOdds = book['markets'][0]['outcomes'][2]['price']
                                                    dIndex = 1
                                                    hIndex = 2
                                            maxHome = americanToDecimal(homeOdds)
                                            maxAway = americanToDecimal(awayOdds)
                                            maxDraw = americanToDecimal(drawOdds)
                                            hBook = book['title']
                                            aBook = book['title']
                                            dBook = book['title']
                                            for otherBook in bet['bookmakers']:
                                                # if allBooks or sportBooks.count(otherBook['title']) > 0:
                                                    if (len(otherBook['markets'][0]['outcomes']) == 3):
                                                        if otherBook['title'] != book['title']:
                                                            if americanToDecimal(str(otherBook['markets'][0]['outcomes'][hIndex]['price'])) > maxHome:
                                                                maxHome = americanToDecimal(str(otherBook['markets'][0]['outcomes'][hIndex]['price'])) 
                                                                hBook = otherBook['title']
                                                            if americanToDecimal(str(otherBook['markets'][0]['outcomes'][aIndex]['price'])) > maxAway:
                                                                maxAway = americanToDecimal(str(otherBook['markets'][0]['outcomes'][aIndex]['price'])) 
                                                                aBook = otherBook['title']
                                                            if americanToDecimal(str(otherBook['markets'][0]['outcomes'][dIndex]['price'])) > maxDraw:
                                                                maxDraw = americanToDecimal(str(otherBook['markets'][0]['outcomes'][dIndex]['price'])) 
                                                                dBook = otherBook['title']
                                            if not(arbitrage) or isGood3(maxHome, maxAway, maxDraw):
                                                totalPerc = 1/maxHome + 1/maxDraw + 1/maxAway
                                                roi3 = getROI3(maxHome, maxAway, maxDraw, total=totalAmount)
                                                if not(arbitrage) or roi3 > roi:
                                                    print(f'{bet['sport_title']} - {betLive}')
                                                    print(f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET')
                                                    print(f'{hBook}: {bet['home_team']}({round(decimalToAmerican(maxHome))})   ${getAmount(maxHome, totalPerc, totalAmount)}')
                                                    print(f'{aBook}: {bet['away_team']}({round(decimalToAmerican(maxAway))})   ${getAmount(maxAway, totalPerc, totalAmount)}')
                                                    print(f'{dBook}: Draw({round(decimalToAmerican(maxDraw))})   ${getAmount(maxDraw, totalPerc, totalAmount)}')
                                                    print(f'ROI: {round(roi3, 2)}%')
                                                    print(f'Profit: ${round(totalAmount * (roi3 / 100), 2)}')
                                                    print(' ')
                                                    output += f'{bet['sport_title']} - {betLive}\n'
                                                    output += f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET\n'
                                                    output += f'{hBook}: {bet['home_team']}({round(decimalToAmerican(maxHome))})   ${getAmount(maxHome, totalPerc, totalAmount)}\n'
                                                    output += f'{aBook}: {bet['away_team']}({round(decimalToAmerican(maxAway))})   ${getAmount(maxAway, totalPerc, totalAmount)}\n'
                                                    output += f'{dBook}: Draw({round(decimalToAmerican(maxDraw))})   ${getAmount(maxDraw, totalPerc, totalAmount)}\n'
                                                    output += f'ROI: {round(roi3, 2)}%\n'
                                                    output += f'Profit: ${round(totalAmount * (roi3 / 100), 2)}''\n\n'
                    resquestsRemaining = response.headers.get('X-Requests-Remaining')
                    continueApiKeyCycle = False
                else:
                    requestsRemaining = response.headers.get('X-Requests-Remaining')
                    print(f'Response error: {response.status_code}. {requestsRemaining} requests remaining for apiKey{apiKeyNum}')
                    if apiKeyNum < 4:
                        apiKeyNum += 1
                        break
                    else:
                        continueApiKeyCycle = False
                        return [f'Response error', resquestsRemaining, [], apiKeyNum]
    if output == '':
        output = 'No bets found with those parameters'
    return [output, resquestsRemaining, jsons, apiKeyNum]

def filter(Results, Live, Pregame, Arbitrage, Roi, FreeBet, TotalAmount):
    output = ''
    live = Live
    pregame = Pregame
    arbitrage = Arbitrage
    freeBet = FreeBet
    totalAmount = TotalAmount
    roi = Roi

    for json in Results:
        for bet in json:
            if (live and bet['commence_time'] < datetime.now().astimezone().timestamp()) or (pregame and bet['commence_time'] > datetime.now().astimezone().timestamp()):
                betLive = 'Pre-game'
                if bet['commence_time'] < datetime.now().astimezone().timestamp():
                    betLive = 'Live'
                date: datetime = bet['commence_time']
                date = datetime.fromtimestamp(date).strftime('%m/%d/%Y %-I:%M%p')
                for book in bet['bookmakers']:
                    # if allBooks or sportBooks.count(book['title']) > 0: 
                        for i in range(len(book['markets'])):
                            if (len(book['markets'][i]['outcomes']) == 2):
                                if book['markets'][i]['key'] == 'totals': 
                                    overOdds = book['markets'][i]['outcomes'][0]['price']
                                    underOdds = book['markets'][i]['outcomes'][1]['price']
                                    for otherBook in bet['bookmakers']:
                                        # if allBooks or sportBooks.count(otherBook['title']) > 0:
                                            for j in range(len(otherBook['markets'])):
                                                if otherBook['markets'][j]['key'] == 'totals':
                                                    if otherBook['title'] != book['title']:
                                                        if otherBook['markets'][j]['outcomes'][0]['point'] == book['markets'][i]['outcomes'][0]['point']:
                                                            underOtherOdd = otherBook['markets'][j]['outcomes'][1]['price']
                                                            oddsSign = getOddSign(str(overOdds), str(underOtherOdd))
                                                            if oddsSign != 0:
                                                                firstOdd = overOdds
                                                                secondOdd = underOtherOdd
                                                                if oddsSign == 1:
                                                                    firstOdd = int(str(overOdds)[1:])
                                                                    secondOdd = underOtherOdd
                                                                elif oddsSign == 2:
                                                                    firstOdd = int(str(underOtherOdd)[1:])
                                                                    secondOdd = overOdds
                                                                if ((not(arbitrage) and not(freeBet)) or ((arbitrage or freeBet) and (firstOdd < secondOdd or oddsSign == 3))):
                                                                    currentRoi = 0.0
                                                                    totalPercent = 0.0
                                                                    overAmount = 0.0
                                                                    underAmount = 0.0
                                                                    if not(freeBet):
                                                                        currentRoi = getROI(americanToDecimal(str(underOtherOdd)), americanToDecimal(str(overOdds)), total=totalAmount)
                                                                        totalPercent = 1/americanToDecimal(str(underOtherOdd)) + 1/americanToDecimal(str(overOdds))
                                                                        overAmount = getAmount(americanToDecimal(str(overOdds)),totalPercent,totalAmount)
                                                                        underAmount = getAmount(americanToDecimal(str(underOtherOdd)),totalPercent,totalAmount)
                                                                    else:
                                                                        betterOdd = 0
                                                                        if americanToDecimal(str(overOdds)) > americanToDecimal(str(underOtherOdd)):
                                                                            results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(overOdds)),minusOdd=americanToDecimal(str(underOtherOdd)))
                                                                            overAmount = round(results[0],2)
                                                                            underAmount = round(results[1],2)
                                                                            betterOdd = americanToDecimal(str(overOdds))
                                                                        else:
                                                                            results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(underOtherOdd)),minusOdd=americanToDecimal(str(overOdds)))
                                                                            underAmount = round(results[0],2)
                                                                            overAmount = round(results[1],2)
                                                                            betterOdd = americanToDecimal(str(underOtherOdd))
                                                                        currentRoi = getFreeROI(total=totalAmount,betterAmount=results[0], betterOdd=betterOdd)
                                                                    if  ((not(arbitrage) and not(freeBet)) or currentRoi > roi):
                                                                        print(f'{bet['sport_title']} - {betLive}')
                                                                        print(f'Total - {bet['home_team']} v {bet['away_team']}  {book['markets'][i]['outcomes'][0]['point']} - {date} ET')
                                                                        print(f'{book['title']}: ->{book['markets'][i]['outcomes'][0]['name']}({overOdds})<- v {book['markets'][i]['outcomes'][1]['name']}({underOdds})   ${overAmount}')
                                                                        print(f'{otherBook['title']}: {otherBook['markets'][j]['outcomes'][0]['name']}({otherBook['markets'][j]['outcomes'][0]['price']}) v ->{otherBook['markets'][j]['outcomes'][1]['name']}({underOtherOdd})<-   ${underAmount}')
                                                                        print(f'ROI: {round(currentRoi, 2)}%')
                                                                        print(f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}')
                                                                        print(' ')
                                                                        output += f'{bet['sport_title']} - {betLive}\n'
                                                                        output += f'Total - {bet['home_team']} v {bet['away_team']}  {book['markets'][i]['outcomes'][0]['point']} - {date} ET\n'
                                                                        output += f'{book['title']}: ->{book['markets'][i]['outcomes'][0]['name']}({overOdds})<- v {book['markets'][i]['outcomes'][1]['name']}({underOdds})   ${overAmount}\n'
                                                                        output += f'{otherBook['title']}: {otherBook['markets'][j]['outcomes'][0]['name']}({otherBook['markets'][j]['outcomes'][0]['price']}) v ->{otherBook['markets'][j]['outcomes'][1]['name']}({underOtherOdd})<-   ${underAmount}\n'
                                                                        output += f'ROI: {round(currentRoi, 2)}%\n'
                                                                        output += f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}''\n\n'
                                else:
                                    homeOdds = 0
                                    awayOdds = 0
                                    homeSpread = 0
                                    awaySpread = 0
                                    if (book['markets'][i]['outcomes'][0]['name'] == bet['home_team']):
                                        homeOdds = book['markets'][i]['outcomes'][0]['price']
                                        awayOdds = book['markets'][i]['outcomes'][1]['price']
                                        if book['markets'][i]['key'] == 'spreads':
                                            homeSpread = book['markets'][i]['outcomes'][0]['point']
                                            awaySpread = book['markets'][i]['outcomes'][1]['point']
                                    else:
                                        homeOdds = book['markets'][i]['outcomes'][1]['price']
                                        awayOdds = book['markets'][i]['outcomes'][0]['price']
                                        if book['markets'][i]['key'] == 'spreads':
                                            homeSpread = book['markets'][i]['outcomes'][1]['point']
                                            awaySpread = book['markets'][i]['outcomes'][0]['point']
                                    
                                    for otherBook in bet['bookmakers']:
                                        # if allBooks or sportBooks.count(otherBook['title']) > 0:
                                            for j in range(len(otherBook['markets'])):
                                                if book['markets'][i]['key'] == otherBook['markets'][j]['key']:
                                                    if otherBook['title'] != book['title']:
                                                        awayOdd = 0
                                                        homeIndex = 0
                                                        if otherBook['markets'][j]['outcomes'][1]['name'] == bet['away_team']:
                                                            awayOdd = otherBook['markets'][j]['outcomes'][1]['price']
                                                            homeIndex = 0
                                                        else:
                                                            awayOdd = otherBook['markets'][j]['outcomes'][0]['price']
                                                            homeIndex = 1
                                                        if otherBook['markets'][j]['key'] == 'h2h' or otherBook['markets'][j]['outcomes'][homeIndex]['point'] == homeSpread:
                                                            oddsSign = getOddSign(str(homeOdds), str(awayOdd))
                                                            if oddsSign != 0:
                                                                firstOdd = homeOdds
                                                                secondOdd = awayOdd
                                                                if oddsSign == 1:
                                                                    firstOdd = int(str(homeOdds)[1:])
                                                                    secondOdd = awayOdd
                                                                elif oddsSign == 2:
                                                                    firstOdd = int(str(awayOdd)[1:])
                                                                    secondOdd = homeOdds

                                                                if ((not(arbitrage) and not(freeBet)) or ((arbitrage or freeBet) and (firstOdd < secondOdd or oddsSign == 3))):
                                                                    currentRoi = 0.0
                                                                    totalPercent = 0.0
                                                                    homeAmount = 0.0
                                                                    awayAmount = 0.0
                                                                    if not(freeBet):
                                                                        currentRoi = getROI(americanToDecimal(str(awayOdd)), americanToDecimal(str(homeOdds)), total=totalAmount)
                                                                        totalPercent = 1/americanToDecimal(str(awayOdd)) + 1/americanToDecimal(str(homeOdds))
                                                                        homeAmount = getAmount(americanToDecimal(str(homeOdds)),totalPercent,totalAmount)
                                                                        awayAmount = getAmount(americanToDecimal(str(awayOdd)),totalPercent,totalAmount)
                                                                    else:
                                                                        if americanToDecimal(str(homeOdds)) > americanToDecimal(str(awayOdd)):
                                                                            results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(homeOdds)),minusOdd=americanToDecimal(str(awayOdd)))
                                                                            homeAmount = round(results[0], 2)
                                                                            awayAmount = round(results[1], 2)
                                                                            betterOdd = americanToDecimal(str(homeOdds))
                                                                        else:
                                                                            results = getFreeAmountsWithTotal(total=totalAmount, plusOdd=americanToDecimal(str(awayOdd)),minusOdd=americanToDecimal(str(homeOdds)))
                                                                            awayAmount = round(results[0],2)
                                                                            homeAmount = round(results[1],2)
                                                                            betterOdd = americanToDecimal(str(awayOdd))
                                                                        currentRoi = getFreeROI(total=totalAmount,betterAmount=results[0], betterOdd=betterOdd)
                                                                    if (not(arbitrage) and not(freeBet)) or currentRoi > roi:
                                                                        print(f'{bet['sport_title']} - {betLive}')
                                                                        output += f'{bet['sport_title']} - {betLive}\n'
                                                                        if book['markets'][i]['key'] == 'spreads': 
                                                                            print(f'Spread {bet['home_team']}({homeSpread}) v {bet['away_team']}({awaySpread}) - {date} ET')
                                                                            output += f'Spread - {bet['home_team']}({homeSpread}) v {bet['away_team']}({awaySpread}) - {date} ET\n'
                                                                        elif book['markets'][i]['key'] == 'h2h':
                                                                            print(f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET')
                                                                            output += f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET\n'
                                                                        print(f'{book['title']}: ->{bet['home_team']}({homeOdds})<- v {bet['away_team']}({awayOdds})   ${homeAmount}')
                                                                        print(f'{otherBook['title']}: {bet['home_team']}({otherBook['markets'][j]['outcomes'][homeIndex]['price']}) v ->{bet['away_team']}({awayOdd})<-   ${awayAmount}')
                                                                        print(f'ROI: {round(currentRoi, 2)}%')
                                                                        print(f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}')
                                                                        print(' ')
                                                                        output += f'{book['title']}: ->{bet['home_team']}({homeOdds})<- v {bet['away_team']}({awayOdds})   ${homeAmount}\n'
                                                                        output += f'{otherBook['title']}: {bet['home_team']}({otherBook['markets'][j]['outcomes'][homeIndex]['price']}) v ->{bet['away_team']}({awayOdd})<-   ${awayAmount}\n'
                                                                        output += f'ROI: {round(currentRoi, 2)}%\n'
                                                                        output += f'Profit: ${round(totalAmount * (currentRoi / 100), 2)}''\n\n'
                            elif (len(book['markets'][0]['outcomes']) == 3 and not(freeBet)):
                                homeOdds = 0
                                awayOdds = 0
                                drawOdds = 0
                                hIndex = 0
                                aIndex = 0
                                dIndex = 0
                                if (book['markets'][0]['outcomes'][0]['name'] == bet['home_team']):
                                    homeOdds = book['markets'][0]['outcomes'][0]['price']
                                    hIndex = 0
                                    if book['markets'][0]['outcomes'][1]['name'] == bet['away_team']:
                                        awayOdds = book['markets'][0]['outcomes'][1]['price']
                                        drawOdds = book['markets'][0]['outcomes'][2]['price']
                                        aIndex = 1
                                        dIndex = 2
                                    else:
                                        drawOdds = book['markets'][0]['outcomes'][1]['price']
                                        awayOdds = book['markets'][0]['outcomes'][2]['price']
                                        aIndex = 2
                                        dIndex = 1
                                else:
                                    awayOdds = book['markets'][0]['outcomes'][0]['price']
                                    aIndex = 0
                                    if book['markets'][0]['outcomes'][1]['name'] == bet['home_team']:
                                        homeOdds = book['markets'][0]['outcomes'][1]['price']
                                        drawOdds = book['markets'][0]['outcomes'][2]['price']
                                        hIndex = 1
                                        dIndex = 2
                                    else:
                                        drawOdds = book['markets'][0]['outcomes'][1]['price']
                                        homeOdds = book['markets'][0]['outcomes'][2]['price']
                                        dIndex = 1
                                        hIndex = 2
                                maxHome = americanToDecimal(homeOdds)
                                maxAway = americanToDecimal(awayOdds)
                                maxDraw = americanToDecimal(drawOdds)
                                hBook = book['title']
                                aBook = book['title']
                                dBook = book['title']
                                for otherBook in bet['bookmakers']:
                                    # if allBooks or sportBooks.count(otherBook['title']) > 0:
                                        if (len(otherBook['markets'][0]['outcomes']) == 3):
                                            if otherBook['title'] != book['title']:
                                                if americanToDecimal(str(otherBook['markets'][0]['outcomes'][hIndex]['price'])) > maxHome:
                                                    maxHome = americanToDecimal(str(otherBook['markets'][0]['outcomes'][hIndex]['price'])) 
                                                    hBook = otherBook['title']
                                                if americanToDecimal(str(otherBook['markets'][0]['outcomes'][aIndex]['price'])) > maxAway:
                                                    maxAway = americanToDecimal(str(otherBook['markets'][0]['outcomes'][aIndex]['price'])) 
                                                    aBook = otherBook['title']
                                                if americanToDecimal(str(otherBook['markets'][0]['outcomes'][dIndex]['price'])) > maxDraw:
                                                    maxDraw = americanToDecimal(str(otherBook['markets'][0]['outcomes'][dIndex]['price'])) 
                                                    dBook = otherBook['title']
                                if not(arbitrage) or isGood3(maxHome, maxAway, maxDraw):
                                    totalPerc = 1/maxHome + 1/maxDraw + 1/maxAway
                                    roi3 = getROI3(maxHome, maxAway, maxDraw, total=totalAmount)
                                    if not(arbitrage) or roi3 > roi:
                                        print(f'{bet['sport_title']} - {betLive}')
                                        print(f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET')
                                        print(f'{hBook}: {bet['home_team']}({round(decimalToAmerican(maxHome))})   ${getAmount(maxHome, totalPerc, totalAmount)}')
                                        print(f'{aBook}: {bet['away_team']}({round(decimalToAmerican(maxAway))})   ${getAmount(maxAway, totalPerc, totalAmount)}')
                                        print(f'{dBook}: Draw({round(decimalToAmerican(maxDraw))})   ${getAmount(maxDraw, totalPerc, totalAmount)}')
                                        print(f'ROI: {round(roi3, 2)}%')
                                        print(f'Profit: ${round(totalAmount * (roi3 / 100), 2)}')
                                        print(' ')
                                        output += f'{bet['sport_title']} - {betLive}\n'
                                        output += f'Moneyline - {bet['home_team']} v {bet['away_team']} - {date} ET\n'
                                        output += f'{hBook}: {bet['home_team']}({round(decimalToAmerican(maxHome))})   ${getAmount(maxHome, totalPerc, totalAmount)}\n'
                                        output += f'{aBook}: {bet['away_team']}({round(decimalToAmerican(maxAway))})   ${getAmount(maxAway, totalPerc, totalAmount)}\n'
                                        output += f'{dBook}: Draw({round(decimalToAmerican(maxDraw))})   ${getAmount(maxDraw, totalPerc, totalAmount)}\n'
                                        output += f'ROI: {round(roi3, 2)}%\n'
                                        output += f'Profit: ${round(totalAmount * (roi3 / 100), 2)}''\n\n'
    if output == '':
        output = 'No bets found with those parameters'
    return [output]
runDatHoe = run(Sport='upcoming', Books='draftkings,fanduel,betmgm,espnbet,caesars', Totals=False, Moneyline=True, Spreads=False, Live=False, Pregame=True, Arbitrage=True, SearchAll=True, Roi=0, FreeBet=False, TotalAmount=1000)
fullOutput = runDatHoe[0]
filterDatHoe = filter(Results=runDatHoe[2], Live=False, Pregame=True, Arbitrage=True, Roi=2.5, FreeBet=False, TotalAmount=1000)
filteredOutput = filterDatHoe[0]
requestsRemaining = f'{runDatHoe[1]} requests remaining for API Key {runDatHoe[3]}'

emailContent = f'ROI > 2.5%:\n{filteredOutput}\n\n-------------------------\n\nAll Arbitrage Bets:\n{fullOutput}\n{requestsRemaining}'

def send_email():
    sender = emailAddress
    app_password = appSpecificPass
    recipient = emailAddress

    msg = MIMEText(emailContent)
    msg["Subject"] = "Arbitrage for today"
    msg["From"] = sender
    msg["To"] = recipient

    # Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.send_message(msg)

send_email()
