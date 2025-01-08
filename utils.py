import json, re
import pandas as pd
import folium
from tqdm import tqdm


async def get_recent_messages(tg_client, channel_username, num_messages):
    async with tg_client:
        messages = []
        async for message in tg_client.iter_messages(channel_username, limit=num_messages):
            messages.append(message)
    return messages


def prompt_model(text, openai_client):
  completion = openai_client.chat.completions.create(
      model="gpt-4o",
      messages=[
          {"role": "user", "content": "In the following text, if geographical locations are mentioned, for each location mentione, provide a JSON dictionary (events) with fields including the location description in English (location), the city or town mentioned in the location in English (town), the country mentioned in the location in English (country), what happened at that location (description). If the message is not in English, please translate the information contained within the JSON dictionary to English. This is the text: " +text}
      ]
  )
  response_string = completion.choices[0].message.content
  response_string = response_string.replace("\n", "")
  return response_string



def convert_to_json(response_string):
  # Regular expression to find JSON-like content (dictionary pattern)
  json_pattern = r"\[.*?\]"
  match = re.search(json_pattern, response_string)
  if match is not None:
    json_text = match.group()
    data = json.loads(json_text)
  else:
    data = None
  return data

def prompt_model_for_location(text, openai_client):
  messages = [
          {"role": "user", "content": """Please give me the only the latitude and longitude of the following location: """ +text+""". Output the coordinates in the following format: {"lat": latitude, "lon": longitude} If you cannot find specific location, just return {"lat": 0, "lon": 0}"""}
      ]
  completion = openai_client.chat.completions.create(
      model="gpt-4o",
      messages=messages
  )
  response_string = completion.choices[0].message.content
  response_string = response_string.replace("\n", "")
  return response_string

def geocode_results_openai(parsed_results_df, openai_client):
    print("Geocoding events... pray even harder")
    for i in tqdm(range(len(parsed_results_df))):
       town = parsed_results_df.loc[i, "town"]
       country = parsed_results_df.loc[i, "country"]
       response = prompt_model_for_location( f"{town}, {country}", openai_client)
       if re.match(r"^\{.*\}$", response):
            response = re.sub(r"\\", "", response)
            coords_dict = eval(response)
            lat = coords_dict["lat"]
            lon = coords_dict["lon"]
            parsed_results_df.loc[i, "coords"] = f"({lat}, {lon})"
            parsed_results_df.loc[i, "lat"] = lat
            parsed_results_df.loc[i, "lon"] = lon
    geolocated_events_df = parsed_results_df[parsed_results_df['coords'] != "(0, 0)"]
    geolocated_events_df = geolocated_events_df.reset_index(drop = True)
    return geolocated_events_df

def parse_results(openai_client, message_texts, message_dates):
  print("Parsing message events... pray that the LLM doesn't hallucinate")
  dfs = []
  for i in tqdm(range(len(message_texts))):
    text = message_texts[i]
    date = message_dates[i]
    # Remove error-prone formatting
    text = text.replace("\n\xa0\n", "")
    text = text.replace("\n\n", "")
    response_string = prompt_model(text, openai_client)
    data = convert_to_json(response_string)
    if data is not None:
      for i in range(len(data)):
        data[i]['date'] = date
      df = pd.DataFrame(data = data)
      dfs.append(df)
  parsed_results_df = pd.concat(dfs)
  parsed_results_df = parsed_results_df.reset_index(drop=True)
  return parsed_results_df


def build_map(geolocated_events):
    # Create a Folium map centered around the average location
    center_lat = geolocated_events['lat'].mean()
    center_lon = geolocated_events['lon'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="Cartodb dark_matter")

    # Add each point to the map
    for idx, row in geolocated_events.iterrows():
        lat= row['lat']
        lon= row['lon']
        tooltip_html = f"""
            <div style="max-width: 2000px; white-space: normal;">
                <b>Location:</b> {row['location']}<br><br>
                <b>Date:</b> {row['date']}<br><br>
                <b>Event Description:</b> {row['description']}
            </div>
        """
        tooltip = folium.Tooltip(tooltip_html,style='width:200px; height:200px')
        folium.Marker(
            location=[lat, lon],
            tooltip=tooltip,
            icon=folium.Icon(color='orange', icon='triangle-exclamation', prefix='fa') # Tooltip shows on hover
        ).add_to(m)
    return m
