import csv
import Utils
from classroom import Student, Team
from typing import List
import itertools as it
import githubInstance as gi
import terminal as term
import config as Config

__students = list()
__student_numbers = set()
__student_in_retired_team_numbers = set()
__teams = list()
__team_numbers = set()
__team_retired_numbers = set()


def len_teams():
  global __team_numbers
  return len(__team_numbers)


def len_students():
  global __student_numbers
  return len(__student_numbers)

# Returns a list of teams

# not used when directly creating csv files
def load_students_from_google_form_file(filename, ignore_header=True, ignore_first_n_col=0):
  studFile = open(Utils.formatFilePath(filename), 'r')
  studReader = csv.reader(studFile)
  teams = list()
  # Ignore header line
  if ignore_header:
    next(studReader, None)
  test = True
  for row in studReader:

    rowIter = iter(row)
    for i in range(ignore_first_n_col):
      next(rowIter, None)  # Ignore first column, timestamp from Google Drive
    team = Team()
    for _id, _username, _fullname in zip(rowIter, rowIter, rowIter):
      team.add_student(Student(_id,_username,fullname=_fullname))
    teams.append(team)
  return teams


def identify_conflicting_teams(teams: List[Team], compare_to_existing=True):
  global __teams, __students

  # Identify teams that conflict
  conflicting_teams = list()
  conflicting_students = set()
  duplicate_teams = list()
  for team1, team2 in it.combinations(teams, 2):
    # If the teams are EXACTLY equal, ignore but remove
    if team1 == team2:
      duplicate_teams.append(team2)
      team1 == team2
      continue
    if team1.conflictsWith(team2):
      if team1 == team2:
        pass
      conflicting_teams.append(team1)
      conflicting_teams.append(team2)
      for student in team1.get_students() + team2.get_students():
        if student not in conflicting_students:
          conflicting_students.add(student)
  # Remove conflicting teams
  for duplicate_team in duplicate_teams:
    print('Removing duplicate team %s' % (str(duplicate_team)))
    teams.remove(duplicate_team)
  teams = [t for t in teams if t not in conflicting_teams]
  if term.isLoading():
    term.loading(msg='Checking if usernames exist',
                 current=1, max=term.loading_max())

  # Identify if any teams have students that don't exist
  need_to_register_teams = list()
  need_to_register_students = list()
  if term.isLoading():
    term.loading(msg="Checking if usernames are registered", current=0, max=len(teams))
  for i_team, team in enumerate(teams):
    needs_to_register = False
    # For each student in the team
    for student in team.get_students():
      if not student.exists_on_github():
        needs_to_register = True
        need_to_register_students.append((student, 'needs_to_register'))
    if needs_to_register:
      need_to_register_teams.append(team)
    if term.isLoading():
      term.loading(msg="Checking if usernames are registered", current=i_team, max=len(teams))
  # Remove teams needing to register users
  teams = [t for t in teams if t not in need_to_register_teams]
  if term.isLoading():
    term.loading(msg='Processing teams', current=2, max=term.loading_max())

  # Compare to internal register of students already registered
  already_existing_teams = list()
  already_existing_students = list()
  if compare_to_existing:
    for team in teams:
      team_can_be_added = True
      for student in team.get_students():
        for __student in __students:
          # Ignore this student as they're in a retired team
          if __student.get_student_number() in __student_in_retired_team_numbers:
            continue
          conflicts, conflictMsg = student.conflictsWith(__student)
          if conflicts:
            already_existing_students.append((student, conflictMsg))
            team_can_be_added = False
      if not team_can_be_added:
        already_existing_teams.append(team)
    teams = [t for t in teams if t not in already_existing_teams]
  if term.isLoading():
    term.loading(current=3, max=term.loading_max())
  return teams, conflicting_teams, list(conflicting_students), need_to_register_teams, need_to_register_students, already_existing_teams, already_existing_students


def add_teams(teams: List[Team]):
  for team in teams:
    add_team(team, give_team_number=True, give_team_name=True)


