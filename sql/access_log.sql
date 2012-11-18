drop table if exists users;
drop table if exists novels;
drop table if exists tags;

create table users (
    id integer primary key auto_increment,
    name varchar(255) not null,
    mail varchar(511) not null unique,
    password varchar(255) not null,
    site varchar(255) not null,
);

create table novels(
    id integer primary key auto_increment,
    user_id integer not null,
    title varchar(255) not null,
    summary text not null,
    index author (user_id)
);

create table tags(
    id integer primary key auto_increment,
    novel_id integer not null,
    name varchar(255) not null,
    lock tinyint(1) not null deafult 0
    index tag (name),
    index novel(novel_id)
);
