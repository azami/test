set foreign_key_checks = 0;
drop table if exists users;
drop table if exists novels;
drop table if exists tags;

create table users (
    id integer primary key auto_increment,
    name varchar(255) ,
    mail varchar(255) not null unique,
    password varchar(255) not null,
    site varchar(255) not null,
    url varchar(255) not null,
    status smallint(1) not null default 1
);

create table novels (
    id integer primary key auto_increment,
    user_id integer not null,
    title varchar(255) not null,
    summary text not null,
    tag_edit smallint(1) not null default 1,
    status smallint(1) not null default 1,
    foreign key (user_id) references users(id),
    index author (user_id)
);

create table tags (
    novel_id integer not null,
    tag varchar(255) not null,
    edit smallint(1) not null default 0,
    status smallint(1) not null default 1,
    foreign key (novel_id) references novels(id),
    constraint tag_key unique (novel_id, tag),
    index tag (tag),
    index novel(novel_id)
);
set foreign_key_checks = 1;
