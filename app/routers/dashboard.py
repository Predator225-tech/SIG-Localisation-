from fastapi import APIRouter
from app.db import connection
router=APIRouter()

@router.get('/dashboard')
def dashboard():
    with connection() as conn:
        k=conn.execute('''SELECT (SELECT COUNT(*) FROM site)::int AS sites,(SELECT COUNT(*) FROM ressource)::int AS ressources,
        (SELECT COUNT(*) FROM type_ressource)::int AS types,(SELECT COUNT(DISTINCT region_id) FROM site WHERE region_id IS NOT NULL)::int AS regions_avec_site,
        (SELECT COUNT(*) FROM region)::int AS regions_total''').fetchone()
        by_res=conn.execute('''SELECT r.code,r.nom,r.couleur,COUNT(s.id)::int AS nombre_sites FROM ressource r LEFT JOIN site s ON s.ressource_id=r.id GROUP BY r.id ORDER BY r.nom''').fetchall()
        by_reg=conn.execute('''SELECT r.nom,COUNT(s.id)::int AS nombre_sites FROM region r LEFT JOIN site s ON s.region_id=r.id GROUP BY r.id ORDER BY nombre_sites DESC,r.nom''').fetchall()
        all_sites=conn.execute('''SELECT s.id,s.nom,r.code AS ressource,r.nom AS ressource_nom,r.couleur,reg.nom AS region,p.annee,p.quantite,p.prix_unitaire,p.devise,r.unite,
        ST_X(s.geom)::float AS longitude,ST_Y(s.geom)::float AS latitude FROM site s JOIN ressource r ON r.id=s.ressource_id LEFT JOIN region reg ON reg.id=s.region_id LEFT JOIN LATERAL (SELECT annee,quantite,prix_unitaire,devise FROM production WHERE site_id=s.id ORDER BY annee DESC LIMIT 1) p ON true ORDER BY s.nom''').fetchall()
    return {'nombre_sites': k['sites'], 'ressources': k['ressources'], 'types': k['types'],
            'regions_avec_site': k['regions_avec_site'], 'regions_total': k['regions_total'],
            'sites_par_ressource': by_res, 'sites_par_region': by_reg, 'sites': all_sites}
