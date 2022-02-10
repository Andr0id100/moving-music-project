import pygsheets 

client = pygsheets.authorize(service_file="credentials.json")
sh = client.open('test')
wks = sh.sheet1 

wks.update_value("A1", "different again")

