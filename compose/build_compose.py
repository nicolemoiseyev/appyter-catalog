import re
import os
import json
import glob

def slugify(s):
  return re.sub(r'[^a-zA-Z0-9_-]+', '-', s).strip('-').lower()

version = '0.0.1'
root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
template_path = os.path.join(root_dir, 'templates')
templates = [
  dict(
    path=os.path.dirname(path),
    **json.load(open(path, 'r')),
  )
  for path in glob.glob(os.path.join(template_path, '*', 'template.json'))
]

proxy_environment = '\n'.join(f"""
      - nginx_proxy_{n:03}="/{template['name']}(/.*) http://{template['name']}:80$$1"
""".strip('\n') for n, template in enumerate(templates)).strip('\n')

proxy_service = f"""
  proxy:
    image: maayanlab/proxy:1.1.7
    environment:
{proxy_environment}
      - nginx_proxy_{len(templates):03}="(/.*) http://app:80$$1"
    ports:
      - 80:80
""".strip('\n')

docker_compose_services = '\n'.join(f"""
  {slugify(template['title'])}:
    build: {os.path.relpath(template['path'], root_dir)}
    image: maayanlab/jtc-{slugify(template['title'])}:{template['version']}
""".strip('\n') for template in templates)

docker_compose = f"""
version: '3'
services:
{proxy_service}
  app:
    build: app
    image: maayanlab/jupyter-template-catalog:{version}
{docker_compose_services}
""".strip('\n')

print(docker_compose)
