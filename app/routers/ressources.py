from fastapi import APIRouter, HTTPException, Query
from app.db import connection
router = APIRouter()

@router.get('/health')
def health():
    try:
        with connection() as conn:
            conn.execute('SELECT 1').fetchone()
        return {'status':'ok','database':'ok'}
    except Exception as exc:
        raise HTTPException(503, detail='Base de données indisponible') from exc

@router.get('/types')
def types():
    with connection() as conn:
        return conn.execute('SELECT code, nom FROM type_ressource ORDER BY id').fetchall()

@router.get('/ressources')
def ressources(type: str | None = Query(default=None, pattern=r'^[a-z0-9_-]{1,30}$')):
    with connection() as conn:
        rows = conn.execute('''SELECT r.code,r.nom,r.couleur,r.unite,t.code AS type,COUNT(s.id)::int AS nombre_sites
          FROM ressource r JOIN type_ressource t ON t.id=r.type_id LEFT JOIN site s ON s.ressource_id=r.id
          WHERE (%s::text IS NULL OR t.code=%s) GROUP BY r.id,t.code ORDER BY t.code,r.nom''',(type,type)).fetchall()
    if type and not rows:
        with connection() as conn:
            exists=conn.execute('SELECT 1 FROM type_ressource WHERE code=%s',(type,)).fetchone()
        if not exists: raise HTTPException(404, detail='Type de ressource introuvable')
    return rows
