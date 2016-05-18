#!/usr/bin/env python
import dateutil.parser
import dateutil.tz
import feedparser

from datetime import datetime, timedelta

from joblist import JobList
class IndeedJobList(JobList):
    base_url = ('http://rss.indeed.com/rss?q={keywords}&l={location}'
                '&sort=date&start={offset}')
    page_size = 20

    def collect_results(self, keywords, location, radius, max_results=1000, oldest=None):
        if oldest is None:
            oldest = timedelta(weeks=52)
        oldest_cutoff = datetime.now(tz=dateutil.tz.tzlocal()) - oldest
        pages = 0
        found = 0
        cutoff = False
        previous = ()
        while found < max_results:
            offset = pages * self.page_size
            print(offset)
            feed = feedparser.parse(
                'http://rss.indeed.com/rss?q={keywords}&l={location}'
                '&sort=date&start={offset}'.format(keywords=keywords,
                                                   location=location,
                                                   radius=radius,
                                                   offset=offset)
            )
            new = []
            for entry in feed['entries']:
                if entry['id'] in previous:
                    continue
                new.append(entry['id'])
                entry_date = dateutil.parser.parse(entry['published'])
                if oldest_cutoff > entry_date:
                    return None
                found += 1
                entry_location = 'Unspecified'
                try:
                    entry_location = entry['title'].split(' - ')[-1]
                except IndexError:
                    pass
                yield {
                    'date': entry_date,
                    'id': 'indeed$' + entry['id'],
                    'link': entry['link'],
                    'location': entry_location,
                    'source': entry['source']['title'],
                    'title': entry['title'],
                }
            if not new:
                # The assumption is that if none of the entries are new,
                # indeed is just repeating and the current group
                # of jobs is ended
                return None
            previous = tuple(new)
            pages += 1
