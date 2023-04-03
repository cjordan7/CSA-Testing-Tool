from selenium import webdriver

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
options = Options()


def timeout(number=3):
    try:
        element_present = EC.presence_of_element_located((By.ID, 'main'))
        WebDriverWait(driver, number).until(element_present)
    except TimeoutException:
        print("")
    finally:
        print("")


# TODO: Things to get from Syzbot
#
# For each lines get
# 1. Sample crash report + informations
# 1.1 Title
# 1.2 Link
# 1.2.1 Kernel config
# 1.2.2 git tree
# 1.2.3 head commit
# 1.3 Sample crash report
# 1.3.1 Grep BUG lines + type of bug -> will need to parse it to get the bug type for CSA
# 1.3.2 Potential file/function/line

# 1.4 Reported by
# 1.5. Fix commit + link
# 1.6 Patched on
#
#
# 2. Get the Patch informations
# 2.1  Title, sample crash report, commit, date

# Get either bissected commit or patch "commit -1"

def timeout(number=3):
    try:
        element_present = EC.presence_of_element_located((By.ID, 'main'))
        WebDriverWait(driver, number).until(element_present)
    except TimeoutException:
        print("")
    finally:
        print("")

# TODO: Get path according to current dir
# TODO: curl chromdriver
driver = webdriver.Chrome(executable_path="/Users/cosmejordan/Desktop/MasterProject/CSA-Testing-Tool/parseSyzbot/chromedriver")

driver.get("https://syzkaller.appspot.com/upstream/fixed")


tableData = driver.find_elements(By.XPATH, "//table[@class='list_table']/tbody/tr")

print(len(tableData))

# TODO: Remove
rows = 0
for row in tableData:
    # TODO: Remove
    rows += 1

    columns = row.find_elements(By.XPATH, "./td")
    tableRow = []
    for column in columns:
        tableRow.append(column)

    columnSize = len(tableRow)

    # Text first column
    title = tableRow[0].text
    print(tableRow[0].find_element_by_tag_name("a").text)
    print(title)

    # Link firt column
    print(tableRow[0].find_element_by_tag_name("a").get_attribute("href"))
    temp = tableRow[0].find_element_by_tag_name("a").get_attribute("href")
    driver.execute_script('''window.open("'''+temp+'''","_blank");''')
    driver.switch_to_window(driver.window_handles[1])
    timeout(2)
    for e in driver.find_elements(By.XPATH, "html/body"):
        text = e.text
        lines = text.splitlines()
        index = lines.index(title)
        print(text.splitlines())
        print(index)


    driver.close()





    driver.switch_to_window(driver.window_handles[0])
    # Text last column
    print(tableRow[-1].text)

    try:
        # Link last column
        temp = tableRow[-1].find_element_by_tag_name("a")
        print(temp.get_attribute("href"))
    except NoSuchElementException:
        print("Warning: Ignoring because there are no links for the fix")

    # TODO: Remove
    if(rows == 1):
        break
