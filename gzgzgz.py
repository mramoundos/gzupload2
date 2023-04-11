import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote


# Replace 'your_refresh_token_here' with your actual Chartmetric refresh token
refresh_token = 'HwtFUNV6fBP2WnM7N4FXTv3y0Ntf98gN13s05aycepYQdVgnoKvBH4ldDi0uqMCo'

# Obtain the access token using the refresh token
token_url = 'https://api.chartmetric.com/api/token'
token_data = json.dumps({'refreshtoken': refresh_token})
headers = {'Content-Type': 'application/json'}

response = requests.post(token_url, data=token_data, headers=headers)

if response.status_code == 200:
    token_response = response.json()

    if 'token' in token_response:
        access_token = token_response['token']
        print(f"Access token: {access_token}")

        # Use the access token in the Authorization header for subsequent API requests
        auth_headers = {'Authorization': f"Bearer {access_token}"}
    else:
        print("Error: The response does not contain an access token.")
else:
    print(f"Error: Unable to obtain access token. Status code: {response.status_code}")
    exit(1)


def refresh_token_if_expired():
    global access_token
    global auth_headers
    
    # Check if access token is already defined and not expired
    if access_token is None or datetime.now() >= token_expiration_time:
        # Obtain a new access token using the refresh token
        token_url = 'https://api.chartmetric.com/api/token'
        token_data = json.dumps({'refreshtoken': refresh_token})
        headers = {'Content-Type': 'application/json'}

        response = requests.post(token_url, data=token_data, headers=headers)

        if response.status_code == 200:
            token_response = response.json()

            if 'token' in token_response:
                access_token = token_response['token']
                print(f"Access token: {access_token}")

                # Use the access token in the Authorization header for subsequent API requests
                auth_headers = {'Authorization': f"Bearer {access_token}"}
                
                # Define token expiration time based on current time and expires_in value from token_response
                expires_in = token_response.get('expires_in', 3600)
                token_expiration_time = datetime.now() + timedelta(seconds=expires_in)
            else:
                print("Error: The response does not contain an access token.")
        else:
            print(f"Error: Unable to obtain access token. Status code: {response.status_code}")
            exit(1)


import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote

# Replace 'your_refresh_token_here' with your actual Chartmetric refresh token
refresh_token = 'your_refresh_token_here'

# Define the function to refresh the access token if it's expired
def refresh_token_if_expired():
    global access_token, token_expiration_time
    if access_token is None or datetime.now() >= token_expiration_time:
        token_url = 'https://api.chartmetric.com/api/token'
        token_data = json.dumps({'refreshtoken': refresh_token})
        headers = {'Content-Type': 'application/json'}

        response = requests.post(token_url, data=token_data, headers=headers)

        if response.status_code == 200:
            token_response = response.json()

            if 'token' in token_response:
                access_token = token_response['token']
                print(f"Access token: {access_token}")

                # Set the expiration time of the token to 50 minutes from now
                token_expiration_time = datetime.now() + timedelta(minutes=50)

                # Use the access token in the Authorization header for subsequent API requests
                auth_headers = {'Authorization': f"Bearer {access_token}"}
            else:
                print("Error: The response does not contain an access token.")
                exit(1)
        else:
            print(f"Error: Unable to obtain access token. Status code: {response.status_code}")
            exit(1)

# Define the function to fetch the artist data from Chartmetric
def fetch_artist_data(artist_name, endpoint, access_token):
    refresh_token_if_expired()
    encoded_artist_name = quote(artist_name)
    artist_id, artist_rank, monthly_listeners = None, None, None

    # Make the request to the Chartmetric API
    artist_url = f"https://api.chartmetric.com/api/{endpoint}?q={encoded_artist_name}"
    response = requests.get(artist_url, headers=auth_headers)

    if response.status_code == 200:
        artist_data = response.json()
        if 'obj' in artist_data and artist_data['obj'] is not None:
            artist_id = artist_data['obj']['id']
            artist_rank = artist_data.get('cm_artist_rank')
            monthly_listeners = artist_data.get('sp_monthly_listeners')
        else:
            print(f"Error: Unable to fetch data from Chartmetric API. Artist '{artist_name}' not found.")
            artist_id, artist_rank, monthly_listeners = None, None, None
    else:
        print(f"Error: Unable to fetch data from Chartmetric API. Status code: {response.status_code}")
        artist_id, artist_rank, monthly_listeners = None, None, None

    return artist_id, artist_rank, monthly_listeners
def fetch_comparable_artists_data(gz_monthly_listeners, access_token):
    # Determine the range of monthly listeners for comparable artists
    if gz_monthly_listeners is None:
        print("Error: Unable to fetch comparable artist data. No monthly listeners data for Garrett Zoukis.")
        return []
    elif gz_monthly_listeners < 25000:
        comparable_listeners_min = gz_monthly_listeners - 5000
        comparable_listeners_max = gz_monthly_listeners + 20000
    elif gz_monthly_listeners < 100000:
        comparable_listeners_min = gz_monthly_listeners - 10000
        comparable_listeners_max = gz_monthly_listeners + 10000
    elif gz_monthly_listeners < 500000:
        comparable_listeners_min = gz_monthly_listeners - 25000
        comparable_listeners_max = gz_monthly_listeners + 25000
    else:
        comparable_listeners_min = gz_monthly_listeners - 50000
        comparable_listeners_max = gz_monthly_listeners + 50000

    # Fetch the comparable artists using the Chartmetric API
    endpoint = "search"
    comparable_artists = []
    for i in range(1, 6):
        search_query = f"search?type=artist&sort=cm_artist_rank&reverse=false&range={comparable_listeners_min}-{comparable_listeners_max}&page={i}"
        search_url = f"https://api.chartmetric.com/api/{endpoint}?{search_query}"
        response = requests.get(search_url, headers=auth_headers)

        if response.status_code == 200:
            search_data = response.json()
            if 'obj' in search_data and search_data['obj'] is not None:
                for artist in search_data['obj']['data']:
                    artist_name = artist['name']
                    monthly_listeners = artist.get('sp_monthly_listeners')
                    if monthly_listeners is not None:
                        comparable_artists.append([artist_name, monthly_listeners])
            else:
                break
        else:
            print(f"Error: Unable to fetch comparable artist data from Chartmetric API. Status code: {response.status_code}")
            break

    return comparable_artists
def generate_table(comparable_artists, gz_monthly_listeners):
    headers = ["Artist Name", "Month-over-Month Change"]
    table_data = []
    
    for artist in comparable_artists:
        artist_name = artist[0]
        monthly_listeners = artist[1]
        if gz_monthly_listeners is not None and monthly_listeners is not None:
            mom_change = round((monthly_listeners - gz_monthly_listeners) / gz_monthly_listeners * 100, 2)
        else:
            mom_change = None
        table_data.append([artist_name, mom_change])
    
    table_data = sorted(table_data, key=lambda x: x[1], reverse=True)
    
    print(tabulate(table_data, headers=headers, numalign="right"))
    
    return table_data

def main():
    # Replace the artist_name variable with the name of the artist you want to analyze
    artist_name = 'Billie Eilish'

    # Fetch the artist data from Chartmetric
    endpoint = 'artist'
    gz_artist_id, gz_artist_rank, gz_monthly_listeners = fetch_artist_data(artist_name, endpoint, access_token)

    if gz_artist_id is None:
        print("Error: Unable to fetch data from Chartmetric API.")
        exit(1)

    # Fetch the comparable artists' data from Chartmetric
    endpoint = 'search/artist'
    comparable_artists = fetch_comparable_artists_data(gz_monthly_listeners, access_token)

    if comparable_artists is None:
        print("Error: Unable to fetch data from Chartmetric API.")
        exit(1)

    # Generate the table of comparable artists
    comparable_artists_table = generate_table(comparable_artists)

    # Generate the table of month-over-month changes
    mom_changes_table = generate_mom_changes_table(comparable_artists, gz_monthly_listeners)

    # Print the Garrett Zoukis data, comparable artists table, and month-over-month changes table
    print_gz_data(gz_artist_id, gz_artist_rank, gz_monthly_listeners)
    print_table(comparable_artists_table, 'Comparable Artists')
    print_table(mom_changes_table, 'Month-over-Month Changes')


if __name__ == '__main__':
    main()