def add_team(team: Team, give_team_number=False, give_team_name=False):
  global __team_numbers
  global __team_retired_numbers
  global __teams
  global __students
  global __student_numbers
  global __student_in_retired_team_numbers
  # Check if team is valid
  if not give_team_number and not team.get_team_num():
    raise ValueError(
        'Team does not have a team number. Please call add_team with give_team_number=True.')
  if give_team_number and team.get_team_num():
    raise ValueError(
        'Assigning new number to a team is invalid. Please call add_team with give_team_number=False')
  if not give_team_number and team.get_team_num() in (__team_numbers | __team_retired_numbers):
    raise ValueError('Team number %d already exists in storage' %
                     (team.get_team_num()))
  for student in team.get_students():
    if student.get_student_number() in __student_numbers:
      raise ValueError('Student with student number %s already exists in storage' % (
          student.get_student_number()))

  if give_team_number:
    team.set_team_num(Config.generate_new_team_num())

  if give_team_name and team.get_team_num():
    team.set_team_name(Config.format_team_name(team))

  # Add team to storage
  __team_numbers.add(team.get_team_num())
  __teams.append(team)
  for student in team.get_students():
    stud_number = student.get_student_number()
    # If the student was in a previously retired team
    if stud_number in __student_in_retired_team_numbers:
      # Student is retired but exists in __students, remove
      # so the new student entry has the new information
      student = get_student(student_number=stud_number)
      __students.remove(student)
      __student_in_retired_team_numbers.remove(stud_number)
    __student_numbers.add(stud_number)
    __students.append(student)


def retire_team(team=None, team_num=None):
  global __teams
  global __team_numbers
  global __team_retired_numbers
  global __student_numbers
  global __student_in_retired_team_numbers
  if (team is not None and team_num is not None) or (team is None and team_num is None):
    raise ValueError(
        'Either team or team_num must be defined, not both or neither')
  if team is not None:
    team_num = team.get_team_num()
  if team_num not in __team_numbers:
    if team_num not in __team_retired_numbers:
      return False, 'No team exists with that team number'
    else:
      return False, 'Team already retired'
  for team in __teams:
    if team.get_team_num() == team_num:
      team.retire()
      # Remove team number from sets
      __team_retired_numbers.add(team_num)
      __team_numbers.remove(team_num)
      # Remove students from sets
      for student in team.get_students():
        stud_number = student.get_student_number()
        if stud_number in __student_numbers:
          __student_numbers.remove(stud_number)
        if stud_number not in __student_in_retired_team_numbers:
          __student_in_retired_team_numbers.add(stud_number)
      return True, None
  return False, 'Unknown error occurred'


__student_storage_headers = ['team_num',
                             'student_number', 'username', 'fullname']
__team_storage_headers = ['team_num', 'team_name', 'retired', 'github_id']

# Load the internal student storage file


def load_team_storage():
  global __teams, __team_numbers, __team_retired_numbers, __students, __student_numbers, __student_in_retired_team_numbers
  # Try to open the storage files
  try:
    studFile = open(Utils.formatFilePath(Config.student_storage_filename), 'r')
    teamFile = open(Utils.formatFilePath(Config.team_storage_filename), 'r')
  except:
    return
  # Create CSV readers
  studReader = csv.reader(studFile)
  teamReader = csv.reader(teamFile)
  # Temporary storage lists
  teams = list()
  students = list()
  student_numbers = set()
  students_in_retired_teams_numbers = set()
  team_numbers = set()
  team_retired_numbers = set()

  ################
  ## Load teams ##
  ################

  # Ignore header line
  next(teamReader, None)
  # For each entry in the team file
  for row in teamReader:
    rowIter = iter(row)
    # Get data from the CSV but throw error if something goes wrong
    try:
      team_num = int(next(rowIter, None))
      team_name = next(rowIter, None)
      team_retired = next(rowIter, None)
      team_retired = True if team_retired == 'True' else False if team_retired == 'False' else None
      team_github_id = next(rowIter, None)
    except:
      raise ValueError('Team storage file is malformed')
    # Create the team object
    team = Team(team_num=team_num, team_name=team_name)
    # If the team is meant to be retired, retired the object
    if team_retired == True:
      team.retire()

    # If the team has a github id, add it
    if team_github_id:
      team.set_github_id(team_github_id)
    # Add team details to lists
    if not team.is_retired():
      teams.append(team)
      team_numbers.add(team_num)
    else:
      teams.append(team)
      team_retired_numbers.add(team_num)

  ###################
  ## Load students ##
  ###################

  # Ignore header line
  next(studReader, None)
  # For each entry in the student file
  for row in studReader:
    rowIter = iter(row)
    # Get data from the CSV but throw error if something goes wrong
    try:
      team_num = int(next(rowIter, None))
      student_number = next(rowIter, None)
      username = next(rowIter, None)
      fullname = next(rowIter, None)
    except:
      raise ValueError('Student storage file is malformed')

    # Create temporary student
    student = Student(student_number, username, fullname=fullname)

    # If the team doesn't exist yet
    if team_num in team_numbers or team_num in team_retired_numbers:
      # Find team in current storage
      team = [t for t in teams if t.get_team_num() == team_num][0]
    else:
      # Create the new team object
      team = Team(
          team_num=team_num
      )
      team.set_team_name(Config.format_team_name(team))
      team_numbers.add(team_num)
      teams.append(team)

    # Check if the student number already exists AND the team isn't retired
    if student_number in student_numbers:
      raise ValueError(
          'Student number %s exists more than once in storage' % (student_number))

    # Add student to team and internal student list
    team.add_student(student)
    students.append(student)
    if not team.is_retired():
      student_numbers.add(student.get_student_number())
    else:
      students_in_retired_teams_numbers.add(student.get_student_number())

  # Double check the maximum team number matches the Config
  if len(__team_numbers) > 0 and max(__team_numbers) != Config.team_most_recent_number():
    raise ValueError(
        'Maximum team number from storage doesn\'t match the config file')

  # Set the internal module teams list
  __teams = teams
  __team_numbers = team_numbers
  __team_retired_numbers = team_retired_numbers
  __students = students
  __student_numbers = student_numbers
  __students_in_retired_teams_numbers = students_in_retired_teams_numbers


