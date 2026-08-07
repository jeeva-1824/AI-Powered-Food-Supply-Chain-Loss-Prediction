import urllib.request
import json

def test_osrm(src_lat, src_lon, dst_lat, dst_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{src_lon},{src_lat};{dst_lon},{dst_lat}?overview=full&amp;alternatives=true&amp;steps=true"
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.loads(resp.read().decode())
            print("OSRM Success!")
            print(f"Distance: {data['routes'][0]['distance']/1000:.1f}km")
            print(f"Duration: {data['routes'][0]['duration']/60:.0f}min")
            print("Geometry sample:", data['routes'][0]['geometry'][:100])
            return True
    except Exception as e:
        print(f"OSRM Error: {e}")
        return False

# Test India routes
test_osrm(19.076, 72.877, 28.613, 77.209)
