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
    '''Joblist class for Indeed
    This joblist is for the indeed.com rss feed. Indeed has an API,
    but it requires registration and is more suited to companies repackaging
    their data. The RSS feed works just fine for the kind of search I'm
    interested in.
    '''

    base_url = ('http://www.indeed.{domain}/rss?q={keywords}&l={location}'
                '&sort=date&start={offset}')
    page_size = 20

    def collect_results(self, keywords, location, radius, filter_location=(),
                        filter_title=(), country='us',
                        max_results=1000, oldest=None):
        '''Collect results for indeed.com (.ca, etc)
        The feeds site is "indeed.com/rss?" plus these parameters:

        * q: a set of keywords, combined with "+"
        * l: the location (a zip code, "city, state", "remote", or just a state)
        * sort: "date" or "relevance", I guess
        * offset: The rss returns up to 20 results, you can page through them
        using this parameter

        :param keywords: str A space-separated list of keywords, arguments to
        the "q" operator

        :param location: str a zip code, "city, state" combination, "remote",
        or state code. Argument to "l"

        :param radius: int radius around a location. Argument to "r". May use 0
        to limit to the location exactly.

        :param filter_location: str an iterable of locations to be removed
        from results. Any location that contains any of the strings
        will be ignored.

        :param filter_title: str an iterable of strings to filter titles. A
        title will be ignored if it contains any of the strings.

        :param country: str A two-letter country code. Defaults to "us", which
        will try indeed.com; will try any other code if provided, but there
        is no guarantee other codes will be handled well.

        :param max_results: int A maximum number of results. The
        results may be less than this, but the function will stop
        querying if this number is reached.

        :param oldest: timedelta Anything older than today - oldest
        will be ignored.

        :returns: A generator which when called will yield a dict of
        the following format:
         {
          'date': The reported date of the entry,
          'id': 'indeed$' + indeed's id for the job entry,
          'link': a link to indeed's page about the entry,
          'location': the entry's reported location,
          'source': the reported author of the post,
          'title': the reported title
         }

        '''
        domain = 'com'
        if country is not 'us':
            domain = country
        if oldest is None:
            oldest = timedelta(weeks=52)
        oldest_cutoff = datetime.now(tz=dateutil.tz.tzlocal()) - oldest
        pages = 0
        found = 0
        cutoff = False
        previous = ()
        while found < max_results:
            # Get a page of feed results (sorted by date), and process
            # it until either a date older than *oldest_cutoff*
            # appears or all the entries have been processed
            offset = pages * self.page_size
            feed = feedparser.parse(
                self.base_url.format(domain=domain,
                                     keywords=keywords,
                                     location=location,
                                     radius=radius,
                                     offset=offset)
            )
            new = []
            for entry in feed['entries']:
                # We've seen this before, skip it.
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
                        if re.search(location_filter, entry_location,
                                     re.IGNORECASE):
                            raise FilterException
                    for title_filter in filter_title:
                        if re.search(title_filter, entry_title,
                                     re.IGNORECASE):
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