def save_students_file(
    students,
    studentFilename,
    reasons=None
):
  studFile = open(Utils.formatFilePath(studentFilename), 'w', newline='')
  studWriter = csv.writer(studFile)
  studentHeaders = ['student_number', 'username', 'fullname']
  if reasons is not None:
    studentHeaders += ['reasons']
  studWriter.writerow(studentHeaders)

  # Write students
  for iStudent, student in enumerate(students):
    studRow = [
        student.get_student_number(),
        student.get_username(),
        student.get_fullname()
    ]
    if reasons is not None:
      studRow += [reasons[iStudent]]
    studWriter.writerow(studRow)


def save_team_storage(
    teams=None,
    studentFilename=None,
    teamFilename=None,
    write_default_storage=False,
    extra_student_arg_header=None,
    extra_student_args=None,
    extra_team_arg_header=None,
    extra_team_args=None,
    generate_team_numbers=False,
    generate_team_names=False
):
  global __teams, __team_storage_headers

  # Handle arguments
  if teams == None:
    _teams = __teams
  else:
    _teams = teams

  _teams.sort(key=lambda x: (x.is_retired(), x.get_team_num()))

  # Override filenames if writing to default storage
  if write_default_storage and not studentFilename:
    studentFilename = Config.student_storage_filename
  if write_default_storage and not teamFilename:
    teamFilename = Config.team_storage_filename

  # Check if must save to student and team files respectively
  w_students = studentFilename != None
  w_teams = teamFilename != None

  # Open files if necessary
  # Write headers and add extra_arg_headers if neccesary
  # If must write students #
  if w_students:
    studFile = open(Utils.formatFilePath(studentFilename), 'w', newline='')
    studWriter = csv.writer(studFile)
    studentHeaders = __student_storage_headers
    if extra_student_arg_header != None:
      studentHeaders += extra_student_arg_header
    studWriter.writerow(studentHeaders)
    student_numbers_written = set()
  # If must write teams #
  if w_teams:
    teamFile = open(Utils.formatFilePath(teamFilename), 'w', newline='')
    teamWriter = csv.writer(teamFile)
    teamHeaders = __team_storage_headers
    if extra_team_arg_header != None:
      teamHeaders += extra_team_arg_header
    teamWriter.writerow(teamHeaders)

  # Count the number of students written IF writing students is enabled
  _student_count = 0 if w_students else None
  # Count the number of students not written because they changed teams IF
  # writing students is enabled
  _retired_student_count = 0 if w_students else None
  # Count the number of teams written IF writing teams is enabled
  __team_count = 0 if w_teams else None
  # Count the number of retired teams written IF writing teams is enabled
  _retired_team_count = 0 if w_teams else None
  # Iterate through each team
  for iTeam, team in enumerate(_teams):
    # Get the team number (generated if set in arguments)
    team_num = iTeam if generate_team_numbers else team.get_team_num()

    # Write teams if enabled #
    if w_teams:
      # Write team details
      teamRow = [
          team_num,
          Config.format_team_name(
              team) if generate_team_names else team.get_team_name(),
          team.is_retired(),
          team.get_github_id()
      ]
      if extra_team_args != None:
        teamRow += extra_team_args[iTeam]
      teamWriter.writerow(teamRow)
      if team.is_retired():
        _retired_team_count += 1
      else:
        __team_count += 1

    # Write students if enabled #
    if w_students:
      # Iterate through all students in given team
      for iStudent, student in enumerate(team.get_students()):
        if student.get_student_number() in student_numbers_written:
          continue
        student_numbers_written.add(student.get_student_number())
        if team.is_retired():
          _retired_student_count += 1
        else:
          _student_count += 1
        # Write student details
        studentRow = [
            iTeam if generate_team_numbers else team_num,
            student.get_student_number(),
            student.get_username(),
            student.get_fullname()
        ]
        if extra_student_args != None:
          studentRow += extra_student_args[iTeam][iStudent]
        studWriter.writerow(studentRow)
  return __team_count, _student_count, _retired_team_count, _retired_student_count


