import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()

step = 1
while True:
    url = f'https://www.freecodecamp.org/learn/2022/responsive-web-design/learn-typography-by-building-a-nutrition-label/step-{step}'

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Check for 404 error
    if "404" in driver.title:
        print(f"Step {step} not found. Exiting...")
        driver.quit()
        break

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
    output_filename = f"step-{step}.txt"
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(html_content + '\n\n' + css_content)

    print(f"Content saved to {output_filename}")

    driver.quit()
    step += 1
