Ext.ns('toolkit.gep');

toolkit.gep.QuesitoAvaliacaoForm = Ext.extend(
    Ext.Window,
    {

        constructor: function(cfg, args, kargs){
            this.pk_questionario = args;
            this.pk_fator_avaliacao = kargs;

            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title':'Associar Questões a Quesitos de Avaliação',
                'layout':'fit',
                'height': 400,
                'width': 600,
                'modal': true,
                'items':this.getGrid(),
                'buttons': [
                {
                    'text': 'Salvar',
                    'scope': this,
                    'handler': this.save
                },
                {
                    'text': 'Cancelar',
                    'scope': this,
                    'handler': this.destroy
                }
                ]   
            });

            toolkit.gep.QuesitoAvaliacaoForm.superclass.constructor.call(this, cfg);
        },

        getStore: function(){
            if(!this._store)
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('GEPQuesitosAvaliacao', 'list_elemento'),
                        'disableCaching': false,
                        'method': 'GET'
                    }),
                    baseParams:{
                        pk_questionario:this.pk_questionario
                    },
                    'reader': new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                        'pk',
                        'pk_element',
                        'enunciado',
                        'tipo' 
                        ]
                    })
                });
        
            return this._store;

        },

        getGrid: function(){
            if(!this._grid){
                this._grid = new toolkit.plugins.JsonGridPanel({
                    scope:this,
                    store: this.getStore(),
                    bbar: this.getPagingToolbar(),
                    searchable: false,
                    columnLines: true,
                    sm: this.getSelModel(),
                    autoExpandColumn: 'enunciado',
                    columns:[
                    this.getSelModel(),
                    {
                        dataIndex:'enunciado', 
                        header:'Enunciado', 
                        key: "enunciado",
                        id: "enunciado",
                        width:400
                    },
                    {
                        dataIndex:'tipo', 
                        header:'Tipo', 
                        key: "tipo",
                        id: "tipo",
                        width:100
                    }
                        
                    ],
                    listeners: {
                        scope: this,
                        render: function(grid) {
                            new Ext.LoadMask(grid.getEl(), {
                                'store': grid.getStore(),
                                'msg': 'Carregando dados...'
                            });
                        }
                    }
                });
            // var tbar= this._grid.getToolbar();
            // tbar.insertButton(0, this.getToolbar());

            }
            return this._grid;
        },

        getSelModel: function(){
            if(!this.selModel){
                var scope= this;
                this.selModel = new Ext.grid.CheckboxSelectionModel({
                    listeners:{
                        selectionchange: function(sm) {
                            if (sm.getCount()) {
                                this.getSelectionIds();

                            } else {

                            }
                        },
                        scope:this
                    },
                });
            }
            return this.selModel;
        },

        getSelectionIds: function(){
            var sm = this.getSelModel();
            var selecteds = []
            Ext.each(
                sm.getSelections(), 
                function(item, idx, all){
                    // selecteds.push(item.id);
                    selecteds.push(item.data['pk']);
                },
                this
                )                    
            // console.debug(selecteds);
            // console.debug(this.pk_questionario);
            return selecteds;
        },

        save: function() {
            var pk_fator_avaliacao = this.pk_fator_avaliacao;
            var pks_elemento = this.getSelectionIds();

            Ext.Ajax.request({
                'scope': this,
                'url': toolkit.util.Normalize.controller_action('GEPQuesitosAvaliacao', 'create'),
                'params': {
                    pk_fator_avaliacao: pk_fator_avaliacao, 
                    pks_elemento:pks_elemento
                },
                'success': function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.success){
                        this.getStore().reload();
                        this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                        Ext.Msg.show({
                            'title': 'Sucesso',
                            'msg': 'Dados salvos com sucesso!',
                            'icon': Ext.Msg.INFO,
                            'buttons': Ext.Msg.OK
                        });
                        this.destroy();
                    }else{
                        Ext.Msg.show({
                            'title': 'Atenção',
                            'msg': obj.message,
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    // this.destroy();
                    }
                },
                'failure': function(request) {
                    this.getStore().reload();
                    Ext.Msg.show({
                        'title': 'Atenção',
                        'msg': 'Não consegui salvar os dados.',
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK
                    });
                }
            })
        },

        getPagingToolbar: function() {
            if(!this._pagingToolbar)
                this._pagingToolbar = new Ext.PagingToolbar({
                    'style': 'border-right:none',
                    'store': this.getStore(),
                    'pageSize':5,
                    'displayInfo': true
                });
        
            return this._pagingToolbar;
        }

    }

    );