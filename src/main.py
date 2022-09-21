from time import sleep
import locale
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from VirtualSoccer import VirtualSoccer


class MyBet365:
    def __init__(self):
        while (True):
            try:
                self.start()
            except Exception as e:
                print(e)
                print("Erro ao criar driver e chamar a classe para buscar dados")
            # break
            sleep(60)

    def start(self):

        try:
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            options.add_argument("--disable-blink-features")
            options.add_argument(
                "--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-notifications")
            s = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=s, options=options)
        except Exception as e:
            print(e)
            print("Erro ao criar driver")
            return
        driver.get("https://www.nj.bet365.com/?lid=32#/AVR/B144/")
        sleep(1)
        driver.get("https://www.nj.bet365.com/?lid=32#/AVR/B146/R^1/")
        sleep(2)
        try:
            VirtualSoccer(driver, 4)

        except Exception as e:
            print(e)
            print("Erro ao executar classe para buscar dados do futebol virtual")

        sleep(2)
        driver.quit()


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, 'pt-BR.UTF-8')
    MyBet365()
