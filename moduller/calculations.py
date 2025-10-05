import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, List
import pandas as pd
import pyinaturalist

"""
dışarıdan alınan pozisyon verileri ve koordinatlar falan
"""
STATE_BBOX: Dict[str, Dict[str, float]] = {
    "Alabama": {"nelat":35.008028, "nelng":-84.88908,  "swlat":30.223334, "swlng":-88.473227},
    "Alaska": {"nelat":71.365162, "nelng":179.77847,   "swlat":51.214183, "swlng":-179.148909},
    "Arizona": {"nelat":37.00426,  "nelng":-109.045223, "swlat":31.332177, "swlng":-114.81651},
    "Arkansas": {"nelat":36.4996,  "nelng":-89.644395,  "swlat":33.004106, "swlng":-94.617919},
    "California": {"nelat":42.009518,"nelng":-114.131211,"swlat":32.534156, "swlng":-124.409591},
    "Colorado": {"nelat":41.003444,"nelng":-102.041524, "swlat":36.992426, "swlng":-109.060253},
    "Connecticut": {"nelat":42.050587,"nelng":-71.786994, "swlat":40.980144, "swlng":-73.727775},
    "Delaware": {"nelat":39.839007,"nelng":-75.048939,  "swlat":38.451013, "swlng":-75.788658},
    "Florida": {"nelat":31.000888,"nelng":-80.031362,  "swlat":24.523096, "swlng":-87.634938},
    "Georgia": {"nelat":35.000659,"nelng":-80.839729,  "swlat":30.357851, "swlng":-85.605165},
    "Hawaii": {"nelat":28.402123,"nelng":-154.806773, "swlat":18.910361, "swlng":-178.334698},
    "Idaho": {"nelat":49.001146,"nelng":-111.043564,  "swlat":41.988057, "swlng":-117.243027},
    "Illinois": {"nelat":42.508481,"nelng":-87.494756,  "swlat":36.970298, "swlng":-91.513079},
    "Indiana": {"nelat":41.760592,"nelng":-84.784579,  "swlat":37.771742, "swlng":-88.09776},
    "Iowa": {"nelat":43.501196, "nelng":-90.140061,  "swlat":40.375501, "swlng":-96.639704},
    "Kansas": {"nelat":40.003162, "nelng":-94.588413,  "swlat":36.993016, "swlng":-102.051744},
    "Kentucky": {"nelat":39.147458,"nelng":-81.964971,  "swlat":36.497129, "swlng":-89.571509},
    "Louisiana": {"nelat":33.019457,"nelng":-88.817017,  "swlat":28.928609, "swlng":-94.043147},
    "Maine": {"nelat":47.459686, "nelng":-66.949895,  "swlat":42.977764, "swlng":-71.083924},
    "Maryland": {"nelat":39.723043,"nelng":-75.048939,  "swlat":37.911717, "swlng":-79.487651},
    "Massachusetts": {"nelat":42.886589,"nelng":-69.928393, "swlat":41.237964, "swlng":-73.508142},
    "Michigan": {"nelat":48.2388,  "nelng":-82.413474,  "swlat":41.696118, "swlng":-90.418136},
    "Minnesota": {"nelat":49.384358,"nelng":-89.491739,  "swlat":43.499356, "swlng":-97.239209},
    "Mississippi": {"nelat":34.996052,"nelng":-88.097888, "swlat":30.173943, "swlng":-91.655009},
    "Missouri": {"nelat":40.61364, "nelng":-89.098843,  "swlat":35.995683, "swlng":-95.774704},
    "Montana": {"nelat":49.00139,  "nelng":-104.039138, "swlat":44.358221, "swlng":-116.050003},
    "Nebraska": {"nelat":43.001708,"nelng":-95.30829,   "swlat":39.999998, "swlng":-104.053514},
    "Nevada": {"nelat":42.002207,"nelng":-114.039648, "swlat":35.001857, "swlng":-120.005746},
    "New Hampshire": {"nelat":45.305476,"nelng":-70.610621, "swlat":42.69699,  "swlng":-72.557247},
    "New Jersey": {"nelat":41.357423,"nelng":-73.893979, "swlat":38.928519, "swlng":-75.559614},
    "New Mexico": {"nelat":37.000232,"nelng":-103.001964,"swlat":31.332301, "swlng":-109.050173},
    "New York": {"nelat":40.9176, "nelng":-73.7004, "swlat":40.4774, "swlng":-74.2591},
    "North Carolina": {"nelat":36.588117,"nelng":-75.460621, "swlat":33.842316, "swlng":-84.321869},
    "North Dakota": {"nelat":49.000574,"nelng":-96.554507, "swlat":45.935054, "swlng":-104.0489},
    "Ohio": {"nelat":41.977523,"nelng":-80.518693,  "swlat":38.403202, "swlng":-84.820159},
    "Oklahoma": {"nelat":37.002206,"nelng":-94.430662,  "swlat":33.615833, "swlng":-103.002565},
    "Oregon": {"nelat":46.292035,"nelng":-116.463504, "swlat":41.991794, "swlng":-124.566244},
    "Pennsylvania": {"nelat":42.26986, "nelng":-74.689516, "swlat":39.7198,   "swlng":-80.519891},
    "Rhode Island": {"nelat":42.018798,"nelng":-71.12057,  "swlat":41.146339, "swlng":-71.862772},
    "South Carolina": {"nelat":35.215402,"nelng":-78.54203,  "swlat":32.0346,  "swlng":-83.35391},
    "South Dakota": {"nelat":45.94545, "nelng":-96.436589, "swlat":42.479635, "swlng":-104.057698},
    "Tennessee": {"nelat":36.678118,"nelng":-81.6469,   "swlat":34.982972, "swlng":-90.310298},
    "Texas": {"nelat":36.500704,"nelng":-93.508292,  "swlat":25.837377, "swlng":-106.645646},
    "Utah": {"nelat":42.001567,"nelng":-109.041058, "swlat":36.997968, "swlng":-114.052962},
    "Vermont": {"nelat":45.016659,"nelng":-71.464555,  "swlat":42.726853, "swlng":-73.43774},
    "Virginia": {"nelat":39.466012,"nelng":-75.242266,  "swlat":36.540738, "swlng":-83.675395},
    "Washington": {"nelat":49.002494,"nelng":-116.915989, "swlat":45.543541, "swlng":-124.763068},
    "West Virginia": {"nelat":40.638801,"nelng":-77.719519, "swlat":37.201483, "swlng":-82.644739},
    "Wisconsin": {"nelat":47.080621,"nelng":-86.805415,  "swlat":42.491983, "swlng":-92.888114},
    "Wyoming": {"nelat":45.005904,"nelng":-104.05216,  "swlat":40.994746, "swlng":-111.056888},
}

