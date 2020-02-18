from django.shortcuts import render
from django.http import HttpResponse
import requests

from isodate import parse_duration
from django.conf.urls.static import settings

from datetime import datetime
from dateutil import relativedelta
from dateutil import parser

from math import floor, log

from .models import Youtube_Search_Api


# Create your views here.


def home(request):
    if request.method == "POST":
        videos = []
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
                'part' : 'snippet',
                'q' : request.POST['search'],
                'key' : settings.YOUTUBE_API_KEY,
                'maxResults' : 50,
                'type' : 'video'
            }

        r = requests.get(search_url, params=search_params)

        results_search = r.json()['items']

        # print(results_search)
        video_ids = []
        for result in results_search:
            video_ids.append(result['id']['videoId'])

        video_params = {
                'key' : settings.YOUTUBE_API_KEY,
                'part' : 'snippet,contentDetails,statistics',
                'id' : ','.join(video_ids),
                'maxResults' : 50
            }

        r = requests.get(video_url, params=video_params)

        results_video = r.json()['items']

        for result in results_video:
                # Convert view Count to abbreviated String
                units = ['', 'K', 'M', 'B', 'T', 'P']
                k = 1000.0
                magnitude = int(floor(log(int(result['statistics']['viewCount']), k)))
                view_count = '%.1f%s' % (int(result['statistics']['viewCount']) / k**magnitude, units[magnitude])
                
            

                # calculate datetime difference
                date_time1 = datetime.now()
                date_time2 = parser.parse(result['snippet']['publishedAt'], ignoretz=True) 
                diff = relativedelta.relativedelta(date_time1, date_time2)
                # print('{} years ago'.format(diff.years))
                # print(date_time1, date_time2)

                video_data = {
                    'title' : result['snippet']['title'],
                    'description': result['snippet']['description'],
                    'id' : result['id'],
                    'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
                    'duration' : int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                    'thumbnail' : result['snippet']['thumbnails']['high']['url'],
                    'createdAt': result['snippet']['publishedAt'],
                    'date': '{} years {} months ago'.format(diff.years, diff.months),
                    'viewCount': result['statistics']['viewCount'],
                    'view_count': view_count
                }

                # init model
                data_model = Youtube_Search_Api()

                # save result to database
                data_model.title = video_data['title']
                data_model.description = video_data['description']
                data_model.search_id = video_data['id']
                data_model.search_video_url = video_data['url']
                data_model.duration = video_data['duration']
                data_model.thumbnail = video_data['thumbnail']
                data_model.date = video_data['date']
                data_model.view_count = video_data['view_count']

                # save model
                data_model.save()

                

                videos.append(video_data)
                

       

        context = {
            'videos': videos,
            'results_video': results_video
        }
        return render(request, 'youtube_api/index.html', context)

    else:
        return render(request, 'youtube_api/index.html', {})



    


    