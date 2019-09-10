CREATE TABLE country(
    id int NOT NULL auto_increment,
    country varchar(2),
    PRIMARY KEY (id)
);

CREATE TABLE city(
    id int NOT NULL auto_increment,
    city varchar(255),
    id_country int,
    PRIMARY KEY (id),
    active tinyint(1),
    FOREIGN KEY (id_country) REFERENCES country(id)
);

CREATE TABLE productos(
    sku VARCHAR(255) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2),
    PRIMARY KEY (sku)
);

CREATE TABLE reglas(
    id_regla int NOT NULL auto_increment,
    ciudad varchar(255),
    pais varchar(2),
    sku varchar(255),
    min_condition int,
    max_condition int,
    variation DECIMAL(10,2),
    PRIMARY KEY (id_regla),
    FOREIGN KEY (sku) REFERENCES productos(sku)
);


INSERT INTO `country` (`country`) VALUES ('ni');
INSERT INTO `country` (`country`) VALUES ('us');

INSERT INTO `city` (`city`, `id_country`, `active`) VALUES ('Leon', '1', '1');
INSERT INTO `city` (`city`, `id_country`, `active`) VALUES ('Chinandega', '1', '0');

INSERT INTO `productos` (`sku`, `descripcion`, `precio`) VALUES ('AZ00001', 'Paraguas de señora estampado', 10);
INSERT INTO `productos` (`sku`, `descripcion`, `precio`) VALUES ('AZ00002', 'Helado de sabor fresa', 1);

INSERT INTO `reglas` (`ciudad`, `pais`, `sku`, `min_condition`, `max_condition`, `variation`) VALUES ('Leon', 'ni', 'AZ00001',500,599,1.5);
INSERT INTO `reglas` (`ciudad`, `pais`, `sku`, `min_condition`, `max_condition`, `variation`) VALUES ('Leon', 'ni', 'AZ00002',500,599,0.5);
