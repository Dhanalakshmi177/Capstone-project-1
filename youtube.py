import os
import googleapiclient.discovery
import googleapiclient.errors
import mysql.connector as db
import streamlit as st
import pandas as pd 
from streamlit_option_menu import option_menu
import plotly.express as px
import time

# -------------------------------------------------------Api Connection 

def api_connect():
 
    api=" # API KEY "

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version,developerKey = api)
    
    return youtube
youtube=api_connect()

# -----------------------------------------------------CONNECTING MYSQL DATABASE
mydb = db.connect(
    host=" host name ",
    port="######",
    user="*****",
    password="*****",
    database= "DB Name"
)
mycursor = mydb.cursor()

# ------------------------------------------------------FETCHING CHANNEL DETAILS

def get_channel_details(channel_id):
    mycursor.execute('''CREATE TABLE IF NOT EXISTS Channel_Table (
                           Channel_Name varchar(255),
                           Channel_Id varchar(255),
                           Subscribers BIGINT,
                           View_Count BIGINT,
                           Playlist_id varchar(100),
                           Total_videos INT,
                           Description Text)''')
    
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id)
    response = request.execute()
    
    for item in response.get('items', []):
        data = {
            'Channel_Name': item['snippet']['title'],
            'Channel_Id': channel_id,
            'Subscribers': item['statistics']['subscriberCount'],
            'View_Count': item['statistics']['viewCount'],
            'Playlist_id': item['contentDetails']['relatedPlaylists']['uploads'],
            'Total_videos': item['statistics']['videoCount'],
            'Description': item['snippet']['description']
        }
       
        channel_details = (data['Channel_Name'], data['Channel_Id'], data['Subscribers'], data['View_Count'], data['Playlist_id'], data['Total_videos'], data['Description'])
        insert_query = ("INSERT INTO Channel_Table (Channel_Name, Channel_Id, Subscribers, View_Count, Playlist_id, Total_videos, Description) VALUES (%s, %s, %s, %s, %s, %s, %s)")
        mycursor.execute(insert_query, channel_details)
        mydb.commit()
        
    return data

#---------------------------------------------------------------FETCHING ALL VIDEO IDS USING NEXT PAGE TOKEN

