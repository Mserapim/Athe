Ext.ns('toolkit.questionario');

toolkit.questionario.VerResposta = Ext.extend(
    Ext.Window,
    {
       
        // constructor: function(cfg, questionario, param, url) {
        constructor: function(cfg, param, url) {
            this.param = param
            this.url = url

            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                // 'title': 'Lista de Respostas',
                'closable': true,
                'autoScroll': true,
                'modal': true,
                'width': 430,
                'height': 330,
                'border': false,
                'items':this.getGrid()
            });

            toolkit.questionario.VerResposta.superclass.constructor.call(this, cfg);
        },

        getStore: function() {
            if(!this._store){
                this._store = new Ext.data.Store({
                    proxy: new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('QMontarQuestionario', 'ver_resposta'),
                        'method': 'GET',
                        'disableCaching': false
                    }),
                    reader: new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                        'data',
                        'enunciado',
                        'tipo',
                        'alternativas',
                        'respostas',
                        'mista',
                        ]
                    }),
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
                overClass:'list-hover',
                itemSelector:'.list-item',
                emptyText: 'Sem itens para exibir.',
                tpl: new xTemplate(
                    '<tpl for="." >',
                        '<div class="list">',
                            '<b><p>{enunciado} </p></b>',
                            '<tpl if="tipo != \'Ref. Textual\'">', 
                                '<div class="list_alt">',
                            '</tpl>',
                            '<tpl for="alternativas">',
                                '<ul><li>',
                                '<tpl if="flag == 0">',
                                '<p>',
                                '</tpl>',
                                '{label} {texto}',
                                '</li></ul>',
                            '</tpl>',
                            '</div>',
                            '<tpl if="tipo != \'Ref. Textual\'">', 
                                '<div class="list_resp">',
                            '</tpl>',
                            '<tpl if="tipo != \'Ref. Textual\'">', 
                                '<i><h6>Respondido em: {data}:</h6></i><br>',
                            '</tpl>',
                            '<tpl if="tipo != \'Questão\'">', 
                                '<tpl for="respostas">',
                                    '<i>{label} {alternativa} </i>',
                                    '<i>{texto}<br></i> ',
                                '</tpl>',
                            '</tpl>',
                            '</div>',
                        '</div>',
                    '</tpl>'
                    )
            });
        },

        getStoreGrid: function() {
            if(!this._gStore){
                this._gStore = new Ext.data.JsonStore({
                    autoLoad:true,
                    root: 'collection',
                    totalProperty: 'count',
                    fields: [
                    'pk', 
                    'data', 
                    'titulo'
                    ],
                    url: this.url,
                    // url: toolkit.util.Normalize.controller_action('QMontarQuestionario','get_resp',[this.questionario,this.param]),
                    // url: toolkit.util.Normalize.controller_action('QMontarQuestionario','get_data_resposta'),
                    // baseParams:{pk_questionario: this.questionario, pk_param: this.param},
                    scope:this
                });
            }
            return this._gStore;
        },

        getGrid: function(){
            if(!this._grid){
                this._grid = new Ext.grid.GridPanel({
                    'scope':this,
                    'width':415,
                    'height': 280,
                    'store': this.getStoreGrid(),
                    'bbar': this.getPagingToolbar(),
                    'columns':[
                    {
                        dataIndex:'titulo', 
                        header:'Titulo do Questionário', 
                        width:260
                    },
                    {
                        dataIndex:'data', 
                        header:'Data', 
                        width:80
                    },
                    {
                        xtype: 'actioncolumn',
                        header:'Visualizar',
                        width: 65,
                        scope:this,
                        items:
                        [
                        {
                            tooltip:'Visualizar Resposta',  
                            icon: '/' + global.Context + '/static/images/document-validate.png',
                            handler: function(grid, row, col)
                            {
                                var record = grid.getStore().getAt(row);
                                var verResposta = new Ext.Window({
                                    'title':record.get('titulo')+' - '+record.get('data'),
                                    'width':500,
                                    'height':500,
                                    'modal': true,
                                    'autoScroll':true,
                                    'items':this.getTpl(),
                                    'listeners': {
                                        show:function(){
                                            this.getStore().load({
                                                params:{
                                                    pk_questionario_resposta:record.get('pk'), 
                                                    pk_param: this.param
                                                }
                                            });
                                        },
                                        scope:this
                                    }
                                });
                                verResposta.show()
                            },
                            scope:this
                        }
                        ]
                    }
                    ],
                    'listeners': {
                        'scope': this,
                        'render': function(grid) {
                            new Ext.LoadMask(grid.getEl(), {
                                'store': grid.getStore(),
                                'msg': 'Carregando Respostas...'
                            });
                        }
                    }
                });

            }
            return this._grid;
        },

        getPagingToolbar: function() {
            if(!this._pagingToolbar){
                this._pagingToolbar = new Ext.PagingToolbar({
                    'style': 'border-left:none',
                    'store': this.getStoreGrid(),
                    'pageSize':15,
                    'displayInfo': true
                });
            }        
            return this._pagingToolbar;
        }
    }
    );