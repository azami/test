drop table if exists access_log;
drop table if exists sites_log;

create table access_log(
    user_id integer default null,
    date date not null,
    ua varchar(255) not null,
    ip varchar(15) not null,
    refer varchar(255)  null,
    link varchar(255),
    constraint tag_key unique (date, ua, ip),
    index refer(refer),
    index link(refer)
);

create table sites_log(
    site_id integer unique,
    total_in bigint not null default 0,
    total_out bigint not null default 0,
    monthly_in integer not null default 0,
    monthly_out integer not null default 0,
    index sites(site_id)
);
