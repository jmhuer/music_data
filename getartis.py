import os
import re

def extract_artists(directory_path):
    pattern = re.compile(r'"/theorytab/artists/([^"/]+)/([^"/]+)"')  # Pattern to match the desired strings
    extracted_links = set()  # Using a set to avoid duplicate entries

    # Iterate through each file in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".html"):  # Ensure it's an HTML file
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                contents = file.read()
                matches = pattern.findall(contents)  # Find all matches in the current file
                for match in matches:
                    link = f'/theorytab/artists/{match[0]}/{match[1]}'  # Removed quotes around the link
                    extracted_links.add(link)

    # Write the extracted links to a text file
    with open("artists.txt", 'w', encoding='utf-8') as output_file:
        for link in sorted(extracted_links):  # Sort the links before writing
            output_file.write(link + '\n')

    return len(extracted_links)  # Return the count of unique links found

# Provide the correct path to your 'artists' directory here
directory_path = 'artists/'
extracted_count = extract_artists(directory_path)
print(f"Extracted {extracted_count} unique artist links.")
