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

#print("Flights list:", flights)


#filtered_flights = fr_api.get_flights(flight = flight)

all_flights = fr_api.get_flights()

flight = None

print("Plains count:", len(all_flights))

f_num = sys.argv[1]

print("Flight number requested:", f_num)

for f in all_flights:
    #print(f)
    #if not f.number == "N/A":
     #  print(f.number)
    #print(f.number)
    if f.number == f_num: 
       flight = f
       break         

if (flight is None):
   print("Рейс {} не найден среди находящихся в воздухе".format(f_num))
   
else:
    print("Flight data:", flight)
    # print("Flight ID:", flight.id)
    print("icao_24bit:", flight.icao_24bit)
    print("latitude:", flight.latitude)
    print("longitude:", flight.longitude)
    # # print("heading:", flight.heading)
    print("altitude:", flight.altitude)

    print("ground_speed:", flight.ground_speed)

    # # print("squawk:", flight.squawk)
    # # print("aircraft_code:", flight.aircraft_code)
    print("registration:", flight.registration)
    print("time:", flight.time/3600)

    print("origin_airport_iata:", flight.origin_airport_iata)
    print("destination_airport_iata:", flight.destination_airport_iata)
    print("number:", flight.number)
    # print("airline_iata:", flight.airline_iata)
    print("on_ground:", flight.on_ground)
    # print("vertical_speed:", flight.vertical_speed)
    print("callsign:", flight.callsign)
    # print("airline_icao:", flight.airline_icao)







#details = fr_api.get_flight_details('280dfde1')

#print("Details:", details)



#print("Airline:", details)

# dropbox_ffmpeg_folder = "/ffmpeg"
# yd_token = "AgAAAAAAAXijAAX_BhpxOzPhgkDejKCZMiH-o5c"

# #jira = JIRA(options = {'server': "http://127.0.0.1:8080"}, basic_auth = {"admin", "123"})

# #ticket = jira.issue("FOG-1730")
# #for attachment in ticket.fields.attachment:
 # #   if attachment.filename ==  'meta_source_' + str(ticket) +'.json':
 # #      meta_data = json.loads(attachment.get())
 # #      break
       
# #print(meta_data["streams"][0]["display_aspect_ratio"])


# #url = '"ftp://91.122.30.115/Video/%D0%93%D0%BE%D1%80%D0%B4%D0%BE%D1%81%D1%82%D1%8C%20%D0%B8%20%D0%BF%D1%80%D0%B5%D0%B4%D1%83%D0%B1%D0%B5%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5%20(Pride%20&%20Prejudice).avi"'
# #url1 = "https://www.dropbox.com/s/diilrfx6mb8lfb8/%D0%BC%D0%B0%D0%BC%D0%B0_%D0%B4%D0%BB%D1%8F_%D0%BC%D0%B0%D0%BC%D0%BE%D0%BD%D1%82%D0%B5%D0%BD%D0%BA%D0%B0.avi?dl=1"
# #command = ['curl', '-sLI', url1]
# #command = ['curl', '-sLI', url1, "|", "grep", "a"]
# #size = subprocess.check_output(command)

# #print(size)


# #DROPBOX_TOKEN = "xeT2yCF_5QAAAAAAAAAAEqfqblDeqX0gJ0Ium36uVbu_SeylPINlkbOKBhJpju3d"
# #url = 'https://yadi.sk/d/ztqqiLPiOx3D2A'

# #name = "Мама для мамонтенка (convert-video-online.com).avi"
# #file_ext = name.split(".")[-1]
# #print(file_ext)
# #print(name.replace("." + file_ext, ""))
# #print(transliterate(name))

# #yd documentation: https://readthedocs.org/projects/yadisk-ru/downloads/pdf/stable/

# # yd = yadisk.YaDisk(yd_token)
# # meta = yd.get_public_meta(url)
# # source_file_name = meta['name']
# # print(meta)
# # print("File info: type =" +  meta['type'] + " name = " + meta['name'] + " size = " + str(meta['size']) + " url = " + meta['file'])
# # source_file_extension = os.path.splitext(source_file_name)[1]
# # print("Extension:" + source_file_extension)
# # if (source_file_extension == '.zip' and meta['media_type'] == 'compressed'):
    # # print("ZIP archive!!")

# #type, name, size, url
# #if yd.check_token() == True:
   
   
 # #  print(yd.get_public_meta(url))

# #else:
 # #    print("Problem with ya token check")   
   # #print(list(y.listdir("/some/path")))
   # # download_link = ya.   
                           # # value_from_ticket = yd.get_public_download_link(value_from_ticket)
                           # # source_url = value_from_ticket
                       # # except BaseException:
                              # # value_from_ticket = "!!! Yandex download link not generated !!!"
                    # # else:
                         # # value_from_ticket = "!!! Yandex token is not valid !!!"



