"""Importe le GeoJSON ADM1 geoBoundaries Madagascar."""
import json, os, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connection
API='https://www.geoboundaries.org/api/current/gbOpen/MDG/ADM1/'

def main():
    local=Path(sys.argv[1]) if len(sys.argv)>1 else Path('data/MDG_ADM1.geojson')
    try:
        if len(sys.argv)>1 or local.exists():
            data=json.loads(local.read_text(encoding='utf-8'))
        else:
            with urllib.request.urlopen(API,timeout=30) as response: metadata=json.load(response)
            url=metadata.get('gjDownloadURL')
            if not url: raise ValueError('URL GeoJSON absente des métadonnées geoBoundaries')
            with urllib.request.urlopen(url,timeout=60) as response: data=json.load(response)
        features=data.get('features',[])
        if len(features)<20: raise ValueError(f'{len(features)} régions trouvées, au moins 20 attendues')
    except Exception as exc:
        raise SystemExit(f"Téléchargement/import geoBoundaries impossible : {exc}. Fournissez le GeoJSON ADM1 (23 régions) puis relancez : python scripts/import_regions.py chemin/vers/MDG_ADM1.geojson")
    imported=0
    with connection() as conn:
        with conn.transaction():
            for feature in features:
                props=feature.get('properties') or {}
                name=next((str(props[k]).strip() for k in ('shapeName','shapeNameEN','name','NAME_1','NAME') if props.get(k)),None)
                if not name: continue
                geom=feature.get('geometry')
                if not geom: continue
                # geoBoundaries supplies WGS84 GeoJSON; ST_Multi also accepts Polygon.
                conn.execute('''INSERT INTO region(nom,geom) VALUES(%s,ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)))
                    ON CONFLICT(nom) DO UPDATE SET geom=EXCLUDED.geom''',(name,json.dumps(geom)))
                imported+=1
            conn.execute('''UPDATE site s SET region_id=r.id FROM region r WHERE r.geom IS NOT NULL AND ST_Within(s.geom,r.geom)''')
    print(f'{imported} limites de régions importées; rattachement des sites effectué par ST_Within.')
if __name__=='__main__': main()
