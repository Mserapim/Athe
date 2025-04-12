Ext.ns('toolkit.questionario');

toolkit.questionario.AlternativaGrid = Ext.extend(

    
Ext.grid.GridPanel,
    {
        _getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('QAlternativa', 'list'),
                        'disableCaching': false,
                        'method': 'GET'
                    }),
                    'reader': new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                            'pk',
                            'label',
                            'texto',
                            'valor',
                            'grupo' 
                        ]
                    })
                });
        
            return this._store;
        },

        _update: function() {
            var sel = this.getSelectionModel().getSelected();

            if(sel) {
                Ext.Ajax.request({
                    'url': toolkit.util.Normalize.controller_action('QAlternativa', 'get', [sel.get('pk')]),
                    'disableCaching': false,
                    'scope': this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);

                        new toolkit.questionario.AlternativaForm({
                            'action': 'update',
                            'params': { 'pk': sel.get('pk') }, 
                            'values': obj.instance,
                            'callback': {
                                'success': {
                                    'scope': this,
                                    'handler': function() { this.getStore().reload() }
                                }
                            }
                        }).show();
                    },
                    'failure': function(request) {
                        Ext.Msg.show({
                            'title': 'Grupo da Tabela',
                            'msg': 'Ocorreu um erro buscando informações, tente novamente.',
                            'icon': Ext.Msg.ERROR,
                            'buttons': Ext.Msg.OK
                        });
                    }
                });
            }
            else Ext.Msg.show({
                'title': 'Grupo da Tabela',
                'msg': 'Primeiro selecione um item para ser editado.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _create: function() {
            new toolkit.questionario.AlternativaForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() { this.getStore().reload() }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create'
            }).show();
        },

        _remove: function() {
            var sels = this.getSelectionModel().getSelections();
            var pks = []

            if (sels.length > 0){

                Ext.each(sels, function(record) {
                    pks.push(record.get('pk'))
                });

                Ext.Msg.show({
                    'title': 'Alternativa',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('QAlternativa', 'remove'),
                            'params': { pk: pks },
                            'success': function(request) {
                                this.getStore().reload();
                            },
                            'failure': function(request) {
                                this.getStore().reload();
                                Ext.Msg.show({
                                    'title': 'Alternativa',
                                    'msg': 'Ocorreram erros removendo os itens selecionados.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                });
            } else  Ext.Msg.show({
                'title': 'Alternativa',
                'msg': 'Primeiro selecione o item que deseja remover.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _move: function(direction) {
            var sels = this.getSelectionModel().getSelections();
            var pks = []
            //var pks_quest = [] // vai armazenar a pk da questao ou da referencia textual

            if(sels.length > 0) {
                Ext.each(sels, function(record) {
                        pks.push(record.get('pk'))
                        //pks_quest.push(record.get('pk')) //recupera a pk da questao ou da referencia textual
                    });

                Ext.Ajax.request({
                    'scope': this,
                    'url': toolkit.util.Normalize.controller_action('QAlternativa', 'move_alternativa',[direction]),
                    'params': { pk: pks},// envia a pk do elemento e da questao ou referencia textual
                    'success': function(request) {
                        this.getStore().reload();
                    },
                    'failure': function(request) {
                        this.getStore().reload();
                        Ext.Msg.show({
                            'title': 'Questões/Referências Textuais',
                            'msg': 'Ocorreram erros na ordenação dos itens selecionados.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                });
            } else  Ext.Msg.show({
                'title': 'Questão',
                'msg': 'Primeiro selecione o item que deseja mover.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        getToolbar: function() {
            if(!this._toolbar)
                this._toolbar = new Ext.Toolbar({
                    'style': 'border-top:none;border-right:none',
                    'items': [
                        {
                            'text': 'Novo',
                            'scope': this,
                            'handler': this._create,
                            'iconCls': 'icon-diarias icon-add'
                        },
                        {
                            'text': 'Editar',
                            'scope': this,
                            'handler': this._update,
                            'iconCls': 'icon-diarias icon-update'
                        },
                        {
                            'text': 'Remover',
                            'scope': this,
                            'handler': this._remove,
                            'iconCls': 'icon-diarias icon-remove'
                        },
                        '-',
                        {
                            'text': 'Acima',
                            'iconCls': 'icon-gep icon-up',
                            'scope': this,
                            'handler': function() { this._move('up') }
                        },
                        {
                            'text': 'Abaixo',
                            'iconCls': 'icon-gep icon-down',
                            'scope': this,
                            'handler': function() { this._move('down') }
                        }
                    ]   
                });
        
            return this._toolbar;
        },

        getPagingToolbar: function() {
            if(!this._pagingToolbar)
                this._pagingToolbar = new Ext.PagingToolbar({
                    'style': 'border-right:none',
                    'store': this._getStore(),
                    'displayInformation': true
                });
        
            return this._pagingToolbar;
        },

        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title':'Alternativas',
                'tbar': this.getToolbar(),
                'bbar': this.getPagingToolbar(),
                'store': this._getStore(),
                'autoExpandColumn': 'autoExpand',
                'cm': new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        'header': 'Texto',
                        'dataIndex': 'texto',
                        'id': 'autoExpand'
                    },
                    {
                        'header': 'Label',
                        'dataIndex': 'label',
                        'width': 100
                    },
                    {
                        'header': 'Peso',
                        'dataIndex': 'valor',
                        'width': 100
                    },
                    {
                        'header': 'Grupo',
                        'dataIndex': 'grupo',
                        'width': 100
                    }
                ])
            });

            toolkit.questionario.AlternativaGrid.superclass.constructor.call(this, cfg);

            this.on('render', function(panel) {
                var store = panel.getStore();

                new Ext.LoadMask(panel.getEl(), {
                    'msg': 'Carregando Alternativas...',
                    'store': store
                });
            });
        }
    }

    
);