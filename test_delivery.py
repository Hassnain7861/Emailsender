import time, requests, json
time.sleep(2)
payload = {
    'name': 'Real Delivery Test',
    'senders': [{'email': 'HASSNAINBALOCH233@GMAIL.COM', 'password': 'uxwl qavz ofuv blyd', 'provider': 'gmail'}],
    'leads': [{'Business Name': 'DIGIVINE', 'Email': 'HASSNAINBALOCH233@GMAIL.COM', 'Location': 'DGKHAN'}],
    'templates': [{'name': 'T1', 'content': 'Hey [Business Name],\n\nThis is a real test from campaign system.\n\nIf you see this, it works!\n\n— Gordon'}],
    'subject_lines': ['TEST: System Working'],
    'follow_ups': [],
    'emails_per_account': 1
}
r = requests.post('http://localhost:5000/api/send-campaign', json=payload)
cid = r.json()['campaign_id']
time.sleep(3)
r2 = requests.get(f'http://localhost:5000/api/campaigns/{cid}')
data = r2.json()
print(f'Campaign Status: {data["status"]}')
print(f'Emails Sent: {data["sent"]}')
if data["results"]:
    print(f'Recipient: {data["results"][0]["email"]}')
