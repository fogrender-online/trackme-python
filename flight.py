#!/usr/bin/env python3.7

import sys
import math
from datetime import datetime
import time
import wikipedia

from FlightRadar24.api import FlightRadar24API
fr_api = FlightRadar24API()


import flightradar24
flight_number = sys.argv[1]
fr = flightradar24.Api()

flight = fr.get_flight(flight_number)

now = time.time()

#print("Size of data: ", len(flight['result']['response']['data']))

#print(flight)

f_data = flight['result']['response']['data']
for f in f_data:
    
    live = f['status']['live']
    time_data = f['time']
    #print("Status: {} {}".format(live, f['status']['text']))
    
    
    if (live is True) or ('Estimated' in f['status']['text']):
       
       #print(f)
       
       flight_id = f['identification']['id']
       print("ID рейса: {}".format(flight_id))
       flight_details = fr_api.get_flight_details(flight_id)
       #print(flight_details['trail'][0])
       lat = flight_details['trail'][0]['lat']
       lng = flight_details['trail'][0]['lng']
       alt = int(int(flight_details['trail'][0]['alt']) * 0.3048)
       speed = int(int(flight_details['trail'][0]['spd']) * 1.852)
       
       print("Местоположение - в воздухе! Координаты: широта {} долгота {} высота {} м скорость {} км/час".format(lat, lng, alt, speed))
       
       destination_airport_name = f['airport']['destination']['name']
       origin_airport_name = f['airport']['origin']['name']
       
       estimated_arrival_date = time_data['estimated']['arrival']
       delta = int(estimated_arrival_date) - now
       delta_hours = delta//3600
       delta_mins = (delta % 3600) // 60
       f_time_hours = (now - int(time_data['real']['departure'])) // 3600
       f_time_mins = (now - int(time_data['real']['departure'])) % 3600 // 60
       
       lat = flight_details['trail'][0]['lat']
       lng = flight_details['trail'][0]['lng']
       
       #compose trail coordinates
       print("Length:", len(flight_details['trail']))
       trail = '&pl=w:4'
       p_count = len(flight_details['trail'])
       step = p_count/100
       print("Step:", step)
       for i in range(0, 99):
           p = flight_details['trail'][int(i*step)]
           #print(p)
           trail = trail + ','+str(p['lng'])+','+str(p['lat'])
           
       
       #print(trail)
       
       origin_airport_lat = f['airport']['origin']['position']['latitude']
       origin_airport_lng = f['airport']['origin']['position']['longitude']
       
       destination_airport_lat = f['airport']['destination']['position']['latitude']
       destination_airport_lng = f['airport']['destination']['position']['longitude']
       
       print("Вылетел из {} (Ш:{} Д:{})".format(origin_airport_name, origin_airport_lat, origin_airport_lng)) 
       print("Время в полете: {} ч. {} мин.".format(f_time_hours, f_time_mins))
       print("Планируемое время прилета в {} (Ш:{} Д:{}) {} (через {} ч. {} мин.)".format(destination_airport_name, destination_airport_lat, destination_airport_lng, estimated_arrival_date, int(delta_hours), int(delta_mins)))
       
       
       #https://static-maps.yandex.ru/1.x/?l=map&bbox=36.6,54.6~38.6,56.6
          
       travel_area = str(origin_airport_lng)+','+str(origin_airport_lat)+'~'+str(destination_airport_lng)+','+str(destination_airport_lat)
       airports_labels = str(origin_airport_lng)+','+str(origin_airport_lat)+',pmgns1~'+str(destination_airport_lng)+','+str(destination_airport_lat)+',pmgns2,'
       plane_label= str(lng)+','+str(lat)+',flag'
       area_size = '&size=400,400'
       map_layers='&l=map'
          
             
       
       wikipedia.set_lang("ru") 
       radius = 10000
       found_objects = wikipedia.geosearch(lat, lng, radius=radius, results=3)
       
       print("{} объектов в радиусе {} м: {}".format(len(found_objects), radius, found_objects))
       
       objects_labels = ""
       
       if found_objects:
          
          index = 1
          for obj in found_objects:
              print("Объект: ", obj)
              obj_page =  wikipedia.page(obj)
              print("URL: ", obj_page.url)
              print("Кол-во символов описания: ", len(obj_page.content))
              obj_lat = round(obj_page.coordinates[0],4)
              obj_lng = round(obj_page.coordinates[1],4)
              
              print("COORD: Ш:{}, Д:{}".format(obj_lat, obj_lng))
              
              print(index)
              
              objects_labels = objects_labels + '~'+str(obj_lng)+','+str(obj_lat)+',pmrds' + str(index)
              index = index + 1
          
          print(objects_labels)
          
          
       
          #print(wikipedia.page(found_objects[-1]).content)
          
       
          #print("Изображения: ", wikipedia.page(title).images)
                   
       
          #print(wikipedia.summary(found_objects[-1].title, sentences=5))
          #print(wikipedia.page(found_objects[-1]).categories)
       
    
       
      
            
       
       
    else:
         
         if 'Landed' in f['status']['text']:
             destination_airport_name = f['airport']['destination']['name']
             landing_time = f['status']['text'].split(' ')[1]
             #delta = now - landing_time
             delta_hours = '3'
             delta_mins = '45'
             
             print("Приземлился в {} в {} ({} ч. {} мин. назад)".format(destination_airport_name, landing_time, delta_hours, delta_mins))
         elif 'Scheduled' in f['status']['text']:
               origin_airport_name = f['airport']['origin']['name']
               delta = int(time_data['scheduled']['departure']) - now
               delta_hours = delta // 3600
               delta_mins = (delta % 3600) // 60
               print("Вылет из {} запланирован на {} (через {} ч. {} мин.)".format(origin_airport_name, time_data['scheduled']['departure'], int(delta_hours), int(delta_mins)))
      
    
full_trace_map_url = 'https://static-maps.yandex.ru/1.x/?' + map_layers+ '&bbox=' + travel_area + '&pt=' + airports_labels + objects_labels + plane_label + area_size + trail
local_map_url = 'https://static-maps.yandex.ru/1.x/?' + map_layers + '&pt=' + plane_label +  objects_labels + area_size

print("URL полной карты маршрута: {}".format(full_trace_map_url))

print("URL локальной карты маршрута: {}".format(local_map_url))
    
    
    
    #print("В воздухе: {}".format(status))
    
    
    #print("Время вылета (план): ", time_data['scheduled']['departure'])
    #print("Время прилета (план): ", time_data['scheduled']['arrival'])
    
    #print("Время вылета (факт): ", time_data['real']['departure'])
    #print("Время прилета (факт): ", time_data['real']['arrival'])
    
    #print("Время вылета (прогноз): ", time_data['estimated']['departure'])
    #print("Время прилета (прогноз): ", time_data['estimated']['arrival'])
    
    
#print(flight['result']['response']['data'][0])

exit()

