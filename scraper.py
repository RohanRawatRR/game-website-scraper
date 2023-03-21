import requests, datetime
import mysql.connector
from bs4 import BeautifulSoup

from settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME

# Get user input for the month
year_list = input("Enter any year or years (e.g. 2021,2022): ")

year_list = list(year_list.split(","))

base_url = 'https://www.gameinformer.com'


# Find the section for the specified month
# month_section = soup.find('h2', text=month)


conn = mysql.connector.connect(
    user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST, database=DATABASE_NAME
)
cur = conn.cursor(buffered=True)

for year in year_list:
    print("***********YEAR {}*******".format(year))
    final_url = base_url + '/' + year

    # Send a GET request to the URL and parse the HTML using BeautifulSoup
    response = requests.get(final_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_game_sections = soup.find_all('span', {"class": "calendar_entry"})

    if all_game_sections:
        # Loop through each game section and print its details
        for game_details in all_game_sections:

            # Get the game data
            created_at = datetime.datetime.now()
            game_name = game_details.find('a').text.strip()
            game_url = game_details.find('a').attrs['href'].strip()
            href = game_url
            game_id = game_url.split('/')[-1]
            existing_game_data = cur.execute(
                '''SELECT * FROM gi_videogame WHERE game_id="{}"'''.format(game_id))
            print(game_name)
            game_detail_url = base_url + game_url
            game_detail_response = requests.get(game_detail_url)

            # Find the section for the specified game info
            game_detail_soup = BeautifulSoup(
                game_detail_response.content, 'html.parser')
            game_info_section = game_detail_soup.find(
                'div', {'class': 'game-info'})
            game_info = game_info_section.find(
                'span', {'class': 'field-content'})

            for game_detail_div in game_info.find_all('div', recursive=False):
                try:
                    label_text = game_detail_div.find(
                        'div', {'class': 'field__label', }).text.strip()
                    field_items = game_detail_div.find(
                        'div', {'class': 'field__items'})
                    if label_text == "Platform:":
                        all_platforms_list = []
                        for field in field_items.find_all('div'):
                            if field != '':
                                all_platforms_list.append(field.text.strip())
                    elif label_text == "Developer:":
                        developer = field_items.text.strip()
                    elif label_text == "Publisher:":
                        publisher = field_items.text.strip()
                    elif label_text == "Genre:":
                        genre = field_items.text.strip()
                    elif label_text == "Industry rating:":
                        industry_rating = field_items.text.strip()
                    elif label_text == "Release Date:":
                        all_releases_dict = {}
                        all_release_dates = field_items
                        for field in all_release_dates.find_all('div'):
                            if field != '':
                                date = datetime.datetime.strptime(
                                    field.text.strip().split('(')[0].strip(), '%B %d, %Y').date()
                                release_platforms = field.text.strip().split(
                                    '(')[-1].split(')')[0]
                                # release_platforms = release_platforms[release_platforms.find("(")+1:release_platforms.find(")")]
                                all_releases_dict[date] = release_platforms
                except Exception as e:
                    pass
            # save videogames data to postgresql database
            try:
                game_obj_id = cur.fetchall()[0][0]
            except Exception as e:
                game_obj_id = None
            if not game_obj_id:
                cur.execute('''INSERT INTO gi_videogame (created_at, game_id, name, all_platforms, developer, publisher, genre, industry_rating) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(
                    created_at, game_id, game_name, ', '.join(all_platforms_list), developer, publisher, genre, industry_rating, ))
                conn.commit()
                game_obj_id = cur.lastrowid

            for release_date, release_platform in all_releases_dict.items():
                try:
                    cur.execute('''INSERT INTO gi_videogame_release (
                        videogame_id, 
                        release_date, 
                        released_on_platforms
                        ) VALUES ("{}", "{}", "{}")'''.format(game_obj_id, release_date, release_platform))
                    conn.commit()
                except Exception as e:
                    pass
    else:
        print('No data found for year {}'.format(year))

conn.close()
