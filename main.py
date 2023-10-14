import logging

import yaml
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def logger_config():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

    file_handler = logging.FileHandler("epic_games_reminder.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    return logger


logger = logger_config()


def selenium_prep(display: bool = False):
    options = webdriver.ChromeOptions()

    if display == False:
        options.add_argument("--headless")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--no-sandbox")
    elif display == True:
        options.add_argument("--start-maximized")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # options.add_argument("user-data-dir=/root/Selenium")
    # options.add_argument(f"profile-directory={profile_directory}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    return driver


def free_epic_games():
    driver = selenium_prep()
    driver.get("https://www.epicgames.com/store/en-US/")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".css-1myhtyb"))
    )
    games = driver.find_elements(By.CSS_SELECTOR, ".css-1myhtyb .css-5auk98")

    games_list = []
    games_next_week = []

    for item in games:
        game_name = item.text.split("\n")[1]
        game_link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        if "FREE NOW" in item.text:
            games_list.append((game_name, game_link))
        elif "COMING SOON" in item.text:
            games_next_week.append((game_name, game_link))
    driver.close()
    return games_list, games_next_week


def discord_message(webhook_url, message):
    headers = {"Content-Type": "application/json"}
    data = {
        "username": "Epic Games",
        "avatar_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/1200px-Epic_Games_logo.svg.png",
        "content": message,
    }
    response = requests.post(webhook_url, headers=headers, json=data)
    # logger.debug(f"Discord message sent {r.text}")


if __name__ == "__main__":
    with open("config.yml", "r") as f:
        data = yaml.safe_load(f)

    games_list, games_next_week = free_epic_games()

    message = (
        "Don't forget to claim free games on epic games\n",
        "https://www.epicgames.com/store/en-US/\n\n",
        "These games are available for free\n",
    )
    for game, link in games_list:
        message += f"• [{game}]({link})\n"

    message += "\nThese games will be available next week\n"
    for game, link in games_next_week:
        message += f"• [{game}]({link})\n"
    discord_message(data['disord_webhook_url'], message)
