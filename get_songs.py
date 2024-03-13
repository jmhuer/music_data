from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
def setup_driver():
    # Initialize the WebDriver
    driver = webdriver.Safari()  # Replace with your preferred driver
    driver.set_window_size(1280, 720)
    return driver

def extract_source(driver, website):
    # Navigate to the website and return the page source
    driver.get(website)
    return driver.page_source

def find_pattern_in_source(source):
    # Updated pattern to match the path and stop at the first double quote
    pattern = re.compile(r'(/theorytab/view/[^/]+/[^/"]+)')
    return pattern.findall(source)

def process_artists_file(input_file, output_file, base_url):
    driver = setup_driver()  # Initialize the web driver
    
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
        for line in infile:
            website = base_url + line.strip()  # Construct the full website URL
            source = extract_source(driver, website)  # Extract the page source
            matches = find_pattern_in_source(source)  # Find all matches
            for match in matches:
                full_url = base_url + match
                outfile.write(full_url + '\n')  # Write each match to the output file
    
    driver.quit()  # Close the browser once done

# Example usage
input_file = 'artists.txt'  # Update this path
output_file = 'output.txt'  # Update this path
base_url = "https://www.hooktheory.com"

process_artists_file(input_file, output_file, base_url)