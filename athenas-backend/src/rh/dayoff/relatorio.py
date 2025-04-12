

A construção dos modelos no django obedece à modelagem com algumas falhas de nomenclatura e,
relação de modelos acessórios: por exemplo, anotações.
Pendência da definição das ações, quais seriam?
Definição de choices precisa ser refeita.
Dayoff terá dependência de afastamentos?
Nenhuma regra de negócio implementada.
Criar:
    - validações no classcode;
    - api backend;
    - restful, infraestrutura para acesso

A principio um PASU é criado, alterado, interrompido ou suspenso.
    CREATION: apenas marcação inicial;
    ALTERATION: qualquer outra marcação será alteração pois pode vir de PASUS ou
        de dias em "época oportuna";
    INTERRUPTION: interrupção de usufruto;
    SUSPENSION: suspensão de usufruto;
    INDEMNIFICATION: indenização de período aquisitivo;
    AUTHORIZATION: autorização de usufruto.

Caso de uso de criação de usufrutos:
1 - CREATION, marcação inicial do período aquisitivo, ocorre em fase de homologação;
2 - ALTERATION, marcação a partir de alteração de períodos já marcados:
    * necessário campo para guardar quantos dias estavam disponíveis(em época oportuna)
    * campos de cache para saber informações "do momento do período aquisitivo"

Implementar nova forma de aquisição de período.


    Quero fazer entregas de produtos pequenos.Entregas semanais.
    Exemplo:
        marcação
        alteração
        suspensão
        autorização

