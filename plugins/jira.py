from atlassian import Jira
import utilslib

links = utilslib.load_config()['atlassian']['links']


def create_issue(creds, issue_summary, issue_description):
    jira = Jira(url=links['jira'],
                username=creds['user'],
                password=creds['password'])
    issue = {
        'project': {'key': 'SRE'},
        'issuetype': {
            "name": "Task"
        },
        'summary': issue_summary,
        'description': issue_description,
        'components': [{'name': 'SRE-L1'}]
    }
    issue = jira.issue_create(fields=issue)
    print(issue)
    if not issue.get('key', None):
        del jira
        raise Exception(issue['errors'])
    jira.assign_issue(issue['key'], creds['user'])
    jira.set_issue_status(issue['key'], status_name='Done')
    del jira
    return issue['key']
