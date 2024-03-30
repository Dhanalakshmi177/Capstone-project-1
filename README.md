# YouTube Data Harvesting and Warehousing
This project gathers data from YouTube channels using the YouTube Data API, followed by meticulous processing and subsequent warehousing.
## Problem Statemnt 
To develop a Streamlit application that enables users to enter a YouTube channel ID and obtain channel information via the YouTube Data API.
A SQL data warehouse will host the collected data.
The application ought to provide several search possibilities for retrieving data from the SQL database.
## Overview
In order to get data from YouTube channels for meticulous processing and warehousing, the project leverages the YouTube Data API. 
The collected data is initially kept in SQL records in order to enable thorough data analysis. The Streamlit app then shows the data that was retrieved.
## Take Away Skills
The following skills were acquired from the project:
Youtube API integration,
Python scripting,
Data Management using MySQL,
Streamlit app development,
Pandas,
Plotly data visualization.
## Work Flow
* Connecting API :
To get information about the channel, video, and comments, establish a connection to the YouTube API. The Python Google API client library is used to submit requests and get the required information.
* Harvesting Data :
  For users to enter the channel ID and retrieve information, the Streamlit app generates a simple user interface.
* Data Management :
  Initially the harvested data is stored in structured MySQL database. This meticulous process ensures that the collected data is organized and optimized for efficient querying and analysis in the 'mysql' 
  environment .
* Data Analysis :
  By utilising join methods in SQL queries, user input determines which channels provide valuable insights.
* Showcase Data :
   At Last, to assist users in analysing the data, Streamlit uses tables and charts to illustrate the channel insights.
## Usage of App
After the project has been successfully set up and activated, users can interact with the Streamlit application through a web browser. Through the application's user-friendly interface, users can carry out the following tasks:
* Input a YouTube channel ID to fetch data for the specified channel.
* Gather information and keep it in a SQL data warehouse for numerous YouTube channels.
* Check out the uploaded channels' details.
* Utilise a variety of search tools to locate and retrieve data from a SQL database.
* Use these integrated features to perform analysis and visualisation of channel data.
## Method of use
Follow these steps,to use this project :
 1 Set up the streamlit package : pip install streamlit
 
 2.Run the Streamlit app: streamlit run app.py
 
 3.The web browser will launch instantly, allowing you to access it.

 4.Open your web browser if it doesn't start automatically. By starting a new tab and typing the following URL, you can visit it:http://localhost:8501
 
 5.Click the store data button after entering the channel ID in the text field on the Extract tab.
 
 6.The database will hold the channel's details.
 
 7.In the views tab,Select the questions that best fit your needs.
 
## Conclusion
 The goal of this project is to create an intuitive Streamlit application by using the Google API to retrieve comprehensive data from YouTube channels. After being retrieved, the data is kept in a SQL data 
 warehouse. The Streamlit app improves the overall data exploration experience by providing users with the ability to quickly search for channel details and execute table joins.
## References 
* YouTube Data API [https://developers.google.com/youtube/v3/getting-started]
* Streamlit App [https://docs.streamlit.io/library/api-reference]
* MySQL [https://pypi.org/project/pymysql/]
* Pandas [https://pandas.pydata.org/docs/]
* Plotly [https://plotly.com/python-api-reference/]
 


