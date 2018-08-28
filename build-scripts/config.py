import Utils
import formatString as fstr

org_name = 'witseie-elen3009'
repo_name_template = \
    fstr.YEAR\
    + '-'\
    + fstr.REPO_NAME\
    + fstr.LAB_NUM \
    + fstr.repeat_for_students('-' + fstr.STUD_STUD_NUM +
                               '-' + fstr.STUD_SURNAME)
repo_name_lab = "lab"
repo_name_project = "project"
student_csv_filename = 'registeredStudents.csv'
error_teams_filename = None
error_students_filename = None
valid_teams_filename = None
team_name_template = fstr.YEAR + '-Team-' + fstr.TEAM_NUM
team_retired_name_template = 'Retired-Team %d'
team_retired_name_search_term = 'Retired'

__team_most_recent_number = 0

team_permission = 'push'
team_privacy = 'secret'
team_student_role = 'member'

student_storage_filename = 'stored_students.csv'
team_storage_filename = 'stored_teams.csv'

__is_dry_run = True


def isDryRun():
  return __is_dry_run


def formatLabRepoName(team, lab_num):
  global repo_name_template
  res = fstr.format(
      repo_name_template,
      lab_num=lab_num,
      team=team,
      students=team.get_students(),
      repo_name=repo_name_lab+'-'
  )
  return res


def formatProjectRepoName(team):
  global lab_repo_name_template
  res = fstr.format(
      repo_name_template,
      team=team,
      students=team.get_students(),
      repo_name=repo_name_project
  )
  return res


def formatRepoName(team, repo_name=None, lab_num=None, project=False):
  global repo_name_template
  # Determine what kind of repo is being made
  is_lab = lab_num is not None
  is_project = project
  is_other_repo = repo_name is not None

  # If the repo is a lab
  if is_lab and not is_project and not is_other_repo:
    return formatLabRepoName(team, lab_num)
  elif is_project and not is_lab and not is_other_repo:
    return formatProjectRepoName(team)
  elif is_other_repo and not is_lab and not is_project:
    return fstr.format(
        repo_name_template,
        team=team,
        students=team.get_students(),
        repo_name=repo_name
    )


def format_team_name(team):
  global team_name_template
  res = fstr.format(team_name_template, team=team)
  return res


def team_most_recent_number():
  global __team_most_recent_number
  return __team_most_recent_number


def generate_new_team_num():
  global __team_most_recent_number
  __team_most_recent_number += 1
  return __team_most_recent_number


__CONFIG_FILENAME = 'cab.conf'


def open_config_file():
  global __CONFIG_FILENAME, __team_most_recent_number, project_repo_name_template, lab_repo_name_template
  try:
    __configFile = open(Utils.formatFilePath(__CONFIG_FILENAME), 'r')
    __lab_repo_name_template = __configFile.readline()
    __project_repo_name_template = __configFile.readline()
    __team_most_recent_number = int(__configFile.readline())
    if __lab_repo_name_template:
      lab_repo_name_template = __lab_repo_name_template
    if __project_repo_name_template:
      project_repo_name_template = __project_repo_name_template
  except:
    save_config_file()


def save_config_file():
  global __CONFIG_FILENAME, project_repo_name_template, lab_repo_name_template, __team_most_recent_number
  __configFile = open(Utils.formatFilePath(__CONFIG_FILENAME), 'w')
  __configFile.write(lab_repo_name_template)
  __configFile.write(project_repo_name_template)
  __configFile.write(str(__team_most_recent_number))


open_config_file()
