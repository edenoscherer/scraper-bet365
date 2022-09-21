from time import sleep
from numpy import size
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from datetime import datetime
from mongo import get_database


class VirtualSoccer:
    def __init__(self, driver: WebDriver, size: int):
        self.driver = driver
        i = 0

        self.driver.find_element(
            By.CLASS_NAME, 'ccm-CookieConsentPopup_Accept').click()
        games = []
        while (i < size):
            event = self.buscaDados(i)
            if (event != False):
                for game in event['games']:
                    games.append(game)
            i += 1

        # self.append_csv(games)
        self.save_mongo(games)

    def save_mongo(self, games: list):
        database = get_database()
        collection = database.get_collection('virtual-soccer')
        for game in games:
            try:
                res = collection.find_one(
                    {'event': game['event'], 'date': game['date']})
                if res == None:
                    collection.insert_one(game)
                elif size(game['details']) > 6:
                    collection.update_one({'_id': res['_id']}, {"$set": game})
            except Exception as e:
                print(e)
                print("Erro ao gravar registro na base de dados")
        print('Dados gravados na base')

    def append_csv(games: list):
        df = pd.DataFrame.from_dict(games)

        path = os.path.dirname(os.path.dirname(__file__))
        xlsx_path = os.path.join(path, 'data', 'VirtualSoccer.xlsx')
        try:
            old = pd.read_excel(xlsx_path)
        except FileNotFoundError:
            old = pd.DataFrame()

        new = pd.concat([old, df])
        new = new.drop_duplicates(subset=["event"])
        new.to_excel(xlsx_path, index=False)
        print("Dados gravados no arquivo " + xlsx_path)
        new.to_dict()

    def buscaDados(self, index: int):
        wait = WebDriverWait(self.driver, 10)
        self.driver.refresh()
        sleep(5)
        navElem = wait.until(EC.element_to_be_clickable(self.driver.find_elements(
            By.CSS_SELECTOR, ".vrl-HorizontalNavBarScroller_HScroll .vrl-MeetingsHeaderButton")[index]))
        webdriver.ActionChains(self.driver).click(navElem).perform()
        baseEvent = navElem.text
        print(baseEvent)
        sleep(2)
        try:
            btnResult = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".vr-EventTimesNavBar_ButtonContainer  .vr-ResultsNavBarButton")))
            sleep(1)
            print(btnResult.text)
            actions = webdriver.ActionChains(self.driver)
            actions.click(btnResult).perform()
            print('click ok')
            sleep(1)

            elems = self.driver.find_elements(
                By.CLASS_NAME, "vrr-HeadToHeadMarketGroup")
            games = []
            for elem in elems:
                elemShowMore = elem.find_element(
                    By.CLASS_NAME, "vrr-ShowMoreButton")
                actions.scroll_to_element(elemShowMore).click(
                    elemShowMore).perform()

                event = elem.find_element(
                    By.CLASS_NAME, "vrr-FixtureDetails_Event").text.strip()
                teamOne = elem.find_element(
                    By.CLASS_NAME, "vrr-HTHTeamDetails_TeamOne").text.strip()
                score = elem.find_element(
                    By.CLASS_NAME, "vrr-HTHTeamDetails_ScoreContainer").text.strip()
                teamTwo = elem.find_element(
                    By.CLASS_NAME, "vrr-HTHTeamDetails_TeamTwoContainer").text.strip()

                if len(teamOne) == 0:
                    continue
                date = datetime.utcnow()
                eventSplit = event.split('-')
                eventSplit = eventSplit[1].split('.')
                dt = date.replace(
                    hour=int(eventSplit[0]), minute=int(eventSplit[1]), second=0, microsecond=0)

                scoreSplit = score.split('-')
                teamOneScore = int(scoreSplit[0].strip())
                teamTwoScore = int(scoreSplit[1].strip())

                print("event: "+event)
                print("teamOne: "+teamOne)
                print("score: "+score)
                print("teamTwo: "+teamTwo)
                sleep(1)

                res = {
                    "baseEvent": baseEvent,
                    "event": event,
                    "teamOne": teamOne,
                    "teamTwo": teamTwo,
                    "score": score,
                    "teamOneScore": teamOneScore,
                    "teamTwoScore": teamTwoScore,
                    "date": dt,
                }

                detailsElements = elem.find_elements(
                    By.CLASS_NAME, "vrr-HeadToHeadParticipant")
                detailsSize = size(detailsElements)
                x = 0
                details = []
                while x < detailsSize:
                    try:
                        detailElement = detailsElements[x]
                        market = detailElement.find_element(
                            By.CLASS_NAME, 'vrr-HeadToHeadParticipant_Market').text.strip()
                        winner = detailElement.find_element(
                            By.CLASS_NAME, 'vrr-HeadToHeadParticipant_Winner').text
                        price = float(detailElement.find_element(
                            By.CLASS_NAME, 'vrr-HeadToHeadParticipant_Price').text)
                        details.append({
                            'market': market,
                            'winner': winner,
                            'price': price,
                        })

                        # res[market+' - Winner'] = detailElement.find_element(
                        #     By.CLASS_NAME, 'vrr-HeadToHeadParticipant_Winner').text
                        # res[market+' - Price'] = float(detailElement.find_element(
                        #     By.CLASS_NAME, 'vrr-HeadToHeadParticipant_Price').text)

                    except Exception as e:
                        print(e)
                        print("Erro detalhes das apostas")
                    x += 1
                res['details'] = details
                games.append(res)
                print('-------------------------------')

            return {
                "baseEvent": baseEvent,
                "games": games
            }
        except Exception as e:
            print(e)
            print("Erro ao clicar no botão de resultado e buscar os dados")
            return False