"""
Eşzamanlıda kullanılacak tek sayan foınksiyon
"""
def count_observations_bbox(tax_name: str, d1: str, d2: str, bbox: Dict[str, float]) -> int:
    try:
        resp = pyinaturalist.get_observations(
            tax_name=tax_name,
            d1=d1,
            d2=d2,
            photos=True,
            geo=True,
            geoprivacy='open',
            nelat=bbox["nelat"],
            nelng=bbox["nelng"],
            swlat=bbox["swlat"],
            swlng=bbox["swlng"],
            per_page=1,
            page=1,
            only_id=True, # payload azaltmak için sadece id 
        )
        total = int(resp.get("total_results", 0))
        return total
    except Exception:
        return 0

"""
Eşzamanlı olarak eyaletler için saınları al. max_workers kaç aktör olduığunu belirler
"""
def get_counts_parallel(tax_name: str, d1: str, d2: str, states: List[str], max_workers: int = 6):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_map = {
            ex.submit(count_observations_bbox, tax_name, d1, d2, STATE_BBOX[s]): s
            for s in states
        }
        for fut in as_completed(future_map):
            s = future_map[fut]
            cnt = 0 
            try:
                cnt = fut.result()
            except Exception:
                cnt = 0
            b = STATE_BBOX[s]
            results.append({
                "state": s,
                "count": cnt,
                "lat": b["clat"],
                "lon": b["clng"],
            })
            time.sleep(0.1) # limit yememek için ara ver
    df = pd.DataFrame(results)
    return df.sort_values("count", ascending=False)