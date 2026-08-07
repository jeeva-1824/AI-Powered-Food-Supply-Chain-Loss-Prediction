import requests
s = requests.Session()
base='http://127.0.0.1:5000'
# Login as admin
r = s.post(base+'/login', data={'email':'foodstopage03@gmail.com','password':'food@1234'}, allow_redirects=True)
print('Login status', r.status_code)
# Post a predict
payload = {'mode':'manual','temperature':'25','humidity':'60','rainfall':'0','transit_time':'12','storage_duration':'2','category':'Fruits','food_type':'Apple','src_lat':'19.0760','src_lon':'72.8777','dst_lat':'28.6139','dst_lon':'77.2090'}
r = s.post(base+'/predict', data=payload, allow_redirects=True)
print('Predict POST status', r.status_code)
# Fetch map
r = s.get(base+'/map')
print('/map status', r.status_code)
# Quick check for waypoints or coords in returned HTML
has_waypoints = 'waypoints' in r.text or 'coords' in r.text
print('Has waypoints/coords in map HTML?', has_waypoints)
# print small snippet
start = r.text.find('routes_json')
print('snippet:', r.text[start:start+400])
