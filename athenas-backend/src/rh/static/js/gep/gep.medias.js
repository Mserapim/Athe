Ext.ns('toolkit.gep');


toolkit.gep.Medias = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg){
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title:'Histórico de Avaliações',
                closable: true,
                autoScroll: true,
                modal: true,
                width: 600,
                height: 500,
                border: false,
                items:this.getTpl()

            });

            toolkit.gep.Medias.superclass.constructor.call(this, cfg);
            // toolkit.Application.tabspace.add(this);
        },

        getStore: function() {
            if(!this._store){
                this._store = new Ext.data.Store({
                    proxy: new Ext.data.HttpProxy({
                        url: toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio', 'get_medias'),
                        disableCaching: false,
                        // method: 'GET'
                    }),
                    reader: new Ext.data.JsonReader({
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                        'pk',
                        'pk_servidor',
                        'servidor',
                        'cargo',
                        'matricula',
                        'lotacao',
                        'fator_avaliacao',
                        'inicio_estagio',
                        'fim_estagio',
                        'avaliacoes',
                        ]
                    }),
                    // autoLoad:true,
                    scope:this
                });
            }
        
            return this._store;
        },

        getTpl: function(){

            return new xDataView({
                store: this.getStore(),
                autoHeight:true,
                multiSelect: true,
                // overClass:'list-hover',
                itemSelector:'.topo',
                emptyText: 'Sem itens para exibir.',
                tpl: new xTemplate(
                    '<tpl for="." >',
                       '<div class="topo">',
                            '<h1>Histórico de Avaliações</h1>',
                            '<p><b>Servidor: </b>{servidor}</p>',
                            '<p><b>Matricula: </b>{matricula}</p>',
                            '<p><b>Cargo: </b> {cargo}</p>',
                            '<p><b>Lotação: </b> {lotacao}</p>',
                            '<p><b>Periodo do Estágio: </b> De {inicio_estagio} até {fim_estagio}</p><br/>',
                        '</div>',
                        '<div class="info">',
                            '<tpl if="fator_avaliacao == \'\'"><h1><b>Nenhuma avaliação encontrada!<h1></tpl>',
                        '</div>',
                        '<tpl for="fator_avaliacao">',

                            '<div class="periodo"',
                                '<p>Etapa Avaliada: {periodo_avaliado}ª <br> Data da avaliação: {data} - Avaliador: {avaliador}</p>',
                            '</div>',
                            '<div class="cabecalho">',
                                '<p>FATOR',
                            '</div>',
                            '<div class="cabecalho">',
                                '<p>MÉDIA POR FATOR',
                            '</div>',
                            '<div class="cabecalho">',
                                '<p>CONCEITO',
                            '</div>',
                                '<tpl for="fator">',
                                    '<div class="quesito">',
                                        '<p>{descricao}</p>',
                                    '</div>',
                                    '<div class="media">',
                                        '<p>{media}</p>',
                                    '</div>',
                                    '<div class="conceito">',
                                        '<p>{conceito}</p>',
                                    '</div>',
                                '</tpl>',
                            '<div class="fim">',
                                '<p>Média da Etapa: {media_etapa}</p>',
                                '<p><font color="red">{media_comissao}</font></p>',
                            '</div>',
                            '</br>',
                        '</tpl>',
                    '</tpl>'
                    )
                });
        },

    }
);