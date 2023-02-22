# Imports
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os


# Urls
# Log-in Webpage
login_url = 'https://mwomercs.com/do/login'
# Logged-In Player Mech Stats Webpage
profileMechStats_url = 'https://mwomercs.com/profile/stats?type=mech'
# Logged-In Player's Raw Data of Mechs
collection_data_url = 'https://mwomercs.com/mech-collection/data'
# Logged-In Player's Profile Webpage
player_url = 'https://mwomercs.com/profile'

# Current Working Directory, needed for the storing of the files being created.
cwd = os.getcwd()

# Gather user credentials
playeremail = input("Please enter your email: ")

playerpassword = input("Please enter your password: ")


# Player's Credentials to be used on log-in
payload = {
    'email': playeremail,
    'password': playerpassword
}

print("Attempting to log in to mwomercs.com with the supplied credentials and gather the relevant information."
      " One moment please. :)")

print("Please do not touch your keyboard while the program is working. Unless you want this prompt to disappear"
      " into the aether upon completion.")


try:
    # Open a session
    with requests.session() as s:
        s.post(login_url, data=payload)
        r = s.get(profileMechStats_url)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Obtain information from tag <table>
        mechs_table = soup.find('table', class_='table table-striped')

        # Collect the headers
        headers = []
        for i in mechs_table.find_all('th'):
            title = i.text
            headers.append(title)

        # Create the dataframe
        mech_data = pd.DataFrame(columns=headers)

        # Fill the dataframe
        for j in mechs_table.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
            length = len(mech_data)
            mech_data.loc[length] = row


        # Get player profile name
        r2 = s.get(player_url)
        soup2 = BeautifulSoup(r2.content, 'lxml')
        playerprofilename = soup2.find('h1')
        playername = playerprofilename.text

        # Convert scraped data table to .csv
        mech_data.to_csv(cwd + "\\" + playername + "_" + 'mech_data_unsorted.csv', index=False)

        # ----------- Sort By Time Played -----------
        sorted_time_played = pd.read_csv(playername + "_" + 'mech_data_unsorted.csv')

        # Find all 'mechs that have X>24 hours play time
        filtered = sorted_time_played[sorted_time_played['Time Played'].str.contains("day")]

        # List to store all converted times for 'mechs with X>24 hours play time
        times_to_add = []

        # Do calculations to show appropriate number of hours instead of "X day(s)"
        for k in filtered['Time Played']:
            time = k.split(' ')
            hours_to_add = 24 * int(time[0])
            # time[1] contains "days" which is what we are removing.
            hms = time[2]
            hms = hms.split(':')
            hours = hours_to_add + int(hms[0])
            hms = str(hours) + ':' + hms[1] + ':' + hms[2]
            times_to_add.append(hms)

        # Change the Time Played strings of the 'mechs with X>24 hours time played to the calculated amount
        for x in range(len(times_to_add)):
            sorted_time_played.loc[filtered.index[x], 'Time Played'] = times_to_add[x]

        # List to store all 'mechs time played
        allHMS = []

        # Remove all ':' characters from the string and convert the resulting string to an integer
        for y in sorted_time_played['Time Played']:
            time = y.split(':')
            hms = time[0] + time[1] + time[2]
            allHMS.append(int(hms))

        # Change the Time Played Strings to the integers
        for z in (range(len(allHMS))):
            sorted_time_played.loc[sorted_time_played.index[z], 'Time Played'] = allHMS[z]

        # Sort the Time Played column by the integer values in descending order
        sorted_time_played = sorted_time_played.sort_values(['Time Played'], axis=0, ascending=False)

        # List to store our conversion from integer back to string with the appropriate format
        mutated_times = []

        # Convert integers to string in the correct format
        # I got lazy and tired. Went with ugly brute-forced code to reformat the time back to H:M:S
        for a in sorted_time_played['Time Played']:
            mtime = str(a)
            if len(mtime) == 1:
                mtime = "00:00:0" + mtime
            elif len(mtime) == 2:
                mtime = "00:00:" + mtime
            elif len(mtime) == 3:
                mtime = "00:0" + mtime[0] + ':' + mtime[1] + mtime[2]
            elif len(mtime) == 4:
                mtime = "00:" + mtime[0] + mtime[1] + ':' + mtime[2] + mtime[3]
            elif len(mtime) == 5:
                mtime = "0" + mtime[0] + ':' + mtime[1] + mtime[2] + ':' + mtime[3] + mtime[4]
            elif len(mtime) == 6:
                mtime = mtime[0] + mtime[1] + ':' + mtime[2] + mtime[3] + ':' + mtime[4] + mtime[5]
            elif len(mtime) > 6:
                seconds = mtime[-2] + mtime[-1]
                minutes = mtime[-4:-2]
                hours = mtime[:-4]
                mtime = hours + ':' + minutes + ':' + seconds
            mutated_times.append(mtime)

        # Change the Time Played Integers to Strings
        for b in range(len(mutated_times)):
            sorted_time_played.loc[sorted_time_played.index[b], 'Time Played'] = mutated_times[b]

        # Remove column that offers no real beneficial information
        sorted_time_played.drop(columns=['XP Earned'], inplace=True)

        # As the mech's were already previously sorted, and we have done no rearranging, simply output to .csv
        sorted_time_played.to_csv(cwd + "\\" + playername + "_" + 'mech_data_sorted_TP.csv', index=False)

        # ---------- Sort by Matches Played ----------
        # Create .csv of mech's sorted by matches played.
        sorted_matches_played = pd.read_csv(playername + "_" + 'mech_data_unsorted.csv')

        # Removed columns that offer no real beneficial information
        sorted_matches_played.drop(columns=['Time Played', 'XP Earned'], inplace=True)

        sorted_matches_played.sort_values(["Matches Played"], axis=0, ascending=False, inplace=True)
        sorted_matches_played.to_csv(cwd + "\\" + playername + "_" + 'mech_data_sorted_MP.csv', index=False)

        # ---------- Player Profile Scraper ----------
        response = s.get(collection_data_url)

        # Create a file to store the raw data
        file1 = open(cwd + '\\' + playername + "_" + 'mech_collection.json', 'w')

        # Fill the file with the data for use
        file1.writelines(response.text)

        # Close the file to prevent memory mismanagement
        file1.close()

        # A list container to store which 'mechs are owned
        owned_mechs = []

        # A dictionary to contain 'Mech IDs and their skill nodes.
        dict_mechIDs = {}

        with open(cwd + "\\" + playername + "_" + 'mech_collection.json') as f:
            # Convert the JSON file into a python recognizable data format (I.E., Dict)
            data = json.load(f)
            collection = data['collection']
            for collection_data in collection:
                variants_data = collection_data['variants']
                for specific_variant in variants_data:
                    if variants_data[specific_variant]['owned'] is True:
                        owned_mechs.append(variants_data[specific_variant]['display_name'])

                        # Store the list of mechIDs for a specific variant
                        mechIDs = variants_data[specific_variant]['mech_ids']

                        # Create an entry in the dictionary of 'Mechs to hold the list of mechIDs
                        dict_mechIDs[variants_data[specific_variant]['display_name']] = mechIDs

            # A list to contain tuples (Mech Variant, Name player gave it, # skill points assigned).
            list_mech_chass_name_SP = []

            for mech, mechID in dict_mechIDs.items():
                for i in mechID:
                    # We now have access to each individual 'mechs mechID.

                    # ------------- Individual mech's skill point scraper ---------------
                    # Create url of the specific 'Mech we want the information of
                    spec_mech_url = collection_data_url + "/stats?mid[]=" + i
                    response_spec_mech = s.get(spec_mech_url)
                    dict_spec_mech = json.loads(response_spec_mech.text)

                    for mech_chassis in dict_spec_mech['mechs']:
                        mech_name = mech_chassis['name']
                        spec_mech_skills = mech_chassis['skills']['NumEquippedSkillNodes']
                        list_mech_chass_name_SP.append((mech, mech_name, spec_mech_skills))

            # Convert list of tuples (mech variant, name, equipped skillpoints) into a dataframe.
            df_list_mech_name_sp = pd.DataFrame(list_mech_chass_name_SP, columns=['Variant', 'Name', 'Skill Points'])

            df_list_mech_name_sp.to_csv(cwd + "\\" + playername + "_" + 'owned_mechs_SP.csv', index=False)

            # Convert list of owned 'mechs into a dataframe
            df_owned_mechs = pd.DataFrame(owned_mechs, columns=['Owned \'Mechs'])

            # Create a .csv from the dataframe of owned 'mechs
            df_owned_mechs.to_csv(cwd + "\\" + playername + "_" + 'owned_mechs.csv', index=False)

            print("Your spreadsheets have been created! :D")
except AttributeError:
    print("Incorrect credentials supplied. The program failed to log in to mwomercs.com and find the appropriate "
          "tables.")

input("Press 'Enter' to continue or simply close this script.")
