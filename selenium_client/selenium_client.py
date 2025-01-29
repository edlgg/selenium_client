import os
from datetime import datetime, timezone
import time
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

CURRENT_DIR = Path(__file__).resolve().parent
tmp_dir = CURRENT_DIR / "../../tmp"

class SeleniumClient:
    def __init__(self, browser='firefox'):
        self.driver: webdriver = self.get_driver(browser)
        self.driver.set_page_load_timeout(10)

    def get_driver(self, browser) -> webdriver:
        if browser == 'firefox':
            options = webdriver.FirefoxOptions()
            if os.environ["ENV"] in ["prod", "staging"]:
                options.add_argument('--width=900')
                options.add_argument('--height=1080')
                options.add_argument('--headless')

            service_log_file = str(CURRENT_DIR / "../../geckodriver.log")
            firefox_binary_location = "/usr/bin/firefox"
            geckodriver_path = "/usr/local/bin/geckodriver"
            return webdriver.Firefox(
                options=options,
                service_log_path=service_log_file,
                # firefox_binary=firefox_binary_location,
                # executable_path=geckodriver_path
            )
        else:
            raise ValueError(f"Browser {browser} not supported.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def navigate(self, url):
        success = False
        current_time = datetime.now(timezone.utc)
        while not success and (datetime.now(timezone.utc) - current_time).seconds < 60:
            try:
                self.driver.get(url)
                success = True
            except:
                print("Failed to load page, retrying")
                time.sleep(2)
        if not success:
            print(f"Failed to load page {url}")
            raise Exception("Failed to load page")

    def click_by_selector(self, selector):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.click()
    
    def click_select_item(self, selector, item_text):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        element.find_element(By.XPATH, f"//*[contains(text(), '{item_text}')]").click()
    
    def click_select_option_by_text(self, selector, option_text):
        select_element = Select(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))))
        select_element.select_by_visible_text(option_text)
    
    def click_by_id(self, id):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, id)))
        element.click()
    
    def click_by_class(self, class_name):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
        element.click()
    
    def click_by_name(self, name):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, name)))
        element.click()

    # def click_by_text_contains(self, text):
    #     element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]")))
    #     element.click() 

    def get_by_text_contains(self, text):
        try:
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]")))
            return element
        except Exception:
            return None

    def click_by_text_contains(self, text):
        # Find the element
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]")))

        # Scroll the element into view using JavaScript
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        
        # Wait for the element to be clickable again
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]")))

        # Click the element
        element.click()
    
    def click_by_xpath(self, xpath):
        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
    
    def get_by_xpath(self, xpath):
        self.driver.find_element(By.XPATH, xpath)

    def input_text(self, selector, text):
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        element.clear()
        element.send_keys(text)

    def select_from_dropdown(self, selector, option_text):
        select_element = Select(WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))))
        select_element.select_by_visible_text(option_text)

    def close(self):
        self.driver.quit()
    
    def find_text(self, text) -> bool:
        try:
            e = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            return True
        except NoSuchElementException:
            return False
    
    def get_item_urls(self):
        items = self.driver.find_elements(By.CSS_SELECTOR, ".contenedor .item")
        urls = []
        for item in items:
            urldetalle = item.get_attribute("urldetalle")
            k_av = item.get_attribute("k_av")
            if urldetalle and k_av:
                urldetalle = urldetalle.replace("PostBienesRaices", "BienesRaices")
                urls.append(urldetalle)
        return urls

    def click_next(self):
        try:
            next_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@onclick=\"btnPaginacion(1, 'Sig');\"]")))
            next_button.click()
        except NoSuchElementException:
            print("Next button not found or not clickable.")
    
    # def get_image_urls(self):
    #     images = self.driver.find_elements(By.CSS_SELECTOR, ".contenedor .item a[data-fancybox='zoom']")
    #     img_urls = [img.get_attribute("href") for img in images]
    #     return img_urls

    def get_image_hrefs_ocasion(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.bgImgGaleria a")
        hrefs = [element.get_attribute("href") for element in elements]
        return hrefs
    
    def get_first_by_class(self, class_name):
        try:
            resp = self.driver.find_element(By.CLASS_NAME, class_name)
            return resp.text
        except NoSuchElementException:
            return "N/A"
    
    def get_all_by_class(self, class_name):
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            return [element.text for element in elements]
        except NoSuchElementException:
            return ["N/A"]
        
    def get_by_id(self, id):
        try:
            return self.driver.find_element(By.ID, id)
        except NoSuchElementException:
            return "N/A"

        
    def get_href_by_partial_href(self, partial_href):
        # Find the element with href starting with 'tel:'
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//a[starts-with(@href, '{partial_href}')]"))
        )

        # Scroll the element into view using JavaScript
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        
        # Get the href attribute of the element
        href = element.get_attribute('href')
        return href

    def get_by_class2(self, class_name):
        try:
            return self.driver.find_element(By.CLASS_NAME, class_name)
        except NoSuchElementException:
            return "N/A"
    
    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def press_tab(self):
        body = self.driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.TAB)
    
    def get_html(self):
        return self.driver.page_source
    
    def close_current_tab(self):
        # Get the current window handle
        current_window_handle = self.driver.current_window_handle
        # Get all window handles
        window_handles = self.driver.window_handles
        
        # Close the current tab
        self.driver.close()
        
        # Remove the current window handle from the list
        window_handles.remove(current_window_handle)
        
        # Switch to another tab if there are any left
        if window_handles:
            self.driver.switch_to.window(window_handles[0])
        else:
            print("No more tabs left to switch to.")
    
    def switch_to_tab_by_index(self, index):
        window_handles = self.driver.window_handles
        if index < len(window_handles):
            self.driver.switch_to.window(window_handles[index])
        else:
            raise IndexError("Tab index out of range")

    def refresh_page(self):
        self.driver.refresh()

    # def scroll_to_element(self, selector, by=By.CSS_SELECTOR):
    #     element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((by, selector)))
    #     self.driver.execute_script("arguments[0].scrollIntoView(true);", element)          

    def scroll_to_element_by_text(self, text):
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def scroll_up_by_pixels(self, pixels):
        self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
    
    def scroll_down_by_pixels(self, pixels):
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def press_page_down(self):
        body = self.driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.PAGE_DOWN)
    
    def move_mouse_to_id(self, id):
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, id)))
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
    
    def fill_by_id(self, id, text):
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, id)))
        element.clear()
        for c in text:
            time.sleep(0.2)
            element.send_keys(c)
    
    def press_enter(self):
        body = self.driver.find_element(By.TAG_NAME, 'body')
        body.send_keys(Keys.ENTER)
    
    def take_screenshot(self, file_name, save_to_cloud):
        """
        Takes a screenshot and saves it to the specified file name in the current directory.
        
        Args:
            file_name (str): The name of the file where the screenshot will be saved.
        """
        # Ensure the file name ends with .png
        if not file_name.endswith('.png'):
            raise ValueError("The file name must end with .png")
        
        screenshot_dir = tmp_dir / "screenshots"
        if not screenshot_dir.exists():
            screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        screenshot_path = screenshot_dir / file_name
        print(f"Screenshot saved to {screenshot_path}")
    
    def click_on_coordinates(self, x, y):
        import mouse
        mouse.move("107", "575")
        mouse.click(button='left')