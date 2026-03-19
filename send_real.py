import time, requests, json

time.sleep(2)

# SEND TO REAL EMAIL ADDRESSES
payload = {
    'name': 'Production Campaign',
    'senders': [{
        'email': 'HASSNAINBALOCH233@GMAIL.COM',
        'password': 'uxwl qavz ofuv blyd',
        'provider': 'gmail'
    }],
    'leads': [
        {
            'Business Name': 'DIGIVINE',
            'Email': 'DIGIVINE.HQ@GMAIL.COM',
            'Location': 'DGKHAN'
        }
    ],
    'templates': [{
        'name': 'Template 1',
        'content': 'Hey [Business Name],\n\nI noticed your business in [City].\n\nYou might be missing out on Google rankings.\n\nLet me know if interested!\n\n— Hassnain'
    }],
    'subject_lines': ['Quick opportunity for [Business Name]'],
    'follow_ups': [],
    'emails_per_account': 1
}

print("Sending campaign...")
r = requests.post('http://localhost:5000/api/send-campaign', json=payload)
campaign_data = r.json()
cid = campaign_data['campaign_id']
print(f"Campaign ID: {cid}")
print(f"Message: {campaign_data['message']}")

# Wait and check status
time.sleep(5)
r2 = requests.get(f'http://localhost:5000/api/campaigns/{cid}')
data = r2.json()

print(f"\nResults:")
print(f"Status: {data['status']}")
print(f"Sent: {data['sent']}")
print(f"Failed: {data['failed']}")

if data['results']:
    for result in data['results']:
        print(f"\nEmail to: {result['email']}")
        print(f"Status: {result['status']}")
        print(f"Subject: {result['subject']}")
        if 'reason' in result:
            print(f"Reason: {result['reason']}")