def get_teams(include_retired=False, exclude_valid=False):
  global __teams, __team_numbers, __team_retired_numbers
  team_number_query = set()
  if include_retired:
    team_number_query |= __team_retired_numbers
  if not exclude_valid:
    team_number_query |= __team_numbers
  return [_t for _t in __teams if _t.get_team_num() in team_number_query]

# Returns the team that has the supplied team_num AND team_name.
# If either is None, it is ignored.


def get_team(team_num=None, team_name=None):
  global __teams, __team_numbers, __team_retired_numbers
  # Return None if neither team_name or team_num is supplied
  if team_num is None and team_name is None:
    return None

  if (
      team_num is not None and
      team_num not in __team_numbers and
      team_num not in __team_retired_numbers
  ):
    return None

  # Search the team list for the team that satisfies the conditions
  for team in __teams:
    if team_num and team.get_team_num() != team_num:
      continue
    if team_name and team.get_team_name() != team_name:
      continue
    return team
  return None


# Returns student from query and whether student is in a retired team
def get_student(student_number=None):
  global __students
  global __student_numbers
  global __student_in_retired_team_numbers

  # If querying on student number
  if student_number is not None:
    if (
        student_number in __student_numbers or
        student_number in __student_in_retired_team_numbers
    ):
      for student in __students:
        if student.get_student_number() == student_number:
          return student, student_number in __student_numbers

  return None, None


def get_students(include_retired=False, exclude_valid=False):
  global __students, __student_numbers, __student_in_retired_team_numbers
  student_number_query_set = set()
  if include_retired:
    student_number_query_set |= __student_in_retired_team_numbers
  if not exclude_valid:
    student_number_query_set |= __student_numbers
  return [_s for _s in __students if _s.get_student_number() in student_number_query_set]


def teams_to_add_to_github(team_nums=None):
  global __teams, __students
  # Get github objects
  org = gi.getOrganization()
  gi_teams = org.get_teams()

  # Generate set of github team names
  gi_team_names = set()
  for gi_team in gi_teams:
    gi_team_names.add(gi_team.name)

  # Filter teams  using team_nums if set
  if team_nums is not None:
    teams = [t for t in __teams if t.get_team_num() in team_nums]
  else:
    teams = __teams

  # Check if any db teams aren't on Github
  teams_to_create = []
  team_names_to_create = []
  for iTeam, team in enumerate(teams):
    term.loading(
        current=iTeam,
        max=len(teams),
        msg='Checking if team (num=%d) exists Github' % (team.get_team_num())
    )
    if not team.is_retired() and team.get_team_name() not in gi_team_names:
      teams_to_create.append(team)
      team_names_to_create.append(team.get_team_name())

  return teams_to_create, team_names_to_create


def create_teams_on_github(team_names, is_secret=True, dry_run=False):
  global __teams
  # Get github objects
  g = gi.getGithub()
  org = gi.getOrganization()

  # Iterate through each team to add
  teams_that_failed = []
  num_teams_created = 0
  nTeams_processed = 0
  for team in __teams:
    # If the team isn't meant to be processed, ignore it
    if team.get_team_name() not in team_names:
      continue
    # Attempt to add the team
    try:
      privacy = 'secret' if is_secret else 'closed'
      term.loading(
          current=nTeams_processed,
          max=len(team_names),
          msg='Creating team (name %s and privacy=%s)' %
          (team.get_team_name(), privacy)
      )
      # Create team on Github
      if not dry_run:
        gi_team = org.create_team(
            team.get_team_name(),
            privacy=privacy
        )
        # Assign github ID to team
        team.set_github_id(gi_team.id)

      num_teams_created += 1
      nTeams_processed += 1
    except:
      term.error()
      teams_that_failed.append(team)
  return teams_that_failed, num_teams_created


