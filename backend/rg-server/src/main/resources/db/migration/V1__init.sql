-- Schema iniziale (GDD 7.2). L'accesso al DB e' solo dal backend: RLS attiva senza policy.

create table profile (
  id         uuid primary key references auth.users(id) on delete cascade,
  nickname   text not null unique,
  created_at timestamptz not null default now()
);

create table game_map (
  id      uuid primary key default gen_random_uuid(),
  code    text not null,
  name    text not null,
  version int  not null default 1,
  data    jsonb not null,
  unique (code, version)
);

create table match (
  id          uuid primary key default gen_random_uuid(),
  map_id      uuid not null references game_map(id),
  status      text not null check (status in ('LOBBY','RUNNING','FINISHED','ABORTED')),
  phase       text not null,
  turn        int  not null default 0,
  seed        bigint not null,
  ruleset     jsonb not null,
  version     int  not null default 0,
  created_by  uuid not null references profile(id),
  created_at  timestamptz not null default now(),
  finished_at timestamptz,
  winner_id   uuid references profile(id)
);

create table match_player (
  match_id  uuid not null references match(id) on delete cascade,
  player_id uuid not null references profile(id),
  seat      int  not null,
  color     text not null,
  shape     text not null,
  status    text not null,
  pp        int  not null default 0,
  joined_at timestamptz not null default now(),
  primary key (match_id, player_id),
  unique (match_id, seat)
);

create table match_snapshot (
  match_id   uuid not null references match(id) on delete cascade,
  version    int  not null,
  phase      text not null,
  state      jsonb not null,
  created_at timestamptz not null default now(),
  primary key (match_id, version)
);

create table match_event (
  match_id   uuid   not null references match(id) on delete cascade,
  seq        bigint not null,
  type       text   not null,
  visibility text   not null check (visibility in ('PUBLIC','PLAYER')),
  player_id  uuid,
  payload    jsonb  not null,
  created_at timestamptz not null default now(),
  primary key (match_id, seq)
);
create index on match_event (match_id, visibility, player_id, seq);

create table match_order (
  match_id     uuid not null references match(id) on delete cascade,
  turn         int  not null,
  phase        text not null,
  player_id    uuid not null references profile(id),
  payload      jsonb not null,
  confirmed_at timestamptz,
  primary key (match_id, turn, phase, player_id)
);

alter table profile        enable row level security;
alter table game_map       enable row level security;
alter table match          enable row level security;
alter table match_player   enable row level security;
alter table match_snapshot enable row level security;
alter table match_event    enable row level security;
alter table match_order    enable row level security;
