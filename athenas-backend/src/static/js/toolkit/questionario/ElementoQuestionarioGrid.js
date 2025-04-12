Ext.ns('toolkit.questionario');

toolkit.questionario.ElementoQuestionarioGrid = Ext.extend(

    Ext.grid.GridPanel,
    {
        _getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('QElemento', 'list'),
                        'disableCaching': false,
                        'method': 'GET'
                    }),
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

        _update: function() {
            var sel = this.getSelectionModel().getSelected();

            if(sel) {
                var tipo = sel.get('tipo');
                var url;
                var instancia;

                if(tipo == 'Ref. Textual'){
                    url = toolkit.util.Normalize.controller_action('QReferenciaTextual', 'get', [sel.get('pk')]);
                    instancia = toolkit.questionario.ReferenciaTextualForm;

                }else if(tipo == 'Questão Enum')
                {
                    url = toolkit.util.Normalize.controller_action('QQuestaoEnum', 'get', [sel.get('pk')]);
                    instancia = toolkit.questionario.QuestaoEnumForm;
                }else //if(tipo == 'Questao')
                {
                    url = toolkit.util.Normalize.controller_action('QQuestao', 'get', [sel.get('pk')]);
                    instancia = toolkit.questionario.QuestaoForm;
                }
                Ext.Ajax.request({
                    'url':url,
                    'scope': this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(obj.success) {
                            new instancia({
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
                            }, this.questionario).show();
                        }
                    },
                    'failure': function(request) {
                        Ext.Msg.show({
                            'title': 'Questão',
                            'msg': 'Erro tentando editar o item selecionado.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Questão',
                'msg': 'Primeiro selecione o item que deseja alterar.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _remove: function() {
            var sels = this.getSelectionModel().getSelections();
            var pks = []
            var pks_quest_reftext = [] 
            var tipo = []
            //console.log(sels)
            if (sels.length > 0){
                Ext.each(sels, function(record) {
                    pks.push(record.get('pk_element'))
                    pks_quest_reftext.push(record.get('pk')) //recupera a pk da questao ou da referencia textual
                    tipo.push(record.get('tipo'))
                });

                Ext.Msg.show({
                    'title': 'Questões/Referências Textuais',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('QElemento', 'remove'),
                            'params': {
                                pk: pks, 
                                pk2:pks_quest_reftext,
                                tipo:tipo
                            },// envia a pk do elemento e da questao ou referencia textual
                            'success': function(request) {
                                this.getStore().reload();
                            },
                            'failure': function(request) {
                                this.getStore().reload();
                                Ext.Msg.show({
                                    'title': 'Questões/Referências Textuais',
                                    'msg': 'Ocorreram erros removendo os itens selecionados.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                })
            } else  Ext.Msg.show({
                'title': 'Questão',
                'msg': 'Primeiro selecione o item que deseja remover.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _move: function(direction) {
            var sels = this.getSelectionModel().getSelections();
            var pks = []
            var pks_quest_reftext = [] // vai armazenar a pk da questao ou da referencia textual

            if(sels.length > 0) {
                Ext.each(sels, function(record) {
                    pks.push(record.get('pk_element'))
                    pks_quest_reftext.push(record.get('pk')) //recupera a pk da questao ou da referencia textual
                });

                Ext.Ajax.request({
                    'scope': this,
                    'url': toolkit.util.Normalize.controller_action('QElemento', 'move_questao',[direction]),
                    'params': {
                        pk: pks, 
                        pk2:pks_quest_reftext
                    },// envia a pk do elemento e da questao ou referencia textual
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

        createRefTextual: function() {
            new toolkit.questionario.ReferenciaTextualForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create'
            }).show();
        },
        
        createQuestao: function() {
            new toolkit.questionario.QuestaoForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create'
            }, this.questionario).show();
        },

        createQuestaoEnum: function() {
            new toolkit.questionario.QuestaoEnumForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create'
            }, this.questionario).show();
        },

        createQuestaoMS: function() {
            new toolkit.questionario.QuestaoMSForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create'
            }, this.questionario).show();
        },

        createQuestaoAberta: function() {
            new toolkit.questionario.QuestaoAbertaForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create'
            }, this.questionario).show();
        },

        createQuestaoCertoErrado: function() {
            new toolkit.questionario.QuestaoCertoErradoForm({
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                },
                'params': this.getStore().baseParams,
                'action': 'create_c_e'
            }, this.questionario).show();
        },

        getManagerActionsSubMenu: function(){
            return [
            {
                'text': 'Questão',
                'scope': this,
                'handler': this.createQuestao
            },
            {
                'text': 'Questão Enumerada',
                'scope': this,
                'handler': this.createQuestaoEnum
            },
            {
                'text': 'Questão Multipla Seleção',
                'scope': this,
                'handler': this.createQuestaoMS
            },
            {
                'text': 'Questão Aberta',
                'scope': this,
                'handler': this.createQuestaoAberta
            },
            {
                'text': 'Questão ex:(Certo/Errado)',
                'scope': this,
                'handler': this.createQuestaoCertoErrado
            }

            ]
        },

        getManagerActions: function() {
            return [
            {
                'text': 'Questão',
                'scope': this,
                'menu':this.getManagerActionsSubMenu()
            },
            {
                'text': 'Referência Textual',
                'scope': this,
                'handler': this.createRefTextual
            }
            ]
        },

        getToolbar: function() {
            if(!this._toolbar)
                this._toolbar = new Ext.Toolbar({
                    'style': 'border-top:none;border-right:none',
                    'items': [
                    {
                        'text': 'Novo',
                        'iconCls': 'icon-diarias icon-add',
                        'menu': this.getManagerActions()
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
                        'handler': function() {
                            this._move('up')
                        }
                    },
                    {
                        'text': 'Abaixo',
                        'iconCls': 'icon-gep icon-down',
                        'scope': this,
                        'handler': function() {
                            this._move('down')
                        }
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
                    'pageSize':5,
                    'displayInfo': true
                });
        
            return this._pagingToolbar;
        },

        getParams: function(param){
            this.questionario = param;
            return param
        },

        constructor: function(cfg) {

            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title':'Questões/Referências Textuais',
                'tbar': this.getToolbar(),
                'bbar': this.getPagingToolbar(),
                'store': this._getStore(),
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

            toolkit.questionario.ElementoQuestionarioGrid.superclass.constructor.call(this, cfg);

            this.on('render', function(panel) {
                var store = panel.getStore();

                new Ext.LoadMask(panel.getEl(), {
                    'msg': 'Carregando Questões...',
                    'store': store
                });
            });
        }
    }
    );