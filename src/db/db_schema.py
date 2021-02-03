DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS channels
(
    channel_id        int8,
    name              text
        unique
        not null,
    link              text
        not null,
    description       text
        not null,
    subscribers_count int8
        not null,
    type              text
        not null,
    constraint pk_channels primary key (channel_id)
);
CREATE TABLE IF NOT EXISTS messages
(
    message_id  int8,
    channel_id  int8,
    date        timestamp
        not null,
    text        text,
    views_count int8,
    author      text,
    is_post     bool,

    constraint pk_messages primary key (message_id),

    constraint fk_channels foreign key (channel_id)
        references channels (channel_id)
        on delete set null
        on update cascade
);'''
