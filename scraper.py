from typing import Optional, List

from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class Scraper:
    options = Options()
    options.headless = True  # TODO: Implement headless option in GUI
    driver = webdriver.Chrome(options=options)

    def __init__(self, username: str, password: str):
        driver = self.driver
        driver.get("https://connect.mheducation.com/connect/login/index.htm")
        assert "McGraw-Hill Connect" in driver.title
        print("Opened textbook website", flush=True)

        username_field = driver.find_element_by_id('userName')
        password_field = driver.find_element_by_id('password')
        username_field.send_keys(username)
        password_field.send_keys(password, Keys.ENTER)  # TODO: Change to button click
        assert "McGraw-Hill Connect | My Courses" in driver.title
        print("Logged in", flush=True)

        wait = WebDriverWait(driver, 5)
        apush_course = wait.until(expected_conditions.element_to_be_clickable(
            (By.LINK_TEXT, "CHS APUSH")))
        apush_course.click()
        apush_book = wait.until(expected_conditions.element_to_be_clickable(
            (By.LINK_TEXT, "American History: Connecting with the Past - AP")))
        assert "McGraw-Hill Connect | Section Home" in driver.title
        print("Navigated to course", flush=True)
        apush_book.click()
        assert "McGraw-Hill Connect - Ebook" in driver.title
        print("Navigated to book", flush=True)

        driver.switch_to.frame('ebookframe')

    def section_body(self, section: str) -> str:
        page_start = section.index('(')
        title = section[:page_start - 1]
        page = int(section[page_start + 4:-1])

        turns = 0
        while turns < 3:
            self.to_page(page + turns)  # TODO: Do not turn to page if already there
            body = self.find_body(title)
            if body is None:
                turns += 1
            else:
                return body  # TODO: Return summarized body
        # TODO: Check end of chapter glossary

    def find_body(self, title) -> Optional[str]:
        driver = self.driver
        wait = WebDriverWait(driver, 8)
        wait.until(expected_conditions.invisibility_of_element_located((By.ID, 'loader')))
        heading_divs = driver.find_elements_by_class_name('sectitle')
        note_divs = driver.find_elements_by_class_name('note')

        for heading_div in heading_divs + note_divs:
            heading = heading_div.text
            if fuzz.ratio(heading.casefold(), title.casefold()) > 90:
                xpath = "//" + heading_div.tag_name + "[@id='" + heading_div.get_attribute('id') + "']/following-sibling::*"
                following_divs = heading_div.find_elements_by_xpath(xpath)
                paragraphs: List[str] = list()
                for div in following_divs:
                    if div.tag_name == 'p':
                        paragraphs.append(div.text)
                    elif fuzz.ratio(div.text.casefold(), heading.casefold()) > 90:
                        pass
                    else:
                        break
                return ' '.join(paragraphs)
        return None

    def to_page(self, page: int):
        driver = self.driver
        page_input = driver.find_element_by_id('toolbar_jumppg')
        wait = WebDriverWait(driver, 8)
        wait.until(expected_conditions.invisibility_of_element_located((By.ID, 'loader')))
        page_go = wait.until(expected_conditions.element_to_be_clickable(
            (By.CLASS_NAME, 'toolbaricon_input_jumpgo')))
        page_input.clear()
        page_input.send_keys(page)
        page_go.click()

        body = driver.find_element_by_tag_name('body')
        wait.until(lambda d: 'cursor' not in body.get_attribute('style'))

    def close(self):
        self.driver.close()
