# villupuram_buses.py
import folium
import random, math, time
from datetime import datetime
import os

# Map center: Villupuram
CENTER = (11.9396, 79.4924)

# 5 sample routes (each route is a list of points)
routes = {
    "Bus 1": [(11.9410,79.4910),(11.9430,79.4930),(11.9450,79.4950),(11.9470,79.4970)],
    "Bus 2": [(11.9380,79.4880),(11.9395,79.4900),(11.9415,79.4920),(11.9435,79.4940)],
    "Bus 3": [(11.9360,79.4950),(11.9375,79.4965),(11.9390,79.4980),(11.9410,79.4995)],
    "Bus 4": [(11.9400,79.5000),(11.9410,79.4975),(11.9420,79.4950),(11.9430,79.4930)],
    "Bus 5": [(11.9345,79.4925),(11.9360,79.4935),(11.9375,79.4945),(11.9390,79.4955)],
}

crowd_states = [("Low 🟢","green"), ("Medium 🟡","orange"), ("High 🔴","red")]

def haversine_km(p1,p2):
    R=6371.0
    lat1,lon1 = p1; lat2,lon2 = p2
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*(math.sin(dlambda/2)**2)
    return 2*R*math.asin(math.sqrt(a))

def make_map(step, filename="map.html", refresh_seconds=15):
    m = folium.Map(location=CENTER, zoom_start=14, control_scale=True)
    sample_stop = (11.9396,79.4924)  # reference stop to compute ETA (center)
    for idx,(bus, pts) in enumerate(routes.items(), start=1):
        i = (step + idx) % len(pts)   # offset each bus so they are staggered
        lat,lng = pts[i]
        crowd_label, color = random.choice(crowd_states)
        # simple artificial ETA: distance to sample_stop / avg speed
        dist_km = haversine_km((lat,lng), sample_stop)
        speed_kmph = random.uniform(15, 30)  # random speed so ETAs vary
        eta_min = max(1, int((dist_km / speed_kmph) * 60))
        popup_html = (
            f"<b>{bus}</b><br>"
            f"Crowd: {crowd_label}<br>"
            f"ETA: {eta_min} min<br>"
            f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        )
        folium.CircleMarker(
            location=(lat,lng),
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)

    # Save the map
    m.save(filename)

    # Inject auto-refresh meta into <head> so browser reloads automatically
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html = f.read()
        if "<meta http-equiv='refresh'" not in html:
            html = html.replace(
                "<head>",
                f"<head>\n    <meta http-equiv='refresh' content='{refresh_seconds}'>\n"
            )
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
    except Exception as e:
        print("Warning: couldn't inject meta-refresh:", e)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] {filename} updated (step {step})")

if __name__ == "__main__":
    step = 0
    # Make sure working directory exists and we write to the script folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        while True:
            make_map(step)
            step += 1
            time.sleep(15)   # regenerate every 5 seconds
    except KeyboardInterrupt:
        print("\nStopped by user. map.html was written to this folder.")
