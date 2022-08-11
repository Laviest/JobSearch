from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import re

#######################################################################################################################
# Can't get all jobs because google link or soup scraping is broken, the find_all for the jobs doesn't work.
# Even though the way I have done it is not practical, it still shows how this can be used in the real world
# with a correctly built/scraped website.
#######################################################################################################################

print("What job are you looking for?")
job = input(">").lower()
stopwords = list(STOP_WORDS)
nlp = spacy.load(
    r'C:\Users\Pero\AppData\Local\Programs\Python\Python38\Lib\site-packages\en_core_web_sm\en_core_web_sm-3.4.0'
)

options = ChromeOptions()
options.add_argument("headless")
PATH = r"C:/Users/Pero/Downloads/chromedriver_win32/chromedriver.exe"
driver = Chrome(executable_path=PATH, options=options)

driver.get(f"https://www.indeed.com/jobs?q={job}")
html = driver.page_source
soup = BeautifulSoup(html, "lxml")

# all_jobs = soup.find_all("div", class_="mosaic mosaic-provider-jobcards mosaic-provider-hydrated")
# print(len(all_jobs))

index = 0
titles = []
company_names = []
locations = []
links = []
salary = []

job_title = soup.find_all("div", class_="css-1xpvg2o e37uo190")
for title in job_title:
    titles.append(title.h2.text)

company_name = soup.find_all("span", {"class": "companyName"})
for name in company_name:
    company_names.append(name.text)

company_location = soup.find_all("div", class_="companyLocation")
for location in company_location:
    locations.append(location.text)

is_new = soup.find("div", class_="new css-ud6i3y eu4oa1w0").text

indeed_link = "https://www.indeed.com"
job_link = soup.find_all("div", class_="css-1xpvg2o e37uo190")
for link in job_link:
    links.append(indeed_link + link.h2.a['href'])

job_salary = soup.find_all("div", {"class": "metadata estimated-salary-container"})
for sal in job_salary:
    salary.append(sal.text)

index = 0
for index in range(len(company_names)):
    print(f"{titles[index]} at {company_names[index]} located at {locations[index]}. Salary is {salary[index]}")
    print(f"{links[index]}")

    print("Would you like me to summarize the extra information for you?")
    more = input(">")
    if more.strip().lower() == "yes":
        driver.get(f"{links[index]}")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        job_desc = soup.find("div", class_="jobsearch-jobDescriptionText").text
        doc = nlp(job_desc)
        tokens = [token.text for token in doc]
        punctuation += '\n'
        punctuation += '\n\n\n'

        word_frequencies = {}
        for word in doc:
            if word.text.lower() not in stopwords:
                if word.text.lower() not in punctuation:
                    search = re.search('[a-zA-Z]', word.text.lower())
                    if search is not None:
                        if word.text not in word_frequencies.keys():
                            word_frequencies[word.text] = 1
                        else:
                            word_frequencies[word.text] += 1

        max_frequency = max(word_frequencies.values())

        for word in word_frequencies.keys():
            word_frequencies[word] = word_frequencies[word]/max_frequency

        sentence_tokens = [sent for sent in doc.sents]
        for sent in sentence_tokens:
            str(sent).strip()

        sentences_scores = {}
        for sent in sentence_tokens:
            for word in sent:
                search = re.search('[a-zA-Z]', word.text.lower())
                if word.text.lower() in word_frequencies.keys() and search is not None:
                    if sent not in sentences_scores.keys():
                        sentences_scores[sent] = word_frequencies[word.text.lower()]
                    else:
                        sentences_scores[sent] += word_frequencies[word.text.lower()]

        select_length = int(len(sentence_tokens) * 0.3)

        summary = nlargest(select_length, sentences_scores, key = sentences_scores.get)

        print(summary)
        print("")
        print("***********************************************")
        print("***********************************************")
        print("")
