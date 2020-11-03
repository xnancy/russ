import json
def extract_elements(data):
    commands = []
    for elem in data['info']:
        r = elem
        if 'xid' in r:
            html_id = r['id'] if r['id'] != None else "None"
            html_text = r['text'] if 'text' in r  else "None"
            row = (r['styles'], r['xid'], r['height'], r['width'], r['top'], r['hidden'], r['children'], r['ref'], r['topLevel'], r['classes'], r['tag'],
                html_id, html_text, r['left'], r['attributes'], 1)
            commands.append(row)
    return commands


