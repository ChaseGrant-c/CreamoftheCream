-- Run this in the Supabase SQL editor after the first successful migrate.
-- Django connects with DATABASE_URL and filters every query by owner_id.
-- These policies cover the Supabase API if the anon key is used from a browser later.
-- The postgres role Django uses bypasses row level security; keep that URL server-side.

alter table public.focus_people enable row level security;
alter table public.focus_links enable row level security;
alter table public.focus_posts enable row level security;

grant select, insert, update, delete on public.focus_people to authenticated;
grant select, insert, update, delete on public.focus_links to authenticated;
grant select, insert, update, delete on public.focus_posts to authenticated;

create policy "focus_people_owner_all"
on public.focus_people
for all
to authenticated
using (owner_id = auth.uid())
with check (owner_id = auth.uid());

create policy "focus_links_owner_all"
on public.focus_links
for all
to authenticated
using (
  exists (
    select 1 from public.focus_people as person
    where person.id = focus_links.connection_id
      and person.owner_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.focus_people as person
    where person.id = focus_links.connection_id
      and person.owner_id = auth.uid()
  )
);

create policy "focus_posts_owner_all"
on public.focus_posts
for all
to authenticated
using (owner_id = auth.uid())
with check (owner_id = auth.uid());
