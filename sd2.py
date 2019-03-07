#!/usr/bin/env python
import csv
import os
import sys
import github
from time import sleep
from github import Github
from github import GithubException
from github import UnknownObjectException
from AUTH import GITHUB_AUTH_TOKEN
import config as Config
import terminal as term
from classroom import Student, Team
import githubInstance as gi
from itertools import combinations

import Args
from Args import ModifyTeamAction as ArgsModTeamAction
import Utils
import Store
from typing import List


def add_teams(args):
  term.heading('Adding new teams from new students file')
  term.status('Loading file...')
  teams = Store.load_students_from_google_form_file(
      Config.student_csv_filename,ignore_first_n_col=2)
  term.loading(msg='Processing teams', current=0, max=3, length=20)
  teams, conflicting_teams, conflicting_students, need_to_register_teams, need_to_register_students, already_existing_teams, already_existing_students = Store.identify_conflicting_teams(
      teams, compare_to_existing=True)
  term.endloading('Finished processing teams')

  # Display teams and their states
  term.status('Loaded file')
  if conflicting_teams:
    term.warningHeading('Teams that conflict')
    term.listTeams(conflicting_teams)
    term.warningHeading('Students that had some conflict')
    _stud_conflict = conflicting_students
    _reason_conflict = ['conflicted_with_another_team'] * len(_stud_conflict)
    term.listStudents(_stud_conflict, reasons=_reason_conflict)
  if need_to_register_teams:
    term.warningHeading('Teams that have invalid Github usernames')
    term.listTeams(need_to_register_teams)
    term.warningHeading('Students that have invalid Github usernames')
    _stud_register, _reason_register = zip(*need_to_register_students)
    _stud_register = list(_stud_register)
    _reason_register = list(_reason_register)
    term.listStudents(_stud_register, reasons=_reason_register)
  if already_existing_teams:
    term.warningHeading('Teams that have already been added')
    term.listTeams(already_existing_teams)
    term.warningHeading('Students that have already been added')
    _stud_already_exist, _reason_already_exist = zip(
        *already_existing_students)
    _stud_already_exist = list(_stud_already_exist)
    _reason_already_exist = list(_reason_already_exist)
    term.listStudents(_stud_already_exist, reasons=_reason_already_exist)

  if len(teams) > 0:
    term.heading('The following teams can be added')
    term.listTeams(teams)
  else:
    term.warning('There are no available teams to add, exiting')
    exit()

  # Write to file if requested
  if Config.error_teams_filename and not Utils.fileExists(Config.error_teams_filename):
    term.status('Writing teams with errors to file')
    # Save teams and students
    Store.save_team_storage(
        teams=conflicting_teams,

        teamFilename=Utils.formatFilePath(Config.error_teams_filename),
        generate_team_numbers=True
    )
  if Config.error_students_filename and not Utils.fileExists(Config.error_students_filename):
    error_students = list()
    error_students_reasons = list()
    if conflicting_teams:
      error_students += _stud_conflict
      error_students_reasons += _reason_conflict
    if need_to_register_teams:
      error_students += _stud_register
      error_students_reasons += _reason_register
    if already_existing_teams:
      error_students += _stud_already_exist
      error_students_reasons += _reason_already_exist
    if error_students:
      Store.save_students_file(
          error_students,
          Config.error_students_filename,
          reasons=error_students_reasons
      )

  if not term.confirm('Would you like to add the above teams to the db? [y/n] (default=y) > '):
    term.status('Exiting')
    exit()

  term.loading_indeterminate('Adding teams to Github')
  Store.add_teams(teams)
  term.endloading('Added teams to Github')


def list_students(args, githubSync, sort, retired=False):
  students = Store.get_students(include_retired=retired, exclude_valid=retired)
  term.heading('Listing students')
  if sort:
    students.sort(key=lambda x: x.get_student_number())
  term.listStudents(students)


