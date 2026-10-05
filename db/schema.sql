CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS type_ressource (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL,
    nom VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS ressource (
    id SERIAL PRIMARY KEY,
    type_id INT NOT NULL REFERENCES type_ressource(id),
    code VARCHAR(30) UNIQUE NOT NULL,
    nom VARCHAR(80) NOT NULL,
    couleur CHAR(7) NOT NULL CHECK (couleur ~ '^#[0-9A-Fa-f]{6}$'),
    unite VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS region (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(80) UNIQUE NOT NULL,
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS idx_region_geom ON region USING GIST (geom);

CREATE TABLE IF NOT EXISTS site (
    id SERIAL PRIMARY KEY,
    ressource_id INT NOT NULL REFERENCES ressource(id),
    region_id INT REFERENCES region(id),
    nom VARCHAR(120) NOT NULL,
    description TEXT,
    geom GEOMETRY(Point, 4326) NOT NULL,
    UNIQUE(nom, ressource_id)
);

CREATE INDEX IF NOT EXISTS idx_site_geom ON site USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_site_ressource ON site (ressource_id);

CREATE TABLE IF NOT EXISTS production (
    id SERIAL PRIMARY KEY,
    site_id INT NOT NULL REFERENCES site(id) ON DELETE CASCADE,
    annee INT NOT NULL CHECK (
        annee BETWEEN 1900
        AND 2200
    ),
    quantite NUMERIC(14, 2),
    prix_unitaire NUMERIC(14, 2),
    devise CHAR(3) DEFAULT 'USD',
    UNIQUE(site_id, annee)
);

CREATE TABLE IF NOT EXISTS route (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(80),
    etat VARCHAR(10) NOT NULL CHECK (etat IN ('bon', 'moyen', 'mauvais', 'coupe')),
    geom GEOMETRY(LineString, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_route_geom ON route USING GIST (geom);