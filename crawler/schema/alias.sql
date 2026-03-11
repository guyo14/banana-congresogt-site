-- Insert non-active Congressmen
INSERT INTO congressmen (id, first_name, last_name, key, party_id, district_id, photo_url, birth_date, status)
VALUES 
(938, 'Ana Patricia', 'Orantes Thomas', 'orantes thomas ana patricia', 11, 13, 'https://www.congreso.gob.gt/assets/uploads/diputados/1d58c-ana-patricia-orantes-thomas.jpg', '1969-01-20', 'inactive'),
(936, 'Jonathan Kiril Thomas', 'Menkos Zeissig', 'menkos zeissig jonathan kiril thomas', 11, 13, 'https://www.congreso.gob.gt/assets/uploads/diputados/e9305-jonathan-kiril-menkos.jpg', '1975-06-29', 'inactive')
ON CONFLICT (id) DO NOTHING;

-- Alias table structure
CREATE TABLE IF NOT EXISTS congressmen_aliases (
    id SERIAL PRIMARY KEY,
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL UNIQUE
);

-- Populating alias matches
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (840, 'ajcip canel hellen magaly alexandra') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (840, 'ajcip canel hellen magaly alexandrá') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (948, 'amézquita del valle cesar augusto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (972, 'arévalo ávila sherol ivanisse') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (918, 'ayala marroquín jorge estuardo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (969, 'barragan morales gerson geovanny') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (891, 'bonilla gonzalez victor vicente') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (891, 'bonilla gonzález victor vicente') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (973, 'cabrera ordoñez jorge mario') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (908, 'caceres gamarro luis antonio') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (791, 'cardona arreaga de pojoy karla betzaida') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (905, 'castañasa mendizabal obbed ediberto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (934, 'castañon gonzález manfredo duvalier') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (939, 'cerna acevedo damaris carolina') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (899, 'chic cardona jose alberto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (962, 'cifuentes barragan gladis carolina') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (39, 'contreras colindres luis alberto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (889, 'cua tumin raul arnulfo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (889, 'cuá tumin raúl arnulfo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (950, 'de jesús mejía edín alexander') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (970, 'de león benitez alberto eduardo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (777, 'de león de león de pérez greicy domenica') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (963, 'domínguez orozco jeovanni omar') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (906, 'dávila cordova cesar roberto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (941, 'enríquez garzaro sergio guillermo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (920, 'galvez de león manrique obel') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (861, 'gutiérrez raguay sonia marina') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (870, 'gálvez muñoz mario ernesto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (892, 'javier javier esduin jerson') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (99, 'martínez herrera joel rubén') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (921, 'martínez juarez christian joel') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (781, 'martínez salazar duay antoni') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (893, 'mendoza franco jose pablo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (897, 'motta kolleff elena sofía') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (932, 'pellecer rodríguez rodrigo antonio') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (945, 'perez toribio marco alejandro') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (834, 'pérez álvarez samuel andrés') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (922, 'ramírez cámeros darwin edgardo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (126, 'ramírez retana thelma elizabeth') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (127, 'reyes lee edgar raul') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (811, 'rivas garcía juan ramón') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (857, 'rivera estévez juan carlos') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (901, 'rodas cardona cesar augusto') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (130, 'rojas alarcón carlos napoleón') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (914, 'sanabria arias jose carlos') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (955, 'tebelan pantzay marcos eduardo') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (954, 'tzun de león erick josé') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (155, 'villagrán antón andrea beatriz') ON CONFLICT (alias) DO NOTHING;
INSERT INTO congressmen_aliases (congressman_id, alias) VALUES (927, 'zepeda zepeda marvin adrian') ON CONFLICT (alias) DO NOTHING;
