drop table if exists in_log;
drop table if exists out_log;
drop table if exists novel_log;

create table in_log(
    user_id integer default null,
    date date not null,
    ua varchar(255) not null,
    ip varchar(15) not null,
    refer varchar(255) not null,
    constraint in_key unique (date, ua, ip, refer),
    index refer(refer)
);

create table out_log(
    user_id integer default null,
    novel_id integer not null,
    date date not null,
    ua varchar(255) not null,
    ip varchar(15) not null,
    url varchar(255) default null,
    refer varchar(255) default null,
    constraint out_key unique (date, ua, ip, novel_id)
);
    
create table novel_log(
    novel_id integer unique,
    total_in bigint not null default 0,
    total_out bigint not null default 0,
    monthly_in integer not null default 0,
    monthly_out integer not null default 0,
    index sites(novel_id)
);
