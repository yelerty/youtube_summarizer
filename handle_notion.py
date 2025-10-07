import httpx
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('NOTION_API_TOKEN')
#database_id = '16ee540d45c480d59429fd92cdc2a8eb'
## click ... right of the 'Table' and Click 'Copy link to view' (chain shape)
database_id = os.getenv('NOTION_DATABASE_ID', '16ee540d45c480948fbff0e3a533d25c')



def mapNotionResultToVideo(result):
  # you can print result here and check the format of the answer.
  video_id = result['id']
  properties = result['properties']
  title = properties['Title']['title'][0]['text']['content']
  url = properties['URL']['rich_text'][0]['text']['content']
  used = properties['used']['checkbox']

  return {
	#'Title':title,
    'URL': url,
    'used': used
    #'video_id': video_id
  }

def getUrlFromNotionDB():
  url = f'https://api.notion.com/v1/databases/{database_id}/query'

  r = httpx.post(url, headers={
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2022-06-28"
  })

  result_dict = r.json()
  #print("result_dict:", result_dict['results'])
  video_list_result = result_dict['results']

  videos = []

  for video in video_list_result:
      videos.append(mapNotionResultToVideo(video))

  df_x = pd.DataFrame(videos, columns=['URL', 'used'])
  return df_x


def get_first_unused_url():
	df = getUrlFromNotionDB()
	# Filter rows where 'used' column value is False
    filtered_rows = df[df['used'] == False]
    
    # Return the first URL from the filtered rows
    return filtered_rows.iloc[0]['URL']

#youvideos = getUrlFromNotionDB()
# json.dumps is used to pretty print a dictionary
#print('Video URLs:\n', youvideos)



