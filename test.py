import csv
import sys
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
import os
import time 

def setup_driver():
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
    file_menu_button_xpath = '/html/body/div/div/div[1]/div[1]/div/div[1]/div[3]/div/div/button'
    print("about to click")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, file_menu_button_xpath))).click()
    subsequent_button_xpath = '/html/body/div/div[2]/div/button[5]'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, subsequent_button_xpath))).click()


def get_latest_file_name(download_dir):
    """Get the last modified file in the download directory."""
    if not os.path.exists(download_dir):
        raise FileNotFoundError(f"Directory '{download_dir}' does not exist.")
    
    files = os.listdir(download_dir)
    if not files:
        return None
    
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
    return latest_file

    # If no new file appears within the wait_time
    return None
def process_songs_from_csv(driver, filename, output_filename):
    download_dir = "/Users/juanhuerta/Downloads/"  # Set to your system's download path
    last_url_processed = None
    start_processing = False

    # Determine the last URL processed if the output file exists
    if os.path.exists(output_filename):
        with open(output_filename, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                last_url_processed = last_line.split(',')[2].strip()

    with open(filename, 'r', newline='') as csvfile, open(output_filename, 'a', newline='') as outfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(outfile)
        header = next(reader)  # Skip header

        if os.path.getsize(output_filename) == 0:  # If the output file is empty, write the header
            writer.writerow(header + ['Downloaded File Name', 'Timestamp'])  # Assuming the output file format

        for row in reader:
            song_url = row[2].replace("openBandEditorOnInit=true", "openBandEditorOnInit=false")

            # Start processing either immediately or after finding the last processed URL
            if last_url_processed is None or start_processing or row[2] == last_url_processed:
                start_processing = True  # Found the last processed URL, start processing the next
                if row[2] == last_url_processed:  # Skip the last processed URL itself
                    continue

                driver.get(song_url)
                sleep(4)
                save_file(driver)
                sleep(4)
                latest_file_name = get_latest_file_name(download_dir)
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow(row + [latest_file_name, current_timestamp])

# Now, just ensure the rest of your main() function and other parts are properly calling this function.


def main():
    parser = argparse.ArgumentParser(description='Process songs from a CSV file and track downloads.')
    parser.add_argument('--filename', type=str, required=True, help='The filename of the CSV containing the song links')
    parser.add_argument('--output', type=str, required=True, help='Output CSV filename to track downloads')
    args = parser.parse_args()

    driver = setup_driver()
    login_url = 'https://hookpad.hooktheory.com/?idOfSong=eWxLyNeEoaK&enableYouTube=false&openBandEditorOnInit=false'
    login(driver, login_url, "jmhuer", "23o6952015.")
    process_songs_from_csv(driver, args.filename, args.output)
    driver.quit()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying...")
            sleep(10)
