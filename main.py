from selenium import webdriver

driver = webdriver.Chrome()

driver.get("https://webscraper.io/test-sites/e-commerce/allinone")
driver.quit()