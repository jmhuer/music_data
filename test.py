import csv
import sys
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def setup_driver():
    # Picture setting up a car for a road trip, this gets everything ready.
    driver = webdriver.Safari()
    driver.set_window_size(1280, 720)
    return driver

def login(driver, login_url, username, password):
    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.native-input.sc-ion-input-md[placeholder='Username']")))
    username_input = driver.find_element(By.CSS_SELECTOR, "input.native-input.sc-ion-input-md[placeholder='Username']")
    password_input = driver.find_element(By.CSS_SELECTOR, "input.native-input.sc-ion-input-md[placeholder='Password']")
    username_input.send_keys(username)
    password_input.send_keys(password)
    sleep(1)
    auth_button_xpath = '/html/body/div/div/div[20]/div/div/ion-button'
    auth_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, auth_button_xpath)))
    auth_button.click()
    sleep(5)

def save_file(driver):
    # This is like navigating through a menu in a game to save your progress.
    file_menu_button_xpath = '/html/body/div/div/div[1]/div[1]/div/div[1]/div[3]/div/div/button'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, file_menu_button_xpath))).click()
    subsequent_button_xpath = '/html/body/div/div[2]/div/button[5]'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, subsequent_button_xpath))).click()

def process_songs_from_csv(driver, filename):
    # Imagine this as reading through a guest list for an event and personally greeting each guest.
    with open(filename, newline='') as csvfile:
        song_reader = csv.reader(csvfile)
        next(song_reader, None)  # This skips the header row
        for row in song_reader:
            song_url = row[2]  # The URL is the VIP guest to greet
            driver.get(song_url)
            sleep(3)
            save_file(driver)

def main():
    parser = argparse.ArgumentParser(description='Process songs from a CSV file.')
    parser.add_argument('--filename', type=str, help='The filename of the CSV containing the song links')
    args = parser.parse_args()

    driver = setup_driver()

    login_url = 'https://hookpad.hooktheory.com/?idOfSong=eWxLyNeEoaK&enableYouTube=false&openBandEditorOnInit=false'
    login(driver, login_url, "jmhuer", "23o6952015.")

    process_songs_from_csv(driver, args.filename)

    driver.quit()

if __name__ == "__main__":
    main()
