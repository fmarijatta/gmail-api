import re

def extract_metrics(body, message_id, message_date, check_output = False):
    out = []
    url_regex = re.compile(r"\(https:\/\/archiveofourown.org\/works\/\d+\).", re.IGNORECASE)
    #Regex to extract key info from message body.
    body_main = re.split('[=]+', body)[1] # remove email title
    body_trim = re.split('-{40,}', body_main)[0] # trim trailing dashes at the end of the body text
    body_list = re.split('-{10,}', body_trim) #remove new-line dividers (----)
    for item in body_list:
        body_clean = re.sub(url_regex, '', item.strip()).strip() #trim spaces and remove url string
        metrics, title = re.split(' left kudos on ', body_clean)
        title = title.strip('"')

        #Identify number of guest kudos
        guest_match = re.search('[Aa\d]+\sguests?$', metrics)
        if guest_match:
            guests = guest_match.group()
            n_guests = re.sub('\sguests?', '', guests)
            n_guests = n_guests if n_guests.lower() != 'a' else 1
            metrics = metrics.replace(guests, '')
            and_match = re.search(',?\sand', metrics)
            if and_match:
                metrics = metrics.replace(and_match.group(), '').strip()
        else:
            n_guests = 0

        # Identify number of user kudos
        if len(metrics) == 0:
            n_users = 0
        else:
            users = metrics.replace(',', '').replace(' and ', ' ')
            n_users = users.count(' ') + 1
        
        extracted_data = {
                            "id": message_id,
                            "date": message_date,
                            "title": title,
                            "n_users": n_users,
                            "n_guests": n_guests
                        }
        out.append(extracted_data)
        if check_output:
            print(f'Original body: {body_clean}')
            print(f'Extracted number of users: {n_users}')
            print(f'Extracted number of guests: {n_guests}')
            print('\n')
    return out
    