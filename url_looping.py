import os
import time
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument('--headless')

def process_step(url_template, folder_name, step):
    url = url_template.format(step=step)

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Check for 404 error
    if "404" in driver.title:
        print(f"Step {step} not found.")
        driver.quit()
        return False

    # Wait for 3 seconds
    time.sleep(3)
    # Wait for the iframe to be loaded
    try:
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "fcc-main-frame"))
        )
    except TimeoutError:
        print("Timed out waiting for the iframe to load.")
        driver.quit()

    # Switch to the iframe
    driver.switch_to.frame(iframe)

    # Use JavaScript to get the iframe's content as an HTML string
    iframe_content = driver.execute_script("return document.documentElement.outerHTML;")

    # Parse the iframe content
    soup = BeautifulSoup(iframe_content, 'html.parser')

    # Extract the HTML and CSS
    html_content = str(soup.body)
    css_content = str(soup.find('style', class_='fcc-injected-styles'))

    # Save the content to a text file
    output_filename = f"{folder_name}/step-{step}.txt"
    os.makedirs(folder_name, exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(html_content + '\n\n' + css_content)

    print(f"Content saved to {output_filename}")

    driver.quit()
    return True

with open("urls.txt", "r") as file:
    for line in file:
        url_template, folder_name = line.strip().split(", ")
        folder_name = folder_name.strip()

        start_step = 1
        batch_size = 10
        completed_steps = 0
        successful_steps = 0

        while True:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Run a batch of steps concurrently
                results = list(executor.map(lambda step: process_step(url_template, folder_name, step), range(start_step, start_step + batch_size)))

            # Count how many steps were successful in the current batch
            successful_steps = results.count(True)

            # Update the number of completed steps
            completed_steps += successful_steps

            # Check if all browsers in the current batch failed
            if successful_steps < batch_size:
                break

            # Update the starting step for the next batch
            start_step += batch_size

        print(f"Completed all {completed_steps} steps for {folder_name}.")