def list_teams(args, sort, listMembership, team_numbers=None, retired=False):
  teams = Store.get_teams(include_retired=retired, exclude_valid=retired)
  # If team numbers is defined, only show the teams chosen
  if team_numbers is not None:
    print(team_numbers)
    selected_teams = []
    for team in teams:
      if team.get_team_num() in team_numbers:
        selected_teams.append(team)
    teams = selected_teams
  term.heading('Listing teams')
  if sort:
    teams.sort(key=lambda x: x.get_team_num())
  if teams:
    term.listTeams(teams, list_membership=listMembership)
  else:
    term.error('No teams were returned for that query')


def sync_db_teams(args, dry_run, team_nums, team_num_negate, check_membership):
  if dry_run:
    term.warning('Running in dry-run mode')

  # Get the teams to add to Github from Store
  if team_nums is not None:
    _team_nums = set(team_nums)
  else:
    _team_nums = None
  if _team_nums is not None and team_num_negate is not None:
    _team_nums -= set(team_num_negate)

  term.heading('Comparing local teams to Github teams')
  teams_to_add, teams_to_add_names = Store.teams_to_add_to_github(
      team_nums=_team_nums)
  term.endloading('Compare completed')

  # List teams if any exist, quit otherwise
  if teams_to_add:
    term.heading('The following teams must be created on Github')
    term.listTeams(teams_to_add, list_membership=False)
    if not term.confirm('Would you like to add the above teams to Github? [y/n] (default=y) > '):
      term.status('Exiting')
      if not check_membership:
        exit()
  else:
    term.warning('No teams must be created on Github')
    if not check_membership:
      exit()
  if teams_to_add:
    term.heading('Creating teams on Github')
    failed_teams, num_teams_created = Store.create_teams_on_github(
        teams_to_add_names, dry_run=dry_run)
    if len(failed_teams) == 0:
      term.endloading('All teams were created')
    else:
      term.endloading(
          term.Fore.RED +
          term.Style.BRIGHT +
          'The following teams failed to be created/have students added' +
          term.Style.RESET_ALL
      )
      term.listTeams(failed_teams, list_membership=False)
      term.status('%d/%d teams were created' %
                  (num_teams_created, len(teams_to_add)))

  if check_membership:
    term.heading('Updating team membership')
    n_members_added, n_members_removed, students_added = Store.update_team_membership(
        team_numbers=_team_nums, dry_run=dry_run)
    term.endloading('Membership updated')
    term.status('%d members added to teams, %d members removed from teams' %
                (n_members_added, n_members_removed))
    if students_added:
      term.heading('The following students were added to teams')
      term.listStudents(students_added)


def add_repo(args, lab_num, team_nums, team_num_negate=None, dry_run=False, repo_type_name=None):
  if dry_run:
    term.warning('Running in dry-run mode')

  # Find the teams
  teams = Store.get_teams(include_retired=True)
  if team_nums != None:
    lab_teams = []
    for team in teams:
      if team.get_team_num() in team_nums:
        lab_teams.append(team)
  else:
    lab_teams = teams

  # Remove retired teams
  retired_teams = list()
  for iTeam, team in enumerate(lab_teams):
    if team.get_team_num() == 39:
      pass
    if team.is_retired():
      retired_teams.append(team)
  for team in retired_teams:
    lab_teams.remove(team)

  # Remove teams with team numbers in team_num_negate
  if team_num_negate is not None:
    negated_teams = list()
    for iTeam, team in enumerate(lab_teams):
      if team.get_team_num() in team_num_negate:
        negated_teams.append(team)
    for team in negated_teams:
      lab_teams.remove(team)

  # Repo details
  if lab_num is not None and repo_type_name is not None:
    term.error('Cannot create a lab repo with repo_name')
    exit()
  is_lab = True if lab_num is not None and repo_type_name is None else False

  # List teams and confirm details
  term.heading('Teams to create repo for')
  term.listTeams(lab_teams, list_membership=False)
  term.heading('Retired teams that were in the query. Repos will not be created for them.')
  term.listTeams(retired_teams,list_membership=False)
  term.heading('Sample repo names')
  for i in range(0, min(3, len(lab_teams))):
    if is_lab:
      term.status('Repo name: %s' %
                  (Config.formatLabRepoName(lab_teams[i], lab_num=lab_num)))
    else:
      term.status('Repo name: %s' %
                  (Config.formatRepoName(lab_teams[i], repo_name=repo_type_name)))

  if not term.confirm('Would you like to create the repo for above teams? [y/n] (default=y) > '):
    term.status('Exiting')
    exit()

  # Create each team's repo
  failed_repo_teams = []
  repo_names = []
  n_teams = len(lab_teams)
  for iTeam, team in enumerate(lab_teams):
    term.loading(
        current=iTeam,
        max=n_teams,
        msg='Creating repo for team %03d' % (team.get_team_num())
    )
    repo_name = Config.formatRepoName(
        team, lab_num=lab_num, repo_name=repo_type_name)
    repo_names.append(repo_name)
    if dry_run:
      result = True
    else:
      result = Store.create_repo_for_team(team, repo_name)
    if not result:
      failed_repo_teams.append(team)

  if len(failed_repo_teams) == 0:
    term.endloading('Success, all repos created')
    term.heading('Repo names')
    term.list_enumerate(repo_names)
  else:
    term.endloading(
        term.Fore.MAGENTA +
        term.Style.BRIGHT +
        'The following teams failed to have their repos be created' +
        term.Style.RESET_ALL
    )
    term.listTeams(failed_repo_teams, list_membership=False)


