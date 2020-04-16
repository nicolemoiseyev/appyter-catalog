#%%
import os
import sys
import json
import traceback
import jsonschema
from subprocess import Popen, PIPE

def get_changed_templates():
  try:
    # try to load files from stdin
    return {
      file.split('/', maxsplit=3)[1]
      for element in json.load(sys.stdin)
      for file in [element['filename']]
      if file.startswith('templates/')
    }
  except:
    # otherwise use git
    p = Popen(['git', 'diff', '--name-only', 'origin/master'], stdout=PIPE)
    files = {
      # templates/{template}/* => {template}
      line.split('/', maxsplit=3)[1]
      for line in map(
        bytes.decode,
        # returns all paths that will be changed
        p.stdout
      )
      if line.startswith('templates/')
    }
    assert p.returncode == 0, '`git diff` command failed'
    return files

def validate_template(template):
  print(f"{template}: Checking for existing of files...")
  assert os.path.isfile(os.path.join('templates', template, 'README.md')), f"Missing templates/{template}/README.md"
  assert os.path.isfile(os.path.join('templates', template, 'template.json')), f"Missing templates/{template}/template.json"
  #
  print(f"{template}: Validating `{template}/template.json`...")
  config = json.load(open(os.path.join('templates', template, 'template.json'), 'r'))
  validator = jsonschema.Draft7Validator({
    '$ref': f"file:///{os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'schema', 'template-validator.json'))}",
  })
  errors = [error.message for error in validator.iter_errors(config)]
  assert errors == [], '\n'.join(errors)
  #
  nbfile = config['template']['file']
  #
  print(f"{template}: Preparing system to run `{nbfile}`...")
  assert os.path.isfile(os.path.join('templates', template, nbfile)), f"Missing templates/{template}/{nbfile}"
  #
  if os.path.isfile(os.path.join('templates', template, 'deps.txt')):
    print(f"{template}: Installing system dependencies from `deps.txt`...")
    exit_code = Popen([
      'sudo', 'apt-get', 'install',
      *filter(None, [
        line.split('#', maxsplit=1)[0].strip()
        for line in open(os.path.join('templates', template, 'deps.txt'))
      ])
    ]).wait()
    assert exit_code == 0, f"`xargs | sudo apt-get install < deps.txt` failed with code {exit_code}"
  else:
    print(f"{template}: [WARN] templates/{template}/deps.txt not found, assuming no system dependencies required.")
  #
  if os.path.isfile(os.path.join('templates', template, 'requirements.txt')):
    print(f"{template}: Installing system dependencies from `requirements.txt`...")
    exit_code = Popen([
      'pip', 'install', '-r', f"templates/{template}/requirements.txt"
    ]).wait()
    assert exit_code == 0, f"`pip install -r templates/{template}/requirements.txt` failed with code {exit_code}"
  else:
    print(f"{template}: [WARN] templates/{template}/requirements.txt not found, assuming no python dependencies required.")
  #
  print(f"{template}: [WARN] Checking {nbfile} not yet implemented")

if __name__ == '__main__':
  valid = True
  for template in get_changed_templates():
    try:
      validate_template(template)
    except Exception:
      traceback.print_exc()
      valid = False
  if valid:
    sys.exit(0)
  else:
    sys.exit(1)
