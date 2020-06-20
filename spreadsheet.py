import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('data.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Internship_Record').sheet1
pp = pprint.PrettyPrinter()
telemedicine = sheet.get_all_records()
#while(telemedicine)
headcode="<table><tr>"
tablebody="<tr>"
#to get all the values inside the file
sheet.get_all_values()
#to get exact row values in a second row (Since 1st row is the header)
row2=sheet.col_values(1)
cell = sheet.find("R100217030")
val=cell.row
rowHarsh=sheet.row_values(val)
count=len(rowHarsh)
for i in range (0,count):
    if(rowHarsh[i]!=""):
       # print(sheet.row_values(1)[i])
       # print(rowHarsh[i])
        headcode=headcode+''.join("<th>"+sheet.row_values(1)[i]+"</th>")
        tablebody=tablebody+''.join("<td>"+rowHarsh[i]+"</td>")
headcode+="</tr>"
tablebody+="</tr>"
print(headcode+tablebody)
try:
    cell = sheet.find('test')
    print('Yes')
except gspread.exceptions.CellNotFound:  # or except gspread.CellNotFound:
    print('No')


#print(rowHarsh)
#to get all the column values in the column 'place'
sheet.col_values(16)
#to extract a particular cell value
sheet.cell(1, 1).value