def add_students_to_team(team: Team, students: List[Student], inplace=False, ignore_multiple_teams=False):
  # If not inplace, retire the old one and create a new one
  if not inplace:
    team.retire()
    Store.retire_team(team.get_team_num())
    old_students = team.get_students()
    team = Team()
    team.add_students(old_students)
  # Check if the students' usernames exist on Github
  need_to_register_students = []
  for student in students:
    if not student.exists_on_github():
      need_to_register_students.append(student)
    else:
      team.add_student(student)


def modify_team(
    args,                           # argparse arguments
    action=None,                    # Args.ModifyTeamAction action to take
    team_num=None,                  # number of team to modify
    inplace=None,                   # Whether to modify the team inplace
    new_students=None,              # new students to add to team
    ignore_multiple_teams=None,     # ignore teams where new_students already exist
    remove_student_number=None,     # student number of student to remove from team
    remove_student_username=None,   # username of student to remove from team
    new_team_num=None,              # team number to change team to
    new_team_name=None,             # new team name to change to
):
  if action is None:
    return

  # Check if the team exists
  team = Store.get_team(team_num=team_num)
  if team is None:
    term.error('Team with number %03d does not exist' % (team_num))
    exit()

  ## Add new students ##
  if action is ArgsModTeamAction.STUDENT_ADD:
    students = []
    for student in new_students:
      student_number = student[0]
      username = student[1]
      fullname = student[2]
      students.append(Student(student_number, username, fullname=fullname))
    add_students_to_team(
        team,
        students,
        inplace=inplace,
        ignore_multiple_teams=ignore_multiple_teams
    )
  ## Remove student ##
  if action is ArgsModTeamAction.STUDENT_REMOVE:
    pass


def retire_team(args, team_num):
  # Check if the team exists
  team = Store.get_team(team_num=team_num)
  if team is None:
    term.error(
        'Team with team number %d doesn\'t exist in the database' % (team_num))
    exit()
  success, reason = Store.retire_team(team)
  if success:
    term.status('Team retired successfully')
  else:
    term.error('An error occurred:')
    term.error(reason)


if __name__ == '__main__':

  Store.load_team_storage()
  Args.setupArguments(
      funcTeamsAddFromFile=add_teams,
      funcListStudents=list_students,
      funcListTeams=list_teams,
      funcSyncTeams=sync_db_teams,
      funcRepoAdd=add_repo,
      funcModifyTeam=modify_team,
      funcRetireTeam=retire_team
  )
  Args.processArguments()
  team_count, student_count, retired_team_count, retired_students_count = Store.save_team_storage(
      write_default_storage=True)
  Config.save_config_file()
  term.status('Currently there are %d retired teams holding %d students that aren\'t allocated to another team' % (
      retired_team_count, retired_students_count))
  term.status('Current team count is %d with a total of %d students' %
              (team_count, student_count))
