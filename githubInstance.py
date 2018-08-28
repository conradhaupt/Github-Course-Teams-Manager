from github import Github
from github.Organization import Organization
from AUTH import GITHUB_AUTH_TOKEN
import config as Config
import terminal as term

__github = None
__org = None


def connect_to_org(orgName):
  g = getGithub()
  org = g.get_organization(orgName)
  setGithubOrganisation(org)
  return org


def setGithubInstance(github):
  global __github
  if not type(github) is Github:
    raise Exception('github must be of type github.MainClass.Github')
  else:
    __github = github


def setGithubOrganisation(organization):
  global __org
  if not type(organization) is Organization:
    raise Exception(
        'organization must be of type github.Organization.Organization')
  else:
    __org = organization


def getGithub() -> Github:
  global __github
  if not __github:
    g = Github(GITHUB_AUTH_TOKEN)
    setGithubInstance(g)
  return __github


def getOrganization() -> Organization:
  global __org
  if not __org:
    # Connect to Github
    term.status('Connecting to %s' % (Config.org_name))
    connect_to_org(Config.org_name)
  return __org