# #jira = JIRA(options = {'server': "http://127.0.0.1:8080"}, basic_auth = {"admin", "123"})

# #ticket = jira.issue("FOG-1706")
# #if "estimation" in ticket.fields.labels:
# #   print(ticket.fields.labels)

# # batch_by_files = str(ticket.fields.customfield_11201)
# # print("Batch by files:" + batch_by_files)
# # if batch_by_files == "Yes": #just folder
   # # file_path = "/" + str(ticket) + "_" + "388801"
# # else: #single archive file
    # # file_name = str(self.ticket.fields.customfield_11200).split(".")[0] + "_f.zip"
    # # print("Result file name is:" + file_name)
    # # file_path = "/" + str(ticket) + "_" + "388801" + "/" + file_name
    # # print("File path is: " + file_path)
        
# #dbx = dropbox.Dropbox(DROPBOX_TOKEN)
# #shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_ffmpeg_folder + file_path)
# #metadata = dbx.sharing_get_shared_link_metadata("https://www.dropbox.com/s/jv2hv0y2eeqx3pv/cave.mp4?dl=0")



# #download_link = shared_link_metadata.url.replace("dl=0", "dl=1")
# #print(metadata.name)

# #current_time = int(time())
# #print("Current")

# #command = ["/home/danik/Dockers/ffmpeg_roten/dropbox_uploader.sh", "-f", "/home/danik/Dockers/ffmpeg_roten/.dropbox_uploader"]
# #print(command)      
# #subprocess.call(command)




# # s_tag = "%"
# # e_tag = "%"
# # task_body = '#META test "%streams_codec_name%"'

# # while task_body.partition(s_tag)[2].partition(e_tag)[0] != "":
      # # meta_field_name = task_body.partition(s_tag)[2].partition(e_tag)[0]
      # # print("meta_field_name is {}".format(meta_field_name))
      # # value_from_meta = "META"
      # # task_body = task_body.replace(s_tag + meta_field_name + e_tag, value_from_meta)
      
      
      
      
      
      
      
      
      
      
      # # Переменные
# # • antivirus_status – str, статус проверки антивирусом
# # 28 Глава 2. Документация
# # YaDisk Documentation, Выпуск 1.2.13
# # • file – str, URL для скачивания файла
# # • size – int, размер файла
# # • public_key – str, публичный ключ
# # • sha256 – str, SHA256 хэш
# # • md5 – str, MD5 хэш
# # • embedded – PublicResourceObject , список вложенных ресурсов
# # • name – str, имя файла
# # • exif – EXIFObject , метаданные EXIF
# # • resource_id – str, идентификатор ресурса
# # • custom_properties – dict, пользовательские свойства ресурса
# # • public_url – str, публичный URL
# # • share – ShareInfoObject , информация об общей папке
# # • modified – datetime.datetime, дата последнего изменения
# # • created – datetime.datetime, дата создания
# # • photoslice_time – datetime.datetime, дата создания фото/видео
# # • mime_type – str, MIME-тип
# # • path – str, путь к ресурсу
# # • preview – str, URL превью файла
# # • comment_ids – CommentIDsObject , идентификаторы комментариев
# # • type – str, тип («file» или «dir»)
# # • media_type – str, тип файла, согласно Яндекс.Диску
# # • revision – int, ревизия Яндекс.Диска на момент последнего изменения
# # • view_count – int, количество просмотров публичного ресурса
# # • owner – UserPublicInfoObject , владелец публичного ресурса

# # print(task_body)





# # def generate_json_meta_by_url(url, json_meta_filename):
    # # command =["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", url]
    # # with open(json_meta_filename, "w") as outfile:
         # # subprocess.call(command, stdout=outfile)

 




# # for attachment in ticket.fields.attachment:
    # # print("Attachment filename is {}".format(attachment.filename))
    # # # if attachment.filename ==  output_file + '.json':
       # # # meta_data = json.loads(attachment.get())
       # # # result_size = int(meta_data['format']['size'])/1024/1024/1024
       # # # print ("Result size is {0:.2f}".format(result_size))
    
    
# #generate_json_meta_by_url('https://www.dropbox.com/s/3hhsl5xhywyqmue/Aria-AntiSPID.mpg?dl=1', 'json_meta_filename.json')


# task_logs = "step 17072900, will finish Fri Nov  6 16:27:46 2020"
# current_progress_log = re.findall('step \d+, will finish', task_logs) #step 17072900, will finish Fri Nov  6 16:27:46 2020


# print(current_progress_log)
# if current_progress_log:
   # log_data = current_progress_log[-1].split(" ")[1].replace(",", "")
   # print(log_data)
   # progress = int(log_data)
   # print(progress)
  




