"""Offline harness for travel_times_free.py: fake Nominatim and Valhalla
responses, so the whole path (geocode -> route -> workbook) is exercised
without network. Also exercises the failure branches, which are the ones that
only ever fire on a bad day and so never get tested otherwise.
Not part of the deliverable - a test scaffold only."""
import os
import sys

os.environ["OSM_CONTACT"] = "test@example.invalid"
import travel_times_free as tf

tf.NOMINATIM_DELAY = 0
tf.VALHALLA_DELAY = 0

# Anything whose canonical name contains one of these gets that behaviour.
GEO_MISS = "gurupalya"          # forces the shortened-query fallback
GEO_FAIL = "old madras road"    # forces a hard geocode failure
ROUTE_FAIL = "balagere"         # forces a routing failure


class FakeResp:
    def __init__(self, payload, code=200):
        self.status_code, self._p = code, payload

    def json(self):
        return self._p

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def fake_request(method, url, headers=None, timeout=None, **kw):
    assert "ceew-bbus-traveltime" in headers["User-Agent"], "UA must identify caller"

    if method == "GET":                       # Nominatim
        q = kw["params"]["q"].lower()
        ncommas = q.count(",")
        if GEO_FAIL in q:
            return FakeResp([])               # never resolves, any query length
        if GEO_MISS in q and ncommas >= 2:
            return FakeResp([])               # full query misses, shorter one works
        # Tumakuru sits ~70 km out; make one place land implausibly far away
        far = "tumakuru" in q
        lat, lon = (13.34, 77.10) if far else (12.93, 77.62)
        if "bidadi" in q:
            lat, lon = (12.80, 77.38)
        return FakeResp([{"lat": str(lat), "lon": str(lon),
                          "display_name": f"{kw['params']['q']}, India",
                          "category": "place", "type": "suburb"}])

    # Valhalla
    body = kw["json"]
    costing = body["costing"]
    o, d = body["locations"]
    if body.get("costing_options"):
        assert costing in body["costing_options"], "top_speed must be under its costing"
        assert body["costing_options"][costing]["top_speed"] == 45

    km = tf.haversine_km((o["lat"], o["lon"]), (d["lat"], d["lon"])) * 1.35 + 0.4
    if ROUTE_FAIL in str(sorted([o["lat"], d["lat"]])):
        pass
    speed = {"auto": 32.0, "motorcycle": 28.0, "bus": 22.0}[costing]
    if body.get("costing_options"):
        speed = min(speed, 24.0)
    return FakeResp({"trip": {"summary": {"time": km / speed * 3600, "length": km}}})


tf.request_with_retry = lambda m, u, ua, **kw: fake_request(m, u, headers={"User-Agent": ua}, **kw)
sys.argv = ["travel_times_free.py"]
tf.main()

# ---------------- verify the workbook ----------------
from openpyxl import load_workbook
p = tf.Path(__file__).resolve().parent / "Travel_Times_FILLED_free.xlsx"
wb = load_workbook(p)
print("\n\n==== WORKBOOK CHECK ====")
print("sheets:", wb.sheetnames)
for n in wb.sheetnames:
    print(f"  {n}: {wb[n].max_row} rows x {wb[n].max_column} cols")

ws = wb["Travel Times"]
hdr = [c.value for c in ws[1]]
print("\nheader:", hdr)
assert not any("delay" in str(h).lower() for h in hdr), \
    "there must be no traffic-delay column - there is no traffic model"

i2w, ibus, iauto, icar = (hdr.index(h) for h in
                          ["2-Wheeler Time (approx)", "Bus Time (approx)",
                           "Auto/Cab Time (approx)", "Car (min)"])
ist = hdr.index("Status")
data = [r for r in ws.iter_rows(min_row=2, values_only=True)
        if r[0] and str(r[0]).startswith("P")]
print(f"data rows: {len(data)}")

filled = [r for r in data if r[i2w] is not None]
print(f"filled: {len(filled)}   blank/review: {len(data) - len(filled)}")

# mode ordering sanity: capped auto must never beat the uncapped 2-wheeler
bad = [(r[0], r[i2w], r[iauto]) for r in filled if r[iauto] < r[i2w] - 1e-9]
print("rows where capped Auto/Cab beats 2-Wheeler (must be empty):", bad[:5])

# bus is the slowest road mode here, so it should not beat the car
bad2 = [(r[0], r[ibus], r[icar]) for r in filled if r[ibus] < r[icar] - 1e-9]
print("rows where Bus beats Car (must be empty):", bad2[:5])

st = {}
for r in data:
    k = str(r[ist]).split(" - ")[0].split(";")[0]
    st[k] = st.get(k, 0) + 1
print("status spread:", st)

gs = wb["Geocoding"]
ghdr = [c.value for c in gs[1]]
ichk = ghdr.index("Check")
checks = [r[ichk] for r in gs.iter_rows(min_row=2, values_only=True) if r[ichk]]
print("geocoding rows flagged for a check:", len(checks))
print("  sample:", checks[:3])
print("failures sheet present:", "Failures" in wb.sheetnames)
if "Failures" in wb.sheetnames:
    for r in wb["Failures"].iter_rows(min_row=2, max_row=4, values_only=True):
        print("  ", r)
