import os
import sys
import re
import unicodedata
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def make_valid_filename(s):
    """
    Sanitizes a string to be a valid filename across different operating systems.
    """
    # Normalize unicode characters
    s = unicodedata.normalize('NFKD', s).encode(
        'ascii', 'ignore').decode('ascii')
    # Remove invalid characters
    s = re.sub(r'[<>:"/\\|?*]', '', s)
    return s.strip()


def get_language_from_url(url):
    """
    Extracts the programming language from the Codewars kata URL.
    """
    path = urlparse(url).path
    # Expected path format: '/kata/<kata-id>/train/<language>'
    parts = path.strip('/').split('/')
    if len(parts) >= 4 and parts[-2] == 'train':
        language = parts[-1]
        return language
    else:
        return None


def create_kata_folder_structure(base_path, level, kata_name):
    """
    Creates the directory structure for the kata.
    """
    level = make_valid_filename(level)
    kata_name = make_valid_filename(kata_name)
    level_path = os.path.join(base_path, level)
    kata_path = os.path.join(level_path, kata_name)
    os.makedirs(kata_path, exist_ok=True)
    return kata_path


def save_file(content, filepath):
    """
    Saves content to a file with the specified filepath.
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)


def scrape_codewars_kata(url):
    """
    Scrapes the Codewars kata page to extract the level, name, description,
    initial code, and test code.
    """
    language = get_language_from_url(url)
    if not language:
        print("Could not determine the language from the URL.")
        return None, None, None, None, None

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        # Load the page
        driver.get(url)

        # Wait for the loading overlay to disappear
        WebDriverWait(driver, 15).until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.fixed.inset-0.w-full.h-screen.z-50.overflow-hidden"))
        )

        # Wait until the description is present and visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'description'))
        )

        # Extract HTML once the loading is complete
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract Kata details
        level_element = soup.find('div', class_='inner-small-hex')
        kata_name_element = soup.find('h4')
        description_element = soup.find('div', id='description')

        level = level_element.text.strip() if level_element else 'Unknown Level'
        kata_name = kata_name_element.text.strip() if kata_name_element else 'Unknown Kata'
        description = description_element.text.strip(
        ) if description_element else 'No Description'

        # Extract the initial code from the code editor
        code_editor_element = driver.find_element(By.ID, 'code')
        code_mirror_code = code_editor_element.find_element(
            By.CLASS_NAME, 'CodeMirror')
        initial_code = driver.execute_script(
            "return arguments[0].CodeMirror.getValue();", code_mirror_code)

        # Extract the test code from the fixture editor
        fixture_editor_element = driver.find_element(By.ID, 'fixture')
        code_mirror_fixture = fixture_editor_element.find_element(
            By.CLASS_NAME, 'CodeMirror')
        test_code = driver.execute_script(
            "return arguments[0].CodeMirror.getValue();", code_mirror_fixture)

        return level, kata_name, description, initial_code, test_code

    except Exception as e:
        print(f"An error occurred while scraping the kata: {e}")
        return None, None, None, None, None
    finally:
        driver.quit()


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <kata_url>")
        return

    url = sys.argv[1]
    language = get_language_from_url(url)
    if not language:
        print("Could not determine the language from the URL.")
        return

    base_path = f'./{language}'  # Base folder to save kata

    # Scraping and retrieving kata details
    level, kata_name, description, initial_code, test_code = scrape_codewars_kata(
        url)

    if not all([level, kata_name, description]):
        print("Failed to retrieve the necessary kata details.")
        return

    markdown_content = f"# {kata_name}\n\n{description}"

    if language == 'php':
        initial_code = f"<?php declare(strict_types=1);\n\n{initial_code}"
        test_code = f"<?php declare(strict_types=1);\n\n{test_code}"

    # Preparing file paths
    kata_path = create_kata_folder_structure(base_path, level, kata_name)
    filename_base = make_valid_filename(kata_name.replace(' ', '').lower())
    markdown_filename = make_valid_filename(f"{kata_name}.md")
    markdown_path = os.path.join(kata_path, markdown_filename)
    code_file_extension = {'php': 'php', 'python': 'py',
                           'javascript': 'js'}.get(language, language)
    code_file_path = os.path.join(
        kata_path, f"{filename_base}.{code_file_extension}")
    test_file_path = os.path.join(
        kata_path, f"{filename_base}Test.{code_file_extension}")

    # Saving files
    save_file(markdown_content, markdown_path)
    save_file(initial_code, code_file_path)
    save_file(test_code, test_file_path)

    print(f"Kata files created successfully in: {kata_path}")


if __name__ == '__main__':
    main()
