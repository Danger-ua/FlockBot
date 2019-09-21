from atlassian import Confluence
from datetime import datetime

def create_nbpm_collab_page(cir_title, creds):
    collab = Confluence(url='https://collab.test.net/', username=creds['user'], password=creds['password'])
    cir_date = datetime.now().strftime("%Y-%m-%d")
    cir_title = cir_title
    body_text = '''    '''

    page = collab.create_page(space="NBPM", parent_id=143085345, title=cir_title, body=body_text)

