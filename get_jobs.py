import pprint

from datetime import timedelta

from indeed import IndeedJobList
from kansasworks import WorksJobList
from jobview import JobView

result = []
one_week_ago = timedelta(days=7)
one_day_ago = timedelta(days=1)
two_days_ago = timedelta(days=2)
indeed = IndeedJobList()
# result.extend(indeed.collect_results('python', '66046', '25', oldest=two_days_ago))
title_filter = (
    # 'senior',
    # 'lead',
)

location_filter = (
    'Atlanta, GA',
    'AZ',
    'FL',
    'Manhattan, NY',
    'New York, NY',
    'Texas',
    'TX',
    'UT',
)
result.extend(indeed.collect_results('python', 'remote', '', filter_location=location_filter,
                                     filter_title=title_filter, oldest=two_days_ago))
result.extend(indeed.collect_results('python', '', '', filter_location=location_filter,
                                     filter_title=title_filter, oldest=two_days_ago))
# result.extend(indeed.collect_results('', '80020', '25', oldest=one_week_ago))
works = WorksJobList()
result.extend(works.collect_results('python', '66046', '35'))
view = JobView()
with_seen = view.transform(result, include_seen=False)
view.render(with_seen, mark_seen=True)
