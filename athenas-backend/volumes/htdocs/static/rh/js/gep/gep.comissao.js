Ext.ns('toolkit.gep');

toolkit.gep.Comissao = Ext.extend(
    Ext.grid.GridPanel,
    {
        constructor: function(cfg){
            Ext.apply(cfg, {
                title:'Comissão',
                tbar: this.getToolbar(),
                bbar: this.getPagingToolbar(),
                store: this.getStore(),
                columnLines: true,
                cm: new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        header: 'Comissão Anterior',
                        dataIndex: 'comissao_anterior',
                        width: 400,
                    },
                    {
                        header: 'Publicação',
                        dataIndex: 'publicacao',
                        width: 300,
                        id: 'publicacao'
                    },
                    {
                        header: 'Data Início',
                        dataIndex: 'data_inicio',
                        width: 150,
                    },
                    {
                        header: 'Data Fim',
                        dataIndex: 'data_fim',
                        width: 150,
                    }

                    
                    ]),
                'listeners': {
                    'scope': this,
                    'render': function(grid) {
                        new Ext.LoadMask(grid.getEl(), {
                            'store': grid.getStore(),
                            'msg': 'Carregando dados...'
                        });

                        grid.getStore().load({});
                    },
                    dblclick: function() {
                        this.getSelectionModel().getSelected() && this._update()
                    }
                }
            });

            toolkit.questionario.QuestionarioGrid.superclass.constructor.call(this, cfg);
        },

        getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    proxy: new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'list'),
                        // 'method': 'GET',
                        'disableCaching': false
                    }),
                    baseParams:{
                        start:0,
                        limit:50
                    },
                    reader: new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                        'pk',
                        'comissao_anterior',
                        'publicacao',
                        'data_inicio',
                        'data_fim',
                        ]
                    })
                });
        
            return this._store;
        },

        _create: function() {
            new toolkit.gep.comissaoForm({
                'action': 'create',
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                }
            }).show();
        },

        _update: function() {
            var sel = this.getSelectionModel().getSelected();
            if(sel) {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'get_list'),
                    params:{
                        'pk_comissao':sel.get('pk')
                    },
                    scope: this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        
                        if(obj.success) {
                            new toolkit.gep.comissaoForm({
                                'action': 'update',
                                'params': {
                                    'pk_comissao': sel.get('pk')
                                }, 
                                'values': obj.collection,
                                'callback': {
                                    'success': {
                                        'scope': this,
                                        'handler': function() {
                                            this.getStore().reload()
                                        }
                                    }
                                }
                            }).show();
                        }
                    },
                    'failure': function(request) {
                        Ext.Msg.show({
                            'title': 'Comissão',
                            'message': 'Erro tentando editar o item selecionado.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Comissão',
                'msg': 'Primeiro selecione o item que deseja alterar.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _remove: function() {
            var sels = this.getSelectionModel().getSelections();
            var pks = []
            if (sels.length > 0){
                Ext.each(sels, function(record) {
                    pks.push(record.get('pk'))
                });

                Ext.Msg.show({
                    'title': 'Comissão',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'remove'),
                            'params': {
                                pk: pks
                            },
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);
                                if(obj.success) 
                                {
                                    Ext.Msg.alert('Sucesso', 'Dados removidos com sucesso!');
                                    this.getStore().reload();
                                }else{
                                    Ext.Msg.show({
                                        'title': 'Atenção!',
                                        'msg': obj.message,
                                        'icon': Ext.Msg.WARNING,
                                        'buttons': Ext.Msg.OK
                                    });
                                }
                            },
                            'failure': function(request) {
                                this.getStore().reload();
                                Ext.Msg.show({
                                    'title': 'Comissão',
                                    'msg': 'Ocorreram erros removendo os itens selecionados.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Comissão',
                'msg': 'Primeiro selecione o item que deseja remover.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        getToolbar: function() {
            if(!this._toolbar)
                this._toolbar = new Ext.Toolbar({
                    'style': 'border-left:none;border-top:none',
                    'items': [
                    {
                        'text': 'Novo',
                        'scope': this,
                        'handler': this._create,
                        'iconCls': 'icon-gep icon-new'
                    },
                    {
                        'text': 'Editar',
                        'scope': this,
                        'handler': this._update,
                        'iconCls': 'icon-gep icon-edit'
                    },
                    {
                        'text': 'Remover',
                        'scope': this,
                        'handler': this._remove,
                        'iconCls': 'icon-gep icon-delete'
                    },
                    '-'
                    ]   
                });
        
            return this._toolbar;
        },

        getPagingToolbar: function() {
            if(!this._pagingToolbar)
                this._pagingToolbar = new Ext.PagingToolbar({
                    'style': 'border-left:none',
                    'store': this.getStore(),
                    'pageSize':15,
                    'displayInfo': true
                });
        
            return this._pagingToolbar;
        }

    }
    );
