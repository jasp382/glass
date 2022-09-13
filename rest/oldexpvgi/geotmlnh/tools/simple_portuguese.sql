CREATE TEXT SEARCH DICTIONARY simple_portuguese
	--(TEMPLATE = pg_catalog.simple, STOPWORDS = portuguese);

CREATE TEXT SEARCH CONFIGURATION simple_portuguese
	--(copy = portuguese);

ALTER TEXT SEARCH CONFIGURATION simple_portuguese
	--ALTER MAPPING FOR asciihword, asciiword, hword, hword_asciipart, hword_part, word
	--WITH simple_portuguese;

--SELECT description, to_tsvector('simple_portuguese', description) AS test FROM geotmlnh_facedata LIMIT 1;
