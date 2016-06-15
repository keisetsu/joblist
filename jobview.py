import json
import os.path
import pprint

from jinja2 import Environment, FileSystemLoader

home = os.path.dirname(os.path.realpath(__file__))
template_env = Environment(loader=FileSystemLoader(os.path.join(home, 'templates')))

output_name = 'jobview.html'

class JobView():
    _seen = None
    seen_file = 'seen.json'

    def transform(self, items, by_date=True, by_location=False, include_seen=False):
        return_value = {}
        for item in items:
            item_id = item['id']
            item['seen'] = item_id in self.seen
            if item['seen']:
#                print('Seen', item_id, item['title'])
                if not include_seen:
                    continue
            date_key = item['date'].date()
            if not return_value.get(date_key):
                return_value[date_key] = []
            return_value[date_key].append(item)
        return return_value

    def render(self, data, mark_seen=False):
        template = template_env.get_template('jobview.html')

        with open(output_name, 'w') as output_file:
            output_file.write(template.render({'jobs': data}))

        if mark_seen:
            for category in data:
                for item in data[category]:
                    self.mark_seen(item['id'])
            self.save_seen()

    @property
    def seen(self):
        if self._seen is None:
            self._seen = self._get_seen()
        return self._seen

    def mark_seen(self, seen_id):
        self._seen.add(seen_id)

    def _get_seen(self):
        seen = set()
        try:
            with open(self.seen_file, 'r') as seen_file:
                seen = set(json.load(seen_file))
        except FileNotFoundError:
            pass
        return seen

    def save_seen(self):
        with open(self.seen_file, 'w') as seen_file:
            json.dump(list(self._seen), seen_file)


# if __name__ == '__main__':
