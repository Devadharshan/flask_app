import requests

# Replace with your own ServiceNow instance URL, username, and password
instance_url = 'https://your_instance.service-now.com'
username = 'your_username'
password = 'your_password'

# Construct the URL to fetch ticket details (change 'incident' to the table you need)
url = f'{instance_url}/api/now/table/incident'

# Set proper headers
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Make the GET request with basic authentication
response = requests.get(url, auth=(username, password), headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()
    # Example: Print ticket details
    for ticket in data['result']:
        print(f"Ticket Number: {ticket['number']}")
        print(f"Short Description: {ticket['short_description']}")
        print(f"State: {ticket['state']}")
        print()  # Empty line for readability
else:
    print(f"Failed to retrieve data: {response.status_code} - {response.text}")
