from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pyautogui

def setup_driver():
    driver = webdriver.Safari()  # Or your preferred driver
    driver.set_window_size(1280, 720)  # Set the window size
    return driver

def login(driver, login_url, username, password):
    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.native-input.sc-ion-input-md[placeholder='Username']")))
    username_input = driver.find_element(By.CSS_SELECTOR, "input.native-input.sc-ion-input-md[placeholder='Username']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input.native-input.sc-ion-input-md[placeholder='Password']")
    username_input.send_keys(username)
    password_input.send_keys(password)
    sleep(1)
    # Additional click to continue the session
    screen_width, screen_height = 1280, 720
    pyautogui.click(screen_width//2, (screen_height//3)*2)

def save_file():
    # Assumes you're already focused on the desired window/frame
    pyautogui.click(247, 160)  # First click position
    pyautogui.click(294, 317)  # Second click position
    sleep(10)  # Wait for the action to complete

def process_songs(driver, songs):
    for url in songs:
        driver.get(url)
        sleep(2)  # Wait for the page to load
        save_file()

driver = setup_driver()

login_url = 'https://hookpad.hooktheory.com/?idOfSong=nZgWEAZQory&enableYouTube=true&openBandEditorOnInit=true'
# Replace "your_username" and "your_password" with your actual login credentials
login(driver, login_url, "jmhuer", "23o6952015.")

songs = [
    'https://hookpad.hooktheory.com/?idOfSong=nZgWEAZQory&enableYouTube=true&openBandEditorOnInit=true',
    'https://hookpad.hooktheory.com/?idOfSong=eWxLyNeEoaK&enableYouTube=false&openBandEditorOnInit=true'
    # Add more URLs as needed
]

process_songs(driver, songs)

driver.quit()
