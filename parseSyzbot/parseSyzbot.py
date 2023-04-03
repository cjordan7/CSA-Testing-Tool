import pickle

from selenium import webdriver

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
options = Options()


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

parsedDict = dict()

# TODO: Remove
rows = 0
for row in tableData:
    rowDict = dict()
    # TODO: Remove
    rows += 1

    columns = row.find_elements(By.XPATH, "./td")
    tableRow = []
    for column in columns:
        tableRow.append(column)

    columnSize = len(tableRow)

    # Text first column

    title = tableRow[0].find_element_by_tag_name("a").text

    if(title in parsedDict):
        print("Problem")
        print(title)
        raise NotImplementedError

    rowDict["title"] = title

    titleLink = tableRow[0].find_element_by_tag_name("a").get_attribute("href")
    rowDict["titleLink"] = titleLink

    print(title)

    spans = tableRow[0].find_elements_by_tag_name("span")

    subsystems = []
    for e in spans:
        subsystems.append((e.find_element_by_tag_name("a").get_attribute("href"),
                           e.find_element_by_tag_name("a").text))

    rowDict["subsystems"] = subsystems

    # Link firt column
    temp = tableRow[0].find_element_by_tag_name("a").get_attribute("href")
    driver.execute_script('''window.open("'''+temp+'''","_blank");''')
    driver.switch_to_window(driver.window_handles[1])
    timeout(2)

    lines = ""
    for e in driver.find_elements(By.XPATH, "html/body"):
        text = e.text
        lines = text.splitlines()
        index = lines.index(title)
        lines = lines[index:]
        indexStatus = list("Status" in x for x in lines).index(True)
        print(lines[indexStatus])

    rowDict["reportLines"] = lines

    driver.close()

    driver.switch_to_window(driver.window_handles[0])
    # Text last column
    print(tableRow[-1].text)

    temp2 = ""
    canOpen = True
    try:
        # Link last column
        temp2 = tableRow[-1].find_element_by_tag_name("a")
        openLink = temp2.get_attribute("href")
    except Exception as e:
        print(e)
        canOpen = False
        print("Warning: Ignoring because there are no links for the fix")

    patch = dict()
    if(canOpen):
        driver.execute_script('''window.open("'''+openLink+'''","_blank");''')
        timeout(2)
        driver.switch_to_window(driver.window_handles[-1])
        tableData2 = driver.find_elements(By.XPATH, "//table[@class='commit-info']/tbody/tr")
        for row2 in tableData2:
            tableRow2 = []
            columns2 = row2.find_elements(By.XPATH, "./*['th' or 'td']")
            temp = []
            for col in columns2:
                temp.append(col)

            print(temp[0].text)
            elements = []
            paragraphs = temp[1].find_elements_by_tag_name("a")
            print(paragraphs)

            for t in paragraphs:
                print(t.get_attribute("href"))
                print(t.text)
                elements.append((t.text, t.get_attribute("href")))

            if(len(paragraphs) == 0):
                elements.append(temp[1].text)

            patch[temp[0].text] = elements

    rowDict["patch"] = patch
    parsedDict[title] = rowDict

    # TODO: Remove
    #if(rows == 1):
    #    break

with open('data/syzbotData.pickle', 'wb') as handle:
    pickle.dump(parsedDict, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('data/syzbotData.pickle', 'rb') as handle:
    b = pickle.load(handle)
print(b)
