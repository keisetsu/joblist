import pprint

from datetime import timedelta

from indeed import IndeedJobList
from kansasworks import WorksJobList
from jobview import JobView

result = []
one_week_ago = timedelta(days=7)
one_day_ago = timedelta(days=1)
indeed = IndeedJobList()
result.extend(indeed.collect_results('', '66046', '25', oldest=one_week_ago))
works = WorksJobList()
result.extend(works.collect_results('', '66046', '35'))
result.extend(indeed.collect_results('python', '', '', oldest=one_week_ago))
result.extend(indeed.collect_results('', '80020', '25', oldest=one_week_ago))
view = JobView()
with_seen = view.transform(result, include_seen=False)
view.render(with_seen, mark_seen=True)
