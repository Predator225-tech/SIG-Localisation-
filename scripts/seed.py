import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import connection

TYPES=[('minier','Minier'),('agricole','Agricole'),('energie','Énergie')]
RESOURCES=[('or','Or','#d9a400','kg','minier'),('argent','Argent','#78909c','kg','minier'),('saphir','Saphir','#2f5fc4','carat','minier'),('nickel','Nickel','#2e9e6b','t','minier'),('graphite','Graphite','#424242','t','minier'),('vanille','Vanille','#e65100','t','agricole'),('girofle','Girofle','#8e24aa','t','agricole'),('hydro','Hydroélectricité','#00acc1','MW','energie')]
REGIONS=["Diana","Sava","Sofia","Boeny","Betsiboka","Melaky","Analanjirofo","Alaotra-Mangoro","Atsinanana","Analamanga","Itasy","Bongolava","Vakinankaratra","Amoron'i Mania","Haute Matsiatra","Vatovavy","Fitovinany","Ihorombe","Atsimo-Atsinanana","Menabe","Atsimo-Andrefana","Androy","Anosy"]
# Coordonnées indicatives de sites, à confirmer avant tout usage opérationnel.
SITES=[('Betsiaka','or',48.90,-13.30,'Diana'),('Ilakaka','saphir',45.20,-22.70,'Ihorombe'),('Ambatovy','nickel',48.30,-18.85,'Alaotra-Mangoro'),('Moramanga','graphite',48.20,-18.95,'Alaotra-Mangoro'),('Zone nord-ouest','argent',46.80,-15.90,'Boeny'),('Sambava','vanille',50.00,-14.27,'Sava'),('Antalaha','vanille',50.25,-14.90,'Sava'),('Fénérive-Est','girofle',49.40,-17.40,'Analanjirofo'),('Andekaleka','hydro',48.50,-18.70,'Atsinanana'),('Toamasina','girofle',49.40,-18.15,'Atsinanana'),('Manakara','girofle',48.02,-22.14,'Fitovinany'),('Tolagnaro','saphir',46.99,-25.03,'Anosy'),('Maevatanana','or',46.84,-16.95,'Betsiboka'),('Mampikony','graphite',47.64,-16.10,'Sofia'),('Ambatofinandrahana','nickel',46.80,-20.55,'Amoron\'i Mania'),('Antsirabe','hydro',47.03,-19.87,'Vakinankaratra'),('Maintirano','argent',44.03,-18.07,'Melaky'),('Morondava','vanille',44.28,-20.28,'Menabe')]

def main():
    with connection() as conn:
        with conn.transaction():
            for code,name in TYPES: conn.execute('INSERT INTO type_ressource(code,nom) VALUES(%s,%s) ON CONFLICT(code) DO UPDATE SET nom=EXCLUDED.nom',(code,name))
            for code,name,color,unit,type_code in RESOURCES:
                conn.execute('INSERT INTO ressource(type_id,code,nom,couleur,unite) VALUES((SELECT id FROM type_ressource WHERE code=%s),%s,%s,%s,%s) ON CONFLICT(code) DO UPDATE SET type_id=EXCLUDED.type_id,nom=EXCLUDED.nom,couleur=EXCLUDED.couleur,unite=EXCLUDED.unite',(type_code,code,name,color,unit))
            for name in REGIONS: conn.execute('INSERT INTO region(nom) VALUES(%s) ON CONFLICT(nom) DO NOTHING',(name,))
            for name,resource,lon,lat,region in SITES:
                site=conn.execute('''INSERT INTO site(ressource_id,region_id,nom,description,geom) VALUES((SELECT id FROM ressource WHERE code=%s),(SELECT id FROM region WHERE nom=%s),%s,%s,ST_SetSRID(ST_MakePoint(%s,%s),4326)) ON CONFLICT(nom,ressource_id) DO UPDATE SET region_id=EXCLUDED.region_id,geom=EXCLUDED.geom RETURNING id''',(resource,region,name,'Point de référence indicatif.',lon,lat)).fetchone()
                for year in (2023,2024,2025):
                    conn.execute('INSERT INTO production(site_id,annee,quantite,prix_unitaire,devise) VALUES(%s,%s,%s,%s,%s) ON CONFLICT(site_id,annee) DO UPDATE SET quantite=EXCLUDED.quantite,prix_unitaire=EXCLUDED.prix_unitaire,devise=EXCLUDED.devise',(site['id'],year,round(100+(year-2023)*12,2),round(500+(year-2023)*25,2),'USD'))
    print(f"Données de départ installées : {len(SITES)} sites, {len(REGIONS)} régions.")
if __name__=='__main__': main()
