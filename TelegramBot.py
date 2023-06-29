from typing import Final
import os
from dotenv import load_dotenv
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()



from selenium.common import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep



TOKEN = os.getenv('TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME')

print(os.getenv('TOKEN'))


ricerca = "sviluppatore java junior"
luogo = "Italia"


async def set_ricerca(update, context):

    global ricerca
    value = update.message.text.partition(' ')[2]
    if value == '':
        await update.message.reply_text("Inserisci il campo")
    else:
        ricerca = value
        await update.message.reply_text("impostata ricerca su " + ricerca)

async def set_luogo(update, context):

    global luogo
    value = update.message.text.partition(' ')[2]
    if value == '':
        await update.message.reply_text("Inserisci il campo")
    else:
        luogo = value
        await update.message.reply_text("impostata ricerca su " + luogo)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    #options.add_argument("--start-maximized");
    service = Service(executable_path='C:\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)


    SITE_ID = "https://it.indeed.com/"
    driver.get(SITE_ID)
    lista_informazioni = []

    driver.refresh()

    selezione_input = WebDriverWait(driver, 10).until(lambda x: driver.find_element(By.ID, 'text-input-what'))

    selezione_input.send_keys(ricerca)


    selezione_input_where = WebDriverWait(driver, 10).until(lambda x: driver.find_element(By.ID, 'text-input-where'))

    selezione_input_where.send_keys(luogo)


    bottone_cerca = WebDriverWait(driver, 10).until(lambda x: driver.find_element(By.CLASS_NAME, 'yosegi-InlineWhatWhere-primaryButton'))

    bottone_cerca.click()
    for i in range(1, 6):
        try:
            list_element = driver.find_element(By.ID, 'mosaic-jobResults')
            job_elements = list_element.find_elements(By.CSS_SELECTOR, 'div.job_seen_beacon')
            sleep(1)

            for job_element in job_elements:
                 if "remoto" in job_element.text:
                    try:
                        try:
                            close_button = driver.find_element(By.CLASS_NAME, 'icl-Modal-close')
                            close_button.click()
                            print("trovata finestra pop-up")
                        except NoSuchElementException:
                            sleep(1)
                            driver.execute_script(
                                "arguments[0].scrollIntoView({'block':'center','inline':'center'})",
                                job_element)
                            job_element.click()
                            link_element = WebDriverWait(driver, 10).until(lambda x: job_element.find_element(By.TAG_NAME, 'a'))
                            link = link_element.get_attribute('href')
                            informazioni = WebDriverWait(driver, 20).until(lambda x: driver.find_element(By.ID, 'jobsearch-ViewjobPaneWrapper'))
                            job_title = driver.find_element(By.CLASS_NAME, 'jobsearch-JobInfoHeader-title')
                            html_link = f'<a href="{link}">{"click here"}</a>'
                            lista_informazioni.append(informazioni.text)
                            print("NoSuchElement")
                            await update.message.reply_html("Found a job: \n" + job_title.text + "\nLink: " + html_link)
                    except ElementClickInterceptedException:
                        try:
                            driver.execute_script(
                                "arguments[0].scrollIntoView({'block':'center','inline':'center'})",
                                job_element)
                            job_element.click()
                            link_element = WebDriverWait(driver, 10).until(
                                lambda x: job_element.find_element(By.TAG_NAME, 'a'))
                            link = link_element.get_attribute('href')
                            informazioni = WebDriverWait(driver, 10).until(
                                lambda x: driver.find_element(By.ID, 'jobsearch-ViewjobPaneWrapper'))
                            job_title = driver.find_element(By.CLASS_NAME, 'jobsearch-JobInfoHeader-title')
                            html_link = f'<a href="{link}">{"click here"}</a>'
                            lista_informazioni.append(informazioni.text)
                            sleep(1)
                            print("Element Intercepted")
                            await update.message.reply_html("Found a job: \n" + job_title.text + "\nLink: " + html_link)
                        except ElementClickInterceptedException:
                            print("lost post")
                            pass

            next_page = WebDriverWait(driver, 10).until(
                                lambda x: driver.find_element("xpath", '//a[@data-testid="pagination-page-next"]'))
            next_page_url = next_page.get_attribute("href")
            driver.get(next_page_url)
            try:
                close_button = driver.find_element(By.CLASS_NAME, 'icl-Modal-close')
                close_button.click()
                print("trovata finestra pop-up")
            except NoSuchElementException:
                pass
        except NoSuchElementException:
            print("here")
            pass
    await update.message.reply_text("Scraping completed. Found {} jobs.".format(len(lista_informazioni)))

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('search', start_command))

    app.add_handler(CommandHandler('set_ricerca', set_ricerca))

    app.add_handler(CommandHandler('set_luogo', set_luogo))


    print('Polling...')

    app.run_polling(poll_interval=5)