def get_channel_videos(channel_id):
    video_ids = []

    request = youtube.channels().list(
                   id=channel_id,
                   part='contentDetails')
    response1=request.execute()
    playlist_id = response1['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token)
        response2=request.execute()
  
        for i in range(len(response2['items'])):
            video_ids.append(response2['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = response2.get('nextPageToken')

        if next_page_token is None:
            break
    mycursor.execute("""CREATE TABLE IF NOT EXISTS video_ids (
                        video_id VARCHAR(255)
                    )""") 
    for video_id in video_ids:
        mycursor.execute("INSERT INTO video_ids (video_id) VALUES (%s)", (video_id,))
    mydb.commit()
    
    return video_ids
# ------------------------------------------------------------------FETCHING VIDEO DETAILS
def get_video_details(video_ids):
    video_data = []
    
    try:
        for video_id in video_ids:
            request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            
            mycursor.execute('''CREATE TABLE IF NOT EXISTS Videoz_Table (
                                   Channel_Name varchar(255),
                                   Channel_Id varchar(255),
                                   Video_id varchar(255),
                                   Title varchar(255),
                                   Views bigint,
                                   Likes bigint,
                                   Comments bigint,
                                   Thumbnail varchar(255),
                                   published_at varchar(100),
                                   Duration varchar(100),
                                   Description Text)''')

            for item in response.get('items', []):
                data = {
                    'Channel_Name': item['snippet']['channelTitle'],
                    'Channel_Id': item['snippet']['channelId'],
                    'Video_id': item['id'],
                    'Title': item['snippet']['title'],
                    'Views': item['statistics']['viewCount'],
                    'Likes': item['statistics']['likeCount'],
                    'Comments': item['statistics']['commentCount'],
                    'Thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'published_at': item['snippet']['publishedAt'].replace('T', ' ').replace('Z', ''),
                    'Duration': item['contentDetails']['duration'].replace('PT', ' '),
                    'Description': item['snippet']['description']
                }
                video_data.append(data)

                mycursor.execute("INSERT INTO Videoz_Table (Channel_Name, Channel_Id, Video_id, Title, Views, Likes, Comments, Thumbnail, published_at, Duration, Description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (data['Channel_Name'], data['Channel_Id'], data['Video_id'], data['Title'], data['Views'], data['Likes'], data['Comments'], data['Thumbnail'], data['published_at'], data['Duration'], data['Description']))
                mydb.commit()
                
    except Exception as e:
        print("Error:", e)            
    return video_data

# -------------------------------------------------------------FETCHING COMMENT DETAILS

def get_comments_details(video_ids):
    comment_data=[]
    try:
        mycursor.execute("""CREATE TABLE IF NOT EXISTS comment_table (
                            comment_Id VARCHAR(255),
                            video_Id VARCHAR(255),
                            comment_Text TEXT,
                            comment_Author VARCHAR(255),
                            comment_Published VARCHAR(255)
                        )""")
        
        for video_id in video_ids:
            request=youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(comment_Id=item['snippet']['topLevelComment']['id'],
                         video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                         comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                         comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                         comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'].replace('T', ' ').replace('Z', ''))

                comment_data.append(data)

                mycursor.execute("INSERT INTO comment_table (comment_Id, video_Id, comment_Text, comment_Author, comment_Published) VALUES (%s, %s, %s, %s, %s)",
                               (data['comment_Id'], data['video_Id'], data['comment_Text'], data['comment_Author'], data['comment_Published']))
                mydb.commit()
    except Exception as e:
        print(f"Error: {e}")
    
    return comment_data

#------------------------------------------------------------------- CALLING FUNCTION

def channel_info(channel_id):
    channel_details=get_channel_details(channel_id)
    video_Ids=get_channel_videos(channel_id)
    video_details=get_video_details(video_Ids)
    comment_details=get_comments_details(video_Ids)

    channel_df = pd.DataFrame([channel_details])
    video_df = pd.DataFrame(video_details)
    comment_df = pd.DataFrame(comment_details)

    return {
        "channel_details": channel_df,
        "video_details": video_df,
        "comment_details": comment_df,
    }

# ---------------------------------------------------------- STREAMLIT WEB CODE

with st.sidebar:
    opt = option_menu("Menu",
                    ['Home','Fetch & Store','Q/A'])
            
if opt=="Home":
        st.title(''':red[_YOUTUBE DATA HARVESTING AND WAREHOUSING_]''')
        st.write("#")
        st.write("This project gathers data from YouTube channels using the YouTube Data API, followed by meticulous processing and subsequent warehousing.")
        st.write("To develop a Streamlit application that enables users to enter a YouTube channel ID and obtain channel information via the YouTube Data API.")
        st.write("A SQL data warehouse will host the collected data.")
        st.write("The application ought to provide several search possibilities for retrieving data from the SQL database.")
            
       
if opt == ("Fetch & Store"):
                
        st.markdown("#    ")
        st.write("### ENTER THE YOUTUBE CHANNEL ID ")
        channel_id = st.text_input("enter here below")
        
        if st.button('Fetch & Store'):
                progress_text="Fetching Data , Please wait for a while..."
                my_bar=st.progress(0, text=progress_text)
  
                for percent_complete in range(100):
                    time.sleep(0.25)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                    time.sleep(1)
                    my_bar.empty()

                details = channel_info(channel_id)
                st.subheader('Channel Data')
                st.write(details["channel_details"])

                st.subheader('Video Data')
                st.write(details["video_details"])

                st.subheader('Comment Data')
                st.write(details["comment_details"])

if opt == ("Q/A"):
      questions=st.selectbox("Shoot Your Question",
                                    ["Choose your Questions...",
                                     '1.What are the names of the all videos and their corresponding channels?',
                                     '2. Which channels have the most number of videos, and how many videos do they have?',
                                     '3. What are the top 10 most viewed videos and their respective channels?',
                                     '4. How many comments were made on each video, and what are their corresponding video names?',
                                     '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                     '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                     '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                     '8. What are the names of all the channels that have published videos in the year 2022?',
                                     '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                     '10. Which videos have the highest number of comments, and what are their corresponding channel names?' ],
                                      index=0)

      if questions == '1.What are the names of the all videos and their corresponding channels?':
                  mycursor.execute("""SELECT Title as Title , Channel_Name as Channel_Name  FROM ytproject.videoz_table ;""")
                  df = pd.DataFrame(mycursor.fetchall(), columns=['Title','Channel_Name'])
                  st.write(df)
      
      elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
            mycursor.execute("""SELECT Channel_Name, COUNT(*) AS Video_Count FROM ytproject.videoz_table GROUP BY Channel_Name ORDER BY Video_Count DESC;""")
            df = pd.DataFrame(mycursor.fetchall(), columns=['Channel_Name', 'Video_Count'])
            st.write(df)
            fig = px.bar(df, x='Channel_Name', y='Video_Count',
            labels={'Channel_Name': 'Channel Name', 'Video_Count': 'Number of Videos'},
            title='Videos Count in Channel')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
            
      elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
            mycursor.execute("""SELECT Title, Channel_Name, Views FROM ytproject.videoz_table ORDER BY Views DESC LIMIT 10""")
            data = mycursor.fetchall()
            df = pd.DataFrame(data, columns=['Title', 'Channel_Name', 'Views'])
            st.write(df)
            
            fig = px.bar(df, x='Title', y='Views', color='Channel_Name',
                 labels={'Title': 'Video Title', 'Views': 'Number of Views'},
                 title='Top 10 Most Viewed Videos and Their Respective Channels')
            fig.update_layout(xaxis_tickangle=45)         
            st.plotly_chart(fig)

      elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
            mycursor.execute("""select Channel_Name , Title ,Video_id, Comments from ytproject.videoz_table ;""")
            df = pd.DataFrame(mycursor.fetchall(), columns=['Channel_Name', 'Title','Video_id','Comments'])
            st.write(df)
            fig = px.line(df, x='Comments', y='Video_id',
                  labels={'Comments': 'Number of Comments','Video_id': 'Video id', },
                  title='Number of Comments on Each Video')
            st.plotly_chart(fig)
              
      elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
            mycursor.execute("""SELECT Channel_Name, Video_Id, Title, Likes FROM ytproject.videoz_table v WHERE Likes = (SELECT MAX(Likes)
                                    FROM ytproject.videoz_table WHERE Channel_Name = v.Channel_Name )""")                                
            data = mycursor.fetchall()
            df = pd.DataFrame(data, columns=['Channel_Name','Video_Id', 'Title', 'Likes'])
            st.write(df)
            
            fig = px.bar(df, x='Title', y='Likes', color='Channel_Name',
                        labels={'Title': 'Video Title', 'Likes': 'Number of Likes'},
                        title='Videos with the Highest Number of Likes and Their Corresponding Channels')
            fig.update_layout(xaxis_tickangle=45) 
            st.plotly_chart(fig)

      elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
                mycursor.execute("""SELECT Title as Title , SUM(Likes) as Likes FROM ytproject.videoz_table  GROUP BY Title""")
                df = pd.DataFrame(mycursor.fetchall(),columns=['Title', 'Likes'])
                st.write(df)
                fig = px.line(df, x='Title', y='Likes',
                 labels={'Title': 'Title', 'Likes': 'Likes'},
                 title='Total Number of Likes for Each Video')
                st.plotly_chart(fig)

      elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
                mycursor.execute("""SELECT channel_name AS Channel_Name, View_Count AS Views FROM ytproject.channel_table ORDER BY Views DESC""")
                df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
                st.write(df)
                fig = px.bar(df, x='Channel_Name', y='Views',
                             color='Channel_Name',
                 labels={'Channel_Name': 'Channel Name', 'Views': 'Total Number of Views'},
                 title='Total Number of Views for Each Channel')
                st.plotly_chart(fig)

      elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
            mycursor.execute("""SELECT Channel_Name AS Channel_Name FROM videoz_table WHERE published_at LIKE '2022%' GROUP BY Channel_Name ORDER BY Channel_Name""")
            df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
            st.write(df)
                        
            fig = px.pie(df, names='Channel_Name', 
                 title='Channels that Published Videos in 2022')
            st.plotly_chart(fig)

      elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
            mycursor.execute("""SELECT Channel_Name AS Channel_Name,AVG(duration)/60 AS "Average_Video_Duration (mins)" FROM ytproject.videoz_table
                                GROUP BY Channel_Name ORDER BY AVG(Duration)/60 DESC""")
            df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
            st.write(df)

            fig = px.bar(df, x='Channel_Name', y='Average_Video_Duration (mins)',
                 labels={'Channel_Name': 'Channel Name', 'Average_Video_Duration (mins)': 'Average Video Duration (mins)'},
                 title='Average Duration of Videos in Each Channel')
            st.plotly_chart(fig)

      elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
           mycursor.execute(""" SELECT Channel_Name,  Title, Comments FROM ytproject.videoz_table v WHERE Comments = (
                                        SELECT MAX(Comments) FROM ytproject.videoz_table WHERE Channel_Name = v.Channel_Name ); """)               
           data = mycursor.fetchall()
           df = pd.DataFrame(data, columns=['Channel_Name','Title','Comments'])
           st.write(df)

           fig = px.line(df, x='Comments',y='Channel_Name', text='Title',
                  labels={'Channel_Name': 'Channel_Name ','Title': 'Title', 'Comments': 'Comments'},
                  title='Videos with the Highest Number of Comments and Their Corresponding Channels')
           fig.update_traces(texttemplate='%{text}', textposition='top center', mode='markers+lines')
           fig.update_layout(xaxis_title='Comments', yaxis_title='Channel Name')  
           st.plotly_chart(fig)