# # #if upload_progress_log:
   # # log_data = upload_progress_log[-1].split("Uploading chunk ")[1].split(" ")
   # # print("Upload progress log data: {}".format(log_data))
   # # uploaded_chunks = int(str(log_data[0]))
   # # total_chunks = int(str(log_data[2]))
   # # pg = 100 * uploaded_chunks/total_chunks
   # # upload_progress = "{0:.1f}%".format(pg)
   # # print("Upload progress is {}".format(upload_progress))
           
# # else:
    # # upload_progress_log = re.findall('\#{1,}\ {1,}\d{1,3}.\d{1,1}%', task_logs) ##     100.0%
    # # if upload_progress_log:
       # # log_data = upload_progress_log[-1].split(" ")[-1]
       # # print("Upload progress log data: {}".format(log_data))
       # # upload_progress = log_data
       # # print("Upload progress is {}".format(upload_progress))
        



# # smtp_server = 'smtp.yandex.ru'
# # smtp_port = 587
# # sender = 'vologdin'
# # smtp_pasword = 'Elbrusdanilin75'
# # mail_lib = smtplib.SMTP(smtp_server, smtp_port)
# # mail_lib.starttls()
# # mail_lib.login(sender, smtp_pasword)
    # # # В случае если функции передан не список с получателями
    # # # а обычную строку
# # #if isinstance(to, str):
# # #   to = ','.join(to)
# # message = 'Преобразоание файла завершено'
# # msg = 'From: %s\r\nTo: %s\r\nContent-Type: text/html; charset="utf-8"\r\nSubject: %s\r\n\r\n' % ('ffmpeg-online', 'appserver@ya.ru', 'Transcoding completed')
# # msg += message
# # mail_lib.sendmail('appserver@ya.ru', 'appserver@ya.ru', msg.encode('utf8'))
# # mail_lib.quit()









# #ffmpeg_folder = "/ffmpeg/TEST_TICKET_KEY_TEST_DEAL_ID/gost.mp4"
# #dropbox_token = "xeT2yCF_5QAAAAAAAAAAEqfqblDeqX0gJ0Ium36uVbu_SeylPINlkbOKBhJpju3d"

# #dbx = dropbox.Dropbox(dropbox_token)
# #shared_link_metadata = dbx.sharing_create_shared_link_with_settings(ffmpeg_folder)
# #print(shared_link_metadata.url)


# #print("Content of /ffmpeg is:{}".format(dbx.files_list_folder(ffmpeg_folder)))
# #dbx.users_get_current_account()






# #log = "2019-10-31T07:08:54.972167725Z   Duration: 00:01:38.32, start: 0.000000, bitrate: 20171 kb/s"
# #search_result = re.search(r'Duration: \d+:\d{2,2}:\d{2,2}.\d{2,2}', log)
# #duration = search_result[0].split(" ")[1]
# #total_frames = 25 * (int(duration.split(":")[0]) * 3600 +  int(duration.split(":")[1]) * 60 + round(float(duration.split(":")[2])))
# #print(total_frames)
# #total_frames = int(search_result[0].split(" ")[1])
                 
# #print("OpenCV version is {}".format(cv2.__version__))
# #print (cv2.getBuildInformation()) 

# # start_time = dt.datetime(time.mktime('2019-10-18T09:16:42Z'))
# # end_time = dt.datetime(time.mktime('2019-10-18T09:16:52Z'))
# # duration = end_time - end_time
# # print(duration) 

# #jira = JIRA(options = {'server': "http://127.0.0.1:8080"}, basic_auth = {"admin", "123"})

# #ticket = jira.issue("FOG-89")

# #rub_snm_rate =  0.8
# #usd_snm_rate =  0.01312898
# #spent_total_fiat = str("{0:.2f}".format(2.55456564 * usd_snm_rate)) + " USD / " + str("{0:.2f}".format(2.55456564 * rub_snm_rate)) + " RUB"  
# #print(spent_total_fiat)


# # #print("Ticket is {}".format(ticket))
# # logs = "Total Speed: 177.084 Mh/s" 

# # #getattr(ticket.fields, "summary")
# # print("Log is {}".format(logs))

# # progress_line = re.findall(r'Total Speed: \d+.\d+ Mh/s', logs)
# # progress = progress_line[0].split(" ")[2] + " " + progress_line[0].split(" ")[3]

# # if progress: 
   # # print("Progress line is: {}".format(progress))
   # # print("\n Matches count is {}.".format(len(progress_line)))
# # else:
     # # print("Not found")


# # # s_tag = "$"
# # # e_tag = "$"
# # # task_body = ' WALLET: "9D15d1699398Ace9bA6eb1e3432736bf35098d40.$summary$"'
# # # while task_body.partition(s_tag)[2] != "":
      # # # jira_field_name = task_body.partition(s_tag)[2].partition(e_tag)[0]
      # # # print("Field name is {}".format(jira_field_name))
      # # # task_body = task_body.replace(s_tag + jira_field_name + e_tag, "TTTTTTT")
