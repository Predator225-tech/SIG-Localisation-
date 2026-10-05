from contextlib import contextmanager
from fastapi import HTTPException
import pytest
import app.routers.ressources as ressources_api
import app.routers.sites as sites_api
import app.routers.regions as regions_api
import app.routers.dashboard as dashboard_api

class Result:
    def __init__(self, rows): self.rows = rows
    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows

class FakeConnection:
    def execute(self, sql, params=None):
        if 'SELECT 1 FROM type_ressource' in sql:
            return Result([] if params and params[0] == 'inconnu' else [{'ok': 1}])
        if 'SELECT 1' in sql: return Result([{'ok': 1}])
        if 'SELECT (SELECT COUNT(*)' in sql:
            return Result([{'sites': 1, 'ressources': 8, 'types': 3, 'regions_avec_site': 1, 'regions_total': 23}])
        if 'FROM type_ressource' in sql and 'JOIN ressource' not in sql:
            return Result([{'code': 'minier', 'nom': 'Minier'}])
        if 'FROM ressource r JOIN type_ressource' in sql:
            if params and params[0] == 'inconnu': return Result([])
            return Result([{'code': 'or', 'nom': 'Or', 'couleur': '#d9a400', 'unite': 'kg', 'type': 'minier', 'nombre_sites': 1}])
        if 'WHERE s.id=%s' in sql:
            if params and params[0] != 1: return Result([])
            return Result([{'id': 1, 'nom': 'Ilakaka', 'description': None, 'ressource': 'saphir', 'ressource_nom': 'Saphir', 'couleur': '#2f5fc4', 'unite': 'carat', 'region': 'Ihorombe', 'geometry': {'type': 'Point', 'coordinates': [45.2, -22.7]}}])
        if 'FROM site s JOIN ressource r' in sql and 'ST_AsGeoJSON' in sql:
            return Result([{'id': 1, 'nom': 'Ilakaka', 'description': None, 'ressource': 'saphir', 'ressource_nom': 'Saphir', 'couleur': '#2f5fc4', 'region': 'Ihorombe', 'annee': 2025, 'quantite': 100, 'prix_unitaire': 500, 'devise': 'USD', 'unite': 'carat', 'geometry': {'type': 'Point', 'coordinates': [45.2, -22.7]}}])
        if 'FROM production WHERE site_id=%s' in sql:
            return Result([{'annee': 2025, 'quantite': 100, 'prix_unitaire': 500, 'devise': 'USD'}])
        if 'FROM region r LEFT JOIN site' in sql:
            return Result([{'id': 1, 'nom': 'Ihorombe', 'nombre_sites': 1, 'geometry': {'type': 'Polygon', 'coordinates': []}}])
        if 'SELECT r.code,r.nom,r.couleur,COUNT(s.id)' in sql:
            return Result([{'code': 'saphir', 'nom': 'Saphir', 'couleur': '#2f5fc4', 'nombre_sites': 1}])
        if 'SELECT r.nom,COUNT(s.id)' in sql:
            return Result([{'nom': 'Ihorombe', 'nombre_sites': 1}])
        if 'ST_X(s.geom)' in sql:
            return Result([{'id': 1, 'nom': 'Ilakaka', 'ressource': 'saphir', 'ressource_nom': 'Saphir', 'couleur': '#2f5fc4', 'region': 'Ihorombe', 'annee': 2025, 'quantite': 100, 'prix_unitaire': 500, 'devise': 'USD', 'unite': 'carat', 'longitude': 45.2, 'latitude': -22.7}])
        return Result([])
    def __enter__(self): return self
    def __exit__(self, *args): pass

@contextmanager
def fake_connection(): yield FakeConnection()

@contextmanager
def failing_connection(): raise RuntimeError('Base indisponible'); yield

def patch_connection(monkeypatch, module, connection=fake_connection):
    monkeypatch.setattr(module, 'connection', connection)

def test_health_ok_and_database_error(monkeypatch):
    patch_connection(monkeypatch, ressources_api)
    assert ressources_api.health()['status'] == 'ok'
    patch_connection(monkeypatch, ressources_api, failing_connection)
    with pytest.raises(HTTPException) as exc: ressources_api.health()
    assert exc.value.status_code == 503

def test_types(monkeypatch):
    patch_connection(monkeypatch, ressources_api)
    assert ressources_api.types()[0]['code'] == 'minier'

def test_ressources_normal_and_unknown_type(monkeypatch):
    patch_connection(monkeypatch, ressources_api)
    assert ressources_api.ressources('minier')[0]['code'] == 'or'
    with pytest.raises(HTTPException) as exc: ressources_api.ressources('inconnu')
    assert exc.value.status_code == 404

def test_sites_geojson(monkeypatch):
    patch_connection(monkeypatch, sites_api)
    result = sites_api.list_sites('saphir')
    assert result['type'] == 'FeatureCollection'
    assert result['features'][0]['geometry']['type'] == 'Point'

def test_site_detail_normal_and_missing(monkeypatch):
    patch_connection(monkeypatch, sites_api)
    assert sites_api.site_detail(1)['productions'][0]['annee'] == 2025
    with pytest.raises(HTTPException) as exc: sites_api.site_detail(999)
    assert exc.value.status_code == 404

def test_regions(monkeypatch):
    patch_connection(monkeypatch, regions_api)
    assert regions_api.regions()['features'][0]['properties']['nom'] == 'Ihorombe'

def test_dashboard(monkeypatch):
    patch_connection(monkeypatch, dashboard_api)
    result = dashboard_api.dashboard()
    assert result['nombre_sites'] == 1
    assert result['sites'][0]['nom'] == 'Ilakaka'
