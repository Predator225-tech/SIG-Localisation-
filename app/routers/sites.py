from fastapi import APIRouter, HTTPException, Query
from app.db import connection
router=APIRouter()

@router.get('/sites')
def list_sites(ressources: str | None = Query(default=None, max_length=300, pattern=r'^[a-z0-9_, -]*$')):
    codes=[x.strip() for x in ressources.split(',') if x.strip()] if ressources else None
    with connection() as conn:
        rows=conn.execute('''SELECT s.id,s.nom,s.description,r.code AS ressource,r.nom AS ressource_nom,r.couleur,reg.nom AS region,
          p.annee,p.quantite,p.prix_unitaire,p.devise,r.unite,ST_AsGeoJSON(s.geom)::json AS geometry
          FROM site s JOIN ressource r ON r.id=s.ressource_id LEFT JOIN region reg ON reg.id=s.region_id
          LEFT JOIN LATERAL (SELECT annee,quantite,prix_unitaire,devise FROM production WHERE site_id=s.id ORDER BY annee DESC LIMIT 1) p ON true
          WHERE (%s::text[] IS NULL OR r.code=ANY(%s)) ORDER BY s.nom''',(codes,codes)).fetchall()
    return {'type':'FeatureCollection','features':[{'type':'Feature','id':x['id'],'geometry':x['geometry'],'properties':{k:v for k,v in x.items() if k not in ('id','geometry')}} for x in rows]}

@router.get('/sites/{site_id}')
def site_detail(site_id: int):
    with connection() as conn:
        item=conn.execute('''SELECT s.id,s.nom,s.description,r.code AS ressource,r.nom AS ressource_nom,r.couleur,r.unite,reg.nom AS region,ST_AsGeoJSON(s.geom)::json AS geometry
          FROM site s JOIN ressource r ON r.id=s.ressource_id LEFT JOIN region reg ON reg.id=s.region_id WHERE s.id=%s''',(site_id,)).fetchone()
        if not item: raise HTTPException(404,detail='Site introuvable')
        history=conn.execute('SELECT annee,quantite,prix_unitaire,devise FROM production WHERE site_id=%s ORDER BY annee',(site_id,)).fetchall()
    return {'site':item,'productions':history}
