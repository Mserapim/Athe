Ext.ns('toolkit.gep');

toolkit.gep.IntegrantesComissao = Ext.extend(

    Ext.grid.GridPanel,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title':'Integrantes da Comissão',
                'tbar': this.getToolbar(),
                // 'bbar': this.getPagingToolbar(),
                'store': this.getStore(),
                // 'autoExpandColumn': 'autoExpand',
                'cm': new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        'header': 'Nome do Integrante',
                        'dataIndex': 'nome_integrante',
                        'id': 'autoExpand',
                        'width':500
                    },
                    {
                        'header': 'Função',
                        'dataIndex': 'funcao',
                        'width': 300
                    },
                    {
                        'header': 'Impedimento',
                        'dataIndex': 'impedimento',
                        'width': 300
                    }
                    ])
            });

            toolkit.gep.IntegrantesComissao.superclass.constructor.call(this, cfg);

        },

        getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'get_integrantes'),
                        'disableCaching': false,
                        'method': 'GET'
                    }),
                    'reader': new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                            'pk',
                            'pk_comissao',
                            'pk_integrante',
                            'nome_integrante',
                            'funcao',
                            'tipo_integrante',
                            'impedimento',
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
            var pk_comissao = this.getParams().pk_comissao;
            // var pk_questionario = this.getParams().pk_questionario;

            new toolkit.gep.IntegranteComissaoForm({
                'action': 'create_integrante',
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                }
            }, pk_comissao).show();
        },

        _update: function() {
            var sel = this.getSelectionModel().getSelected();
            if(sel) {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'get_list_integrantes'),
                    params:{
                        'pk_comissao':sel.get('pk_comissao'),
                        'pk_integrante':sel.get('pk_integrante'),
                        'tipo_integrante':sel.get('tipo_integrante'),

                    },
                    scope: this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        
                        if(obj.success) {
                            new toolkit.gep.IntegranteComissaoForm({
                                'action': 'update_integrantes',
                                'params': {
                                    'pk_comissao_servidor': sel.get('pk')
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
                            'title': 'Integrantes da Comissão',
                            'message': 'Erro tentando editar o item selecionado.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Integrantes da Comissão',
                'msg': 'Primeiro selecione o item que deseja alterar.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _remove: function() {
            var sels = this.getSelectionModel().getSelections();
            var pk_integrante = []
            var pk_comissao = []
            var tipo_participante = []

            if (sels.length > 0){
                Ext.each(sels, function(record) {
                    pk_integrante.push(record.get('pk_integrante'))
                    pk_comissao.push(record.get('pk_comissao'))
                    tipo_participante.push(record.get('tipo_integrante'))
                });

                Ext.Msg.show({
                    'title': 'Integrantes da Comissão',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'remove_integrante'),
                            'params': {
                                pk_integrante: pk_integrante,
                                pk_comissao: pk_comissao,
                                tipo_participante: tipo_participante
                            },
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);

                                if(obj.success){
                                    Ext.Msg.alert('Sucesso', 'Dados removidos com sucesso!');
                                    this.getStore().reload();
                                }else{
                                    Ext.Msg.show({
                                        'title': 'Atenção',
                                        'msg': 'Ocorreu um erro ao remover os itens.',
                                        'icon': Ext.Msg.WARNING,
                                        'buttons': Ext.Msg.OK
                                    });

                                }
                            },
                            'failure': function(request) {
                                this.getStore().reload();
                                Ext.Msg.show({
                                    'title': 'Integrantes da Comissão',
                                    'msg': 'Ocorreram erros removendo os itens selecionados.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                })
            } else  Ext.Msg.show({
                'title': 'Integrantes da Comissão',
                'msg': 'Primeiro selecione o item que deseja remover.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _move: function(direction) {
            var sel = this.getSelectionModel().getSelected();

            if(sel) {
                Ext.Ajax.request({
                    'scope': this,
                    'url': toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', 'move_integrante',[direction]),
                    'params': {
                        pk: sel.get('pk'), 
                    },
                    'success': function(request) {
                        this.getStore().reload();
                    },
                    'failure': function(request) {
                        this.getStore().reload();
                        Ext.Msg.show({
                            'title': 'Integrantes da Comissão',
                            'msg': 'Ocorreram erros na ordenação dos itens selecionados.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                });
            }else  Ext.Msg.show({
                'title': 'Integrantes da Comissão',
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
                            'iconCls': 'icon-gep icon-new',
                            'scope': this,
                            'handler': this._create
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
                        ,
                        {
                            'text': 'Acima',
                            'scope': this,
                            'handler': function() {
                                this._move('up')
                            },
                            'iconCls': 'icon-gep icon-up'
                        },
                        {
                            'text': 'Abaixo',
                            'scope': this,
                            'handler': function() {
                                this._move('down')
                            },
                            'iconCls': 'icon-gep icon-down'
                        }
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