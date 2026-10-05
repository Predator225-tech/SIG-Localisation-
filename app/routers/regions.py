from fastapi import APIRouter
from app.db import connection
router=APIRouter()

@router.get('/regions')
def regions():
    with connection() as conn:
        rows=conn.execute('''SELECT r.id,r.nom,COUNT(s.id)::int AS nombre_sites,ST_AsGeoJSON(r.geom)::json AS geometry
        FROM region r LEFT JOIN site s ON s.region_id=r.id GROUP BY r.id ORDER BY r.nom''').fetchall()
    return {'type':'FeatureCollection','features':[{'type':'Feature','id':r['id'],'geometry':r['geometry'],'properties':{'nom':r['nom'],'nombre_sites':r['nombre_sites']}} for r in rows]}
