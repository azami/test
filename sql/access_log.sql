drop table if exists in_logs;
drop table if exists out_logs;
drop table if exists user_logs;
drop table if exists novel_logs;

create table in_logs(
    user_id integer default null,
    cookie varchar(16) not null,
    date date not null,
    ua varchar(255) not null,
    ip varchar(15) not null,
    refer varchar(255) not null,
    constraint in_key unique (date, ua, ip, refer),
    index refer(refer)
);

create table out_logs(
    user_id integer default null,
    cookie varchar(16) not null,
    novel_id integer not null,
    date date not null,
    ua varchar(255) not null,
    ip varchar(15) not null,
    url varchar(255) default null,
    constraint out_key unique (date, ua, ip, novel_id)
);
    
create table user_logs(
    user_id integer unique,
    total_in bigint not null default 0,
    monthly_in integer not null default 0,
    index site_access(user_id)
);

create table novel_logs(
    novel_id integer unique,
    total_out bigint not null default 0,
    monthly_out integer not null default 0,
    index novel_access(novel_id)
);
