#!/usr/bin/env python
import dateutil.parser
import dateutil.tz
import feedparser
import re

from datetime import datetime, timedelta

from joblist import JobList

class FilterException(Exception):
    pass

class IndeedJobList(JobList):
    base_url = ('http://rss.indeed.com/rss?q={keywords}&l={location}'
                '&sort=date&start={offset}')
    page_size = 20

    def collect_results(self, keywords, location, radius, filter_location=(),
                        filter_title=(), max_results=1000, oldest=None):
        if oldest is None:
            oldest = timedelta(weeks=52)
        oldest_cutoff = datetime.now(tz=dateutil.tz.tzlocal()) - oldest
        pages = 0
        found = 0
        cutoff = False
        previous = ()
        while found < max_results:
            offset = pages * self.page_size
            feed = feedparser.parse(
                # 'http://rss.indeed.com/rss?q={keywords}&l={location}'
                # '&sort=date&start={offset}'
                self.base_url.format(keywords=keywords,
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
                entry_title = entry['title']
                entry_location = 'Unspecified'
                try:
                    entry_location = entry_title.split(' - ')[-1]
                except IndexError:
                    pass
                try:
                    for location_filter in filter_location:
                        if re.search(location_filter, entry_location, re.IGNORECASE):
                            # print('skipping ' + entry_location +
                            #       ' because of ' + location_filter)
                            raise FilterException
                    for title_filter in filter_title:
                        if re.search(title_filter, entry_title, re.IGNORECASE):
                            print('skipping ' + entry_title +
                                  ' because of ' + title_filter)
                            raise FilterException
                except FilterException:
                    continue
                found += 1

                yield {
                    'date': entry_date,
                    'id': 'indeed$' + entry['id'],
                    'link': entry['link'],
                    'location': entry_location,
                    'source': entry['source']['title'],
                    'title': entry_title,
                }
            if not new:
                # The assumption is that if none of the entries are new,
                # indeed is just repeating and the current group
                # of jobs is ended
                return None
            previous = tuple(new)
            pages += 1