def update_team_membership(teams=None, dry_run=False, team_numbers=None):
  if teams is None:
    teams = __teams
  # Get github objects
  g = gi.getGithub()
  org = gi.getOrganization()
  # Iterate through each team
  n_members_added = 0
  n_members_removed = 0
  n_teams = len(teams)
  students_added = []
  for iTeam, team in enumerate(teams):
    # If the team is retired, ignore membership
    if team.is_retired():
      continue
    if team_numbers is not None and team.get_team_num() not in team_numbers:
      continue
    # Get the team object
    term.loading(
        current=iTeam,
        max=n_teams,
        msg='Processing members for team %s [%d]' % (
            team.get_team_name(),
            team.get_team_num()
        )
    )
    # if dry_run and the team
    if team.get_github_id() is None:
      continue
    gi_team = org.get_team(team.get_github_id())
    # Get current membership and usernames
    gi_team_members = gi_team.get_members()
    gi_team_member_logins = set()
    # Get current member logins
    for m in gi_team_members:
      if m is not None and m.login is not None:
        gi_team_member_logins.add(str(m.login).lower())
    student_names_added = list()
    # For all students in the team
    NStudentsInTeam = len(team.get_students())
    for iStudent, student in enumerate(team.get_students()):
      # Check if the student is already in the team on Github
      if (
          str(student.get_username()).lower() in gi_team_member_logins or
          gi_team.has_in_members(g.get_user(student.get_username()))
      ):
        student_is_member = True
        gi_team_member_logins.remove(student.get_username())
        student_names_added.append(student.get_username())
      else:
        student_is_member = False
      if not student_is_member:
        term.loading(current=iStudent,max=NStudentsInTeam,msg='Add student (%s,%s)' % (
            student.get_student_number(),
            student.get_username()
        ))
      if not dry_run and not student_is_member:
        n_members_added += 1
        gi_student = g.get_user(login=student.get_username())
        students_added.append(student)
        gi_team.add_membership(gi_student, role='member')

    # Remove all members no longer assigned to team
    for username in gi_team_member_logins:
      n_members_removed += 1
      term.loading(msg='Removing student (username=%s)' % (username))
      if not dry_run:
        gi_student = g.get_user(login=username)
        gi_team.remove_membership(gi_student)

  return n_members_added, n_members_removed, students_added


def create_repo_for_team(team, repo_name, private=True):
  org = gi.getOrganization()
  try:
    gi_team = org.get_team(team.get_github_id())
  except:
    term.warning('Cannot find team %s' % (team.get_team_name()))
    return False

  try:
    repo = org.create_repo(repo_name, private=private)
  except:
    term.warning('Could not create repo %s' % (repo_name))
    return False

  # Attempt to add team to repo
  # for i in range(0,5):
  try:
    #The functionality of add_to_repos may be covered by set_repo_permission
    #gi_team.add_to_repos(repo)
    gi_team.set_repo_permission(repo, 'push')

      # # Check if the team was added to the repo
      # repo_new = org.get_repo(repo.name)
      # if len(repo_new.get_teams()) > 0:
    return True
  except:
    term.warning('Error while adding team (%s) to repo (%s)' %
                (team.get_team_name(), repo_name))
    return False
  term.warning('Could not add team (%s) to repo (%s)' %
                  (team.get_team_name(), repo_name))
  return False


def load_students_add_teams_from_file(filename):
  studFile = open(Utils.formatFilePath(filename), 'r')
  studReader = csv.reader(studFile)
  teams = list()
  team_identifiers = set()
  for row in studReader:
    rowIter = iter(row)
    team_id = next(rowIter, None)
    student_number = next(rowIter, None)
    username = next(rowIter, None)
    fullname = next(rowIter, None)
    student = Student(
        student_number,
        username,
        fullname=fullname
    )
    if team_id in team_identifiers:
      team = Team(team_id)
  return teams
