import time, requests

time.sleep(2)

payload = {
    'name': 'Send to DIGIVINE',
    'senders': [{
        'email': 'HASSNAINBALOCH233@GMAIL.COM',
        'password': 'uxwl qavz ofuv blyd',
        'provider': 'gmail'
    }],
    'leads': [{
        'Business Name': 'DIGIVINE',
        'Email': 'digivine.hq@gmail.com',
        'Location': 'DGKHAN'
    }],
    'templates': [{
        'name': 'Template 1',
        'content': 'Hey [Business Name],\n\nI noticed your business in [City].\n\nYou might be missing out on Google rankings.\n\nWould you be interested in learning more?\n\n- Hassnain'
    }],
    'subject_lines': ['Quick Question About Your Google Rankings'],
    'follow_ups': [],
    'emails_per_account': 1
}

r = requests.post('http://localhost:5000/api/send-campaign', json=payload)
cid = r.json()['campaign_id']
print(f'Campaign started: {cid}')

time.sleep(4)

r2 = requests.get(f'http://localhost:5000/api/campaigns/{cid}')
data = r2.json()

print(f'Status: {data["status"]}')
print(f'Sent: {data["sent"]}')
print(f'Failed: {data["failed"]}')

if data['results']:
    result = data['results'][0]
    print(f'\nEmail sent to: {result["email"]}')
    print(f'Status: {result["status"]}')
    print(f'Subject: {result.get("subject", "N/A")}')
