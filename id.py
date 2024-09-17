import pandas as pd
import csv


gameid=0
with open('./static/steamcmd_appid.csv') as file_obj:
                reader_obj = csv.reader(file_obj,delimiter=';')
                for row in reader_obj:
                    print(row[0])
print(gameid)
