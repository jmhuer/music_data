from selenium import webdriver
import re
import os
import selenium

def setup_driver():
    driver = webdriver.Safari()  # Or your preferred driver
    driver.set_window_size(1280, 720)
    driver.set_page_load_timeout(40)  
    return driver


def extract_sections_and_songs(driver, url):
    attempt_count = 0
    while attempt_count < 2:  # Allow for the initial attempt and one retry
        try:
            driver.get(url)
            page_source = driver.page_source
            sections = re.findall(r'<a name="([^"]+)"></a>', page_source)
            songs = re.findall(r'href="([^"]*?idOfSong[^"]+)"', page_source)
            return list(zip(sections, songs)) if len(sections) == len(songs) else []
        except selenium.common.exceptions.WebDriverException as e:
            print(f"Attempt {attempt_count + 1}: Exception occurred while trying to load the page: {url}")
            print(e)
            attempt_count += 1
            if attempt_count < 2:
                print("Retrying...")
            else:
                print("Failed after retrying. Exiting.")
                exit()


def find_last_processed_link(output_file):
    last_line = None
    try:
        with open(output_file, 'r') as file:
            for line in file:
                last_line = line.strip()
        if last_line:
            return last_line.split(',')[0]  # Assuming the URL is the first element
    except FileNotFoundError:
        return None

def process_links(input_file, output_file):
    last_processed_link = find_last_processed_link(output_file)
    continue_processing = not bool(last_processed_link)
    
    driver = setup_driver()
    with open(input_file, 'r') as infile, open(output_file, 'a' if last_processed_link else 'w') as outfile:
        if not last_processed_link:
            outfile.write("original_link,section,link\n")  # Write header if starting fresh
        
        for line in infile:
            original_link = line.strip()
            if original_link == last_processed_link:
                continue_processing = True  # Found where we left off, start processing next lines
                continue
            
            if continue_processing:
                section_song_matches = extract_sections_and_songs(driver, original_link)
                for section, song in section_song_matches:
                    outfile.write(f"{original_link},{section},{song}\n")
    
    driver.quit()

# Example usage
input_file = 'output.txt'  # Update with the path to your input file
output_file = 'sections_output.csv'  # Path where you want to save the output

process_links(input_file, output_file)
