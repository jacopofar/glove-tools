--main table, for each word stores the GloVe vector as a JSON structure
CREATE TABLE word_vectors(
  word text NOT NULL,
  vector json,
  CONSTRAINT pk_word PRIMARY KEY (word)
);

--sequence to give each vector ball an identifier

CREATE SEQUENCE vector_balls_id_seq
INCREMENT 1
MINVALUE 1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

--vector balls
CREATE TABLE vector_balls(
  id integer NOT NULL DEFAULT nextval('vector_balls_id_seq'::regclass),
  words json NOT NULL,
  vectors json NOT NULL,
  central_vector json NOT NULL,
  radius double precision,
  CONSTRAINT vector_balls_pkey PRIMARY KEY (id)
);
