Ext.ns('toolkit.gep');

toolkit.gep.QuesitoAvaliacao = Ext.extend(

    Ext.grid.GridPanel,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title':'Quesitos de Avaliação',
                'tbar': this.getToolbar(),
                // 'bbar': this.getPagingToolbar(),
                'store': this.getStore(),
                'autoExpandColumn': 'autoExpand',
                'cm': new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        'header': 'Enunciado',
                        'dataIndex': 'enunciado',
                        'id': 'autoExpand'
                    },
                    {
                        'header': 'Tipo',
                        'dataIndex': 'tipo',
                        'width': 100
                    }
                    ])
            });

            toolkit.gep.QuesitoAvaliacao.superclass.constructor.call(this, cfg);

        },

        getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('GEPQuesitosAvaliacao', 'list_quesitos'),
                        'disableCaching': false,
                        'method': 'GET'
                    }),
                    'reader': new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                        'pk',
                        'pk_quesito',
                        'pk_element',
                        'enunciado',
                        'tipo' 
                        ]
                    })
                });
        
            return this._store;
        },

        getParams: function(){
            // console.log(this.getStore().baseParams);
            // console.log(this.getStore().baseParams.pk_fator);
            var obj = this.getStore().baseParams;
            return obj;
        },


        _create: function(){
            var pk_fator = this.getParams().pk_fator;
            var pk_questionario = this.getParams().pk_questionario;

            new toolkit.gep.QuesitoAvaliacaoForm({
                'action': 'create',
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                }
            }, pk_questionario, pk_fator).show();

        },

        _remove: function() {
            var sels = this.getSelectionModel().getSelections();
            var pks = []
            var pk_quesito = []

            if (sels.length > 0){
                Ext.each(sels, function(record) {
                    pks.push(record.get('pk'))
                    pk_quesito.push(record.get('pk_quesito'))
                });

                Ext.Msg.show({
                    'title': 'Quesitos de Avaliação',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('GEPQuesitosAvaliacao', 'remove'),
                            'params': {
                                pk_element: pks,
                                pk_quesito: pk_quesito
                            },
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);

                                if(obj.success){
                                    Ext.Msg.alert('Sucesso', 'Dados removidos com sucesso!');
                                    this.getStore().reload();
                                }else{
                                    Ext.Msg.show({
                                        'title': 'Atenção',
                                        'msg': obj.message,
                                        'icon': Ext.Msg.WARNING,
                                        'buttons': Ext.Msg.OK
                                    });

                                }
                            },
                            'failure': function(request) {
                                this.getStore().reload();
                                Ext.Msg.show({
                                    'title': 'Quesitos de Avaliação',
                                    'msg': 'Ocorreram erros removendo os itens selecionados.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                })
            } else  Ext.Msg.show({
                'title': 'Quesitos de Avaliação',
                'msg': 'Primeiro selecione o item que deseja remover.',
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
                        'iconCls': 'icon-gep icon-new',
                        'scope': this,
                        'handler': this._create
                    },
                    {
                        'text': 'Remover',
                        'scope': this,
                        'handler': this._remove,
                        'iconCls': 'icon-gep icon-delete'
                    },
                    '-',
                    ]   
                });
        
            return this._toolbar;
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