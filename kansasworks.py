import datetime
import re

import dateutil.parser
import dateutil.tz
import requests

from bs4 import BeautifulSoup

from joblist import JobList

class WorksJobList(JobList):
    ''' A scraper for the KansasWorks job list site
    Uses beautifulsoup to scrape the KansasWorks site for jobs

    '''

    page_size = 250
    base_url = ('https://www.kansasworks.com/ada/r/search/jobs?'
                'date_posted=1+week&per_page={page_size}&keywords={keywords}'
                '&location={location}&radius={radius}'
    )
    def collect_results(self, keywords, location, radius, max_results=5000, oldest=None):
        requests_complete = 0
        found = 0
        initial_request = self.base_url.format(
                keywords=keywords, location=location, page_size=self.page_size,
                radius=radius)
        request_template = initial_request + '&is_subsequent_search=true&page={offset}'
        initial_result = requests.get(initial_request)
        soup = BeautifulSoup(initial_result.content, 'html.parser')
        result_count_text = soup.find(class_='result_count').text
        result_count_match = re.search(r'.*of (.*) matches.*', result_count_text)
        result_count = int(result_count_match.group(1).replace(',', ''))
        if result_count < max_results:
            max_results = result_count
        while found < max_results:
            print('Found:', found, 'result_count: ', result_count)
            if requests_complete > 0:
                request = requests.get(request_template.format(offset=requests_complete))
                content = request.content
                soup = BeautifulSoup(content, 'html.parser')
            search_results = soup.find('dl', 'search_results')
            entries = search_results.find_all('dt')
            results = []
            for entry in entries:
                found += 1
                link = entry.a
                job_id = link.get('href')
                description = entry.find_next_sibling('dd')
                title = link.get_text()
                updated_text = entry.find(class_='updated').get_text()
                updated = updated_text.split(': ')[1]
                updated_date = dateutil.parser.parse(updated,
                                                     default=datetime.datetime(
                                                         2016, 1, 1, 0, 0, 0,
                                                         tzinfo=dateutil.tz.tzlocal()))
                employer_label = description.find('div', 'col_1').b
                source = 'None given'
                try:
                    source = employer_label.next_sibling.strip()
                except AttributeError:
                    pass
                    #    employer = employer_text.split('</b>')[1].strip()
                location = description.i.get_text().lower()
                description_text = description.find(class_='description').get_text()

                yield {
                    'date': updated_date,
                    'id': 'kansasworks$' + job_id,
                    'link': 'https://www.kansasworks.com/' + str(job_id),
                    'location': location,
                    'source': source,
                    'title': title
                }
            requests_complete += 1
