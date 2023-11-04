-- script create RDS tables
create table if not exists supermercado(
	id SERIAL primary key,
	nome VARCHAR(60) unique not null,
	franquia VARCHAR(30) not null,
    endereco VARCHAR(90),
    estado VARCHAR(30),
    cidade VARCHAR(30),
    bairro VARCHAR(30),
	url VARCHAR(60) not null,
	cep INTEGER
);


create table if not exists departamento(
	id SERIAL primary key, 
	nome VARCHAR(30) not null,
	url VARCHAR(120) not null,
	hierarquia VARCHAR(90) not null
);

create table if not exists produto(
	id SERIAL primary key,
	nome VARCHAR(90) not null,
	marca VARCHAR(60)
);

create table if not exists anuncio(
	id_anuncio SERIAL primary key,
	id_supermercado INTEGER not null,
	id_departamento INTEGER not null,
	id_produto INTEGER not null, 
	preco_regular FLOAT,
	preco_exclusivo FLOAT,
	tempo DATE,
    FOREIGN KEY (id_supermercado)
    	references supermercado(id),
    FOREIGN KEY (id_departamento)
    	references departamento(id),
    FOREIGN KEY (id_produto)
    	references produto(id)
);


-- drop table supermercado
-- drop table departamento 
-- drop table produto 
-- drop table anuncio