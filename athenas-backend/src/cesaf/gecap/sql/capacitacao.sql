create or replace view gecap_tipo_evento as
select
    gc.id,
    (select count(*) from gecap_congresso gcc where gcc.capacitacao_ptr_id = gc.id) as congresso,
    (select count(*) from gecap_curso gccu where gccu.capacitacao_ptr_id = gc.id) as curso,
    (select count(*) from gecap_evento gce where gce.capacitacao_ptr_id = gc.id) as evento,
    (select count(*) from gecap_feira gcf where gcf.capacitacao_ptr_id = gc.id) as feira,
    (select count(*) from gecap_oficina gco where gco.capacitacao_ptr_id = gc.id) as oficina,
    (select count(*) from gecap_reuniao gcr where gcr.capacitacao_ptr_id = gc.id) as reuniao,
    (select count(*) from gecap_seminario gcs where gcs.capacitacao_ptr_id = gc.id) as seminario
from
    gecap_capacitacao gc;

create or replace view gecap_tipo_evento_titulo as
select
    gcte.id,
    case
        when gcte.congresso > 0 then 'CONGRESSO'
        when gcte.curso > 0 then 'CURSO'
        when gcte.evento > 0 then 'EVENTO'
        when gcte.feira > 0 then 'FEIRA'
        when gcte.oficina > 0 then 'OFICINA'
        when gcte.reuniao > 0 then 'REUNIÃO'
        when gcte.seminario > 0 then 'SEMINÁRIO'
    end as tipo_evento
from
    gecap_tipo_evento gcte;
