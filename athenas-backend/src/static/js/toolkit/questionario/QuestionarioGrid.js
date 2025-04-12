Ext.ns('toolkit.questionario');

toolkit.questionario.QuestionarioGrid = Ext.extend(
    Ext.grid.GridPanel,
    {
        constructor: function(cfg){
            Ext.apply(cfg, {
                'title':'Questionários',
                'tbar': this.getToolbar(),
                'bbar': this.getPagingToolbar(),
                'store': this.getStore(),
                'autoExpandColumn': 'autoExpand',
                'cm': new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        'xtype': 'actioncolumn',
                        'header': '',
                        'width': 30,
                        'scope':this,
                        'items': [
                        {
                            getClass:function(v, meta, rec){ 
                                return rec.get('ativo') ? 'published' : 'non-published';
                            }
                        }
                        ]
                    },
                    {
                        'header': 'Título',
                        'dataIndex': 'titulo',
                        'width': 100,
                        'id': 'autoExpand'
                    },
                    {
                        'header': 'Data Inicio',
                        'dataIndex': 'data_inicio',
                        'width': 100
                    },
                    {

                        'header': 'Data Fim',
                        'dataIndex': 'data_fim',
                        'width': 100
                    },
                    ]),
                'listeners': {
                    'scope': this,
                    'render': function(grid) {
                        new Ext.LoadMask(grid.getEl(), {
                            'store': grid.getStore(),
                            'msg': 'Carregando Questionários...'
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
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('QQuestionario', 'list'),
                        'method': 'GET',
                        'disableCaching': false
                    }),
                    'reader': new Ext.data.JsonReader({
                        'totalProperty': 'count',
                        'root': 'collection',
                        'fields': [
                        'pk',
                        'titulo',
                        'data_inicio',
                        'data_fim',
                        'ativo'
                        ]
                    }),
                    listeners:{
                        load:function()
                        {
                            Ext.select('.published').set({
                                alt:'Ativo',
                                title:'Ativo',
                                src:'/' + global.Context + '/static/images/published.png'
                                });
                            Ext.select('.non-published').set({
                                alt:'Inativo',
                                title:'Inativo',
                                src:'/' + global.Context + '/static/images/no-published.png'
                                });
                        },
                        scope:this
                    }
                });
        
            return this._store;
        },

        _create: function() {
            new toolkit.questionario.Form({
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
                    'url': toolkit.util.Normalize.controller_action('QQuestionario', 'get', [sel.get('pk')]),
                    'scope': this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.success) {
                            new toolkit.questionario.Form({
                                'action': 'update',
                                'params': {
                                    'pk': sel.get('pk')
                                }, 
                                'values': obj.instance,
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
                            'title': 'Questionário',
                            'msg': 'Erro tentando editar o item selecionado.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Questionário',
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
                    'title': 'Questionários',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('QQuestionario', 'remove'),
                            'params': {
                                pk: pks
                            },
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);
                                if(obj.success) 
                                {
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
                                    'title': 'Questionários',
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
                'title': 'Questionário',
                'msg': 'Primeiro selecione o item que deseja remover.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _verResposta: function(){
            var sel = this.getSelectionModel().getSelected();
            if(sel) {
                new toolkit.questionario.VerResposta({
                    'callback': {
                        'success': {
                            'scope': this,
                            'handler': function() {
                                this.getStore().reload()
                            }
                        }
                    }
                },sel.get('pk')).show();
            }
            else Ext.Msg.show({
                'title': 'Questionário',
                'msg': 'Primeiro selecione um questionário.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });

        },

        _montarQuestionario: function() {
            var sel = this.getSelectionModel().getSelected();
            if(sel) {
                Ext.Ajax.request({
                    'url': toolkit.util.Normalize.controller_action('QMontarQuestionario', 'get', [sel.get('pk')]),
                    'scope': this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.collection.length>0) 
                        {
                            new toolkit.questionario.MontaQuestionario({
                                'title':sel.get('titulo'),
                                'action': 'create',
                                'values':obj.collection,
                                'callback': {
                                    'success': {
                                        'scope': this,
                                        'handler': function() {
                                            this.getStore().reload()
                                        }
                                    }
                                }
                            },obj.collection,sel.get('titulo')).show();
                        }else{
                            Ext.Msg.show({
                                'title': 'Atenção!',
                                //'msg': 'Este Questionário não possui questões cadastradas ou está inativo!',
                                'msg': obj.message,
                                'icon': Ext.Msg.WARNING,
                                'buttons': Ext.Msg.OK
                            });
                        }
                    },
                    'failure': function(request) {
                        Ext.Msg.show({
                            'title': 'Questionário',
                            'msg': 'Erro ao exibir o questionário.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Questionário',
                'msg': 'Primeiro selecione um questionário.',
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
                    /*{
                        'text': 'Montar Questionário',
                        'scope': this,
                        'handler': this._montarQuestionario,
                        'iconCls': true,
                        'icon': '/' + global.Context + '/static/images/quest.png'
                    },
                    {
                        'text': 'Ver Resposta',
                        'scope': this,
                        'handler': this._verResposta,
                        'iconCls': true,
                        'icon': '/' + global.Context + '/static/images/document-validate.png'
                    },*/
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
