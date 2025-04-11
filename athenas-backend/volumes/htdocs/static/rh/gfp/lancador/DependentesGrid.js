Ext.ns('toolkit.gfp');

toolkit.gfp.DependentesGrid = Ext.extend(
    Ext.grid.GridPanel,
    {
        constructor: function(cfg, cf){
            this.cf = cf;
            Ext.apply(cfg, {
                title:'Dependentes',
                tbar: this.getToolbar(),
                bbar: this.getPagingToolbar(),
                store: this.getStore(),
                columnLines: true,
                autoExpandColumn: 'autoExpand',
                cm: new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        header: 'Nome',
                        dataIndex: 'nome',
                        width: 250,
                    id: 'autoExpand'
                    },
                    {
                        header: 'Tipo Parentesco',
                        dataIndex: 'status',
                        width: 100,
                    },
                    {
                        header: 'Idade',
                        dataIndex: 'idade',
                        width: 80,
                    },
                    {
                        header: 'Data Nascimento',
                        dataIndex: 'dt_nascimento',
                        width:100
                    },
                    {
                        header: 'Data Início',
                        dataIndex: 'data_inicio',
                        width:100
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

            toolkit.gfp.DependentesGrid.superclass.constructor.call(this, cfg);
        },

        getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    proxy: new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('GFPLancador', 'dependentes'),
                        'disableCaching': false
                    }),
                    baseParams:{
                        start:0,
                        limit:5,
                        servidor:this.cf.servidor,
                        date:this.cf.date
                    },
                    reader: new Ext.data.JsonReader({
                        'totalProperty': 'totalRows',
                        'root': 'root',
                        'fields': ['pk', 'nome', 'ir', 'sf', 'ac', 'status', 'idade', 'dt_nascimento','tipo_parentesco','data_inicio']
                    }),
                });
        
            return this._store;
        },

        _create: function() {
            new toolkit.gfp.DependenteForm({
                'action': 'create',
                'params': {
                    'servidor': this.cf.servidor
                }, 
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
                    url: toolkit.util.Normalize.controller_action('RHDependente', 'get_list'),
                    params:{
                        'pk':sel.get('pk')
                    },
                    scope: this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        
                        if(obj.success) {
                            new toolkit.gfp.DependenteForm({
                                'action': 'update',
                                'params': {
                                    'pk': sel.get('pk')
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
                            'title': 'Dependente',
                            'message': 'Erro tentando editar o item selecionado.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Dependente',
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
                    'title': 'Dependente',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('RHDependente', 'remove'),
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
                                    'title': 'Dependente',
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
                'title': 'Dependente',
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
                    'pageSize':5,
                    'displayInfo': true
                });
        
            return this._pagingToolbar;
        }
    }
);

toolkit.gfp.DependenciaGrid = Ext.extend(

    Ext.grid.GridPanel,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title':'Dependências',
                'tbar': this.getToolbar(),
                // 'bbar': this.getPagingToolbar(),
                'store': this.getStore(),
                'autoExpandColumn': 'autoExpand',
                'cm': new Ext.grid.ColumnModel([
                    new Ext.grid.RowNumberer(),
                    {
                        header: "Status", 
                        sortable: false, 
                        dataIndex: "status", 
                        key: "status", 
                        // id: "status",
                        width: 40, 
                        renderer: toolkit.util.formatStatus
                    },
                    {
                        'header': 'Tipo',
                        'dataIndex': 'tipo',
                        'id': 'autoExpand'
                    },
                    {
                        'header': 'Data Início',
                        'dataIndex': 'data_inicio',
                        'width': 100
                    },
                    {
                        'header': 'Data Fim',
                        'dataIndex': 'data_fim',
                        'width': 100
                    },
                    {
                        'header': 'Idade Limite',
                        'dataIndex': 'idade_limite',
                        'width': 100
                    },
                    {
                        'header': 'Estudante',
                        'dataIndex': 'estudante',
                        'width': 100
                    },
                    {
                        'header': 'Suspenso',
                        'dataIndex': 'suspenso',
                        'width': 100
                    },
                ]),
                'listeners': {
                    'scope': this,
                    dblclick: function() {
                        this.getSelectionModel().getSelected() && this._update()
                    }
                }
            });

            toolkit.gfp.DependenciaGrid.superclass.constructor.call(this, cfg);

        },

        getStore: function() {
            if(!this._store)
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action('GFPLancador', 'dependencias'),
                        'disableCaching': false,
                        'method': 'GET'
                    }),
                    'reader': new Ext.data.JsonReader({
                        'totalProperty': 'totalRows',
                        'root': 'root',
                        'fields': [
                            'pk',
                            'pk_dependente',
                            'tipo',
                            'data_inicio',
                            'data_fim',
                            'status', 
                            'idade_limite',
                            'estudante',
                            'suspenso',
                            'status' 
                        ]
                    })
                });
        
            return this._store;
        },

        getParams: function(){
            var obj = this.getStore().baseParams;
            return obj;
        },

        _create: function(){
            var pk = this.getParams().pk;
            // console.log(this.getParams());
            new toolkit.gfp.DependenciaForm({
                'action': 'create',
                'params': {
                    'dependencia': pk
                }, 
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
                    url: toolkit.util.Normalize.controller_action('RHDependencia', 'get_list'),
                    params:{
                        'pk':sel.get('pk'),
                        'pk_dependente':sel.get('pk_dependente')
                    },
                    scope: this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        
                        if(obj.success) {
                            new toolkit.gfp.DependenciaForm({
                                'action': 'update',
                                'params': {
                                    'pk': sel.get('pk')
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
                            'title': 'Dependente',
                            'message': 'Erro tentando editar o item selecionado.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        })
                    }
                })
            }
            else Ext.Msg.show({
                'title': 'Dependente',
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
                    'title': 'Dependências',
                    'msg': 'Tem certeza que deseja remover os itens selecionados.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            'scope': this,
                            'url': toolkit.util.Normalize.controller_action('RHDependencia', 'remove'),
                            'params': {
                                pk: pks,
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
                                    'title': 'Dependências',
                                    'msg': 'Ocorreram erros removendo os itens selecionados.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                })
            } else  Ext.Msg.show({
                'title': 'Dependências',
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

toolkit.gfp.DependenteForm = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title: 'Dependente',
                closable: true,
                resizable: true,
                modal: true,
                width: 550,
                // autoWidth:true,
                border: false,
                buttons: [
                {
                    text: 'Salvar',
                    scope: this,
                    handler: this.save
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: this.destroy
                }
                ]   
            });

            toolkit.gfp.DependenteForm.superclass.constructor.call(this, cfg);
            this.add(this.getFormPanel());
            if(this.values) this.getFormPanel().getForm().setValues(this.values);
            // console.log(this.values)
        },

        getFormPanel: function() {
            if(!this._formPanel)
                this._formPanel = new Ext.form.FormPanel({
                    frame: true,
                    layout: 'fit',
                    resizable: true,
                    border: false,
                    items: [
                        new Ext.TabPanel({
                            width: 500,
                            activeTab: 0,
                            autoHeight:true,
                            border: false,
                            items: [
                                new Ext.Panel({
                                    title: 'Dados Básicos',
                                    defaults: {
                                        width: 450
                                    },
                                    autoHeight:true,
                                    labelWidth: 130,
                                    border: false,
                                    style: 'padding:5pt',
                                    layout: 'form',
                                    items: [
                                        {
                                            displayField: 'description', 
                                            name:'dependente',
                                            fieldLabel: 'Dependente', 
                                            allowBlank: false, 
                                            hiddenName: 'pessoa_fisica', 
                                            valueField: 'pk', 
                                            triggerAction: 'all', 
                                            queryAction: 'query', 
                                            hideTrigger: true, 
                                            queryParam: 'keyword', 
                                            crudController: 'RHPessoaFisica', 
                                            xtype: 'autocompletefield',
                                            width: 350,
                                            conf: {
                                                canAdd: true,
                                                canEdit: true
                                            },
                                        },
                                        {
                                            xtype: 'combo',
                                            width:350,
                                            hiddenName: 'parentesco',
                                            allowBlank:true,
                                            fieldLabel: 'Tipo de Parentesco',
                                            id:'parentesco',
                                            store: [
                                                [1, 'CÔNJUGE'],
                                                [2, 'COMPANHEIRO'],
                                                [3, 'FILHO(A)'],
                                                [4, 'PAI/MÃE'],
                                                [5, 'IRMÃO'],
                                                [6, 'ENTEADO'],
                                                [7, 'MENOR TUTELADO'],
                                                [8, 'EX-CÔNJUGE'],
                                                [9, 'NETOS'],
                                                [10, 'OUTROS'],
                                            ],
                                            triggerAction: 'all',
                                        },
                                        {
                                            xtype: 'combo',
                                            width:350,
                                            allowBlank:false,
                                            hiddenName: 'tipo',
                                            fieldLabel: 'Tipo',
                                            store: [
                                                [1, 'CÔNJUGE'],
                                                [2, 'COMPANHEIRO(A)'],
                                                [3, 'FILHO(A) NÃO EMANCIPADO MENOR DE 21 ANOS'],
                                                [4, 'FILHO INVÁLIDO(A)'],
                                                [5, 'PAI(MÃE) COM DEPENDÊNCIA ECONÔMICA'],
                                                [6, 'IRMÃO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA'],
                                                [7, 'IRMÃO INVÁLIDO COM DEPENDÊNCIA ECONÔMICA'],
                                                [8, 'ENTEADO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA'],
                                                [9, 'ENTEADO INVÁLIDO COM DEPENDÊNCIA ECONÔMICA'],
                                                [10, 'MENOR TUTELADO NÃO EMANCIPADO MENOR DE 21 ANOS COM DEPENDÊNCIA ECONÔMICA'],
                                                [11, 'MENOR TUTELADO INVÁLIDO COM DEPENDÊNCIA ECONÔMICA'],
                                            ],
                                            triggerAction: 'all',                            
                                        },
                                        {
                                            xtype: 'combo',
                                            width:350,
                                            allowBlank:false,
                                            hiddenName: 'capacidade',
                                            fieldLabel: 'Capacidade',
                                            store: [
                                                [1, 'VÁLIDO'],
                                                [2, 'INVÁLIDO'],
                                            ],
                                            triggerAction: 'all',                            

                                        },
                                        {
                                            xtype: 'checkbox',
                                            fieldLabel: 'Recebe Auxílio Creche',
                                            boxLabelAlign:'before',
                                            boxLabel: '',
                                            name: 'auxilio_creche'
                                        },
                                    ]
                                }),
                                new Ext.Panel({
                                    title: 'Informações e Datas',
                                    defaults: {
                                        width: 450
                                    },
                                    autoHeight:true,
                                    labelWidth: 130,
                                    border: false,
                                    style: 'padding:5pt',
                                    layout: 'form',
                                    items: [
                                        {
                                            xtype: 'combo',
                                            width:350,
                                            hiddenName: 'motivo_inicio_dependencia',
                                            fieldLabel: 'Motivo Início Dependência',
                                            store: [
                                                [0, 'OUTROS'],
                                                [1, 'NASCIMENTO'],
                                                [2, 'ADOÇÃO'],
                                                [3, 'FILHO PÓSTUMO'],
                                                [4, 'TUTELA DO MENOR'],
                                                [5, 'DECISÃO JUDICIAL'],
                                                [6, 'IVALIDEZ'],
                                                [7, 'CASAMENTO'],
                                                [8, 'UNIÃO ESTÁVEL'],
                                                [9, 'DEPENDÊNCIA ECONÔMICA'],
                                            ],
                                            triggerAction: 'all',
                                        },
                                        {
                                            allowBlank: true,
                                            width:350,
                                            xtype: 'datefield',
                                            name: 'data_inicio',
                                            fieldLabel: 'Data de Início',
                                        },
                                        {
                                            xtype: 'combo',
                                            width:350,
                                            hiddenName: 'motivo_fim_dependencia',
                                            fieldLabel: 'Motivo Fim Dependência',
                                            store: [
                                                [0, 'OUTROS'],
                                                [1, 'MAIORIDADE'],
                                                [2, 'EMANCIPAÇÃO'],
                                                [3, 'DECISÃO JUDICIAL'],
                                                [4, 'ÓBITO'],
                                                [5, 'SEPARAÇÃO JUDICIAL'],
                                                [6, 'INDEPENDÊNCIA ECONÔMICA'],
                                                [7, 'CESSAÇÃO DE INVALIDEZ'],
                                            ],
                                            triggerAction: 'all',
                                        },
                                        {
                                            allowBlank:true,
                                            width:350,
                                            xtype:'datefield',
                                            name:'data_fim',
                                            fieldLabel:'Data de Fim',
                                        },
                                        {
                                            xtype: 'checkbox',
                                            boxLabel: '',
                                            fieldLabel: 'Imposto de Renda',
                                            name: 'imposto_renda'
                                        },
                                        {
                                            xtype: 'checkbox',
                                            fieldLabel: 'Salário Familia',
                                            boxLabel: '',
                                            name: 'salario_familia'
                                        },
                                        {
                                            xtype: 'checkbox',
                                            fieldLabel: 'Dependente Direto',
                                            boxLabel: '',
                                            name: 'dependente_direto'
                                        }
                                    ]
                                }),
                            ]
                        })
                    ]
                });
        
            return this._formPanel;
        },

        getParams: function() {
            return this.params;
        },

        save: function() {
            var form = this.getFormPanel().getForm();
            form.waitMsgTarget = this.getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action('RHDependente', this.action),
                params: this.getParams(),
                scope: this,
                success: function(form, action) {
                    // this.getStore().reload();
                    if(this.callback && this.callback.success)
                        this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                    Ext.Msg.alert('Sucesso', 'Dados salvos com sucesso!');
                    this.destroy()
                },
                failure: function(form, action) {
                    // console.debug(action);
                    var message = ''
                    if(action.failureType == 'connect')
                        message = 'Não consegui acessar o recurso no servidor.'
                    else
                        message = action.result.message

                    Ext.Msg.show({
                        title: 'Dependente',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });

                    if(this.callback && this.callback.failure)
                        this.callback.failure.handler.call(this.callback.failure.scope ? this.callback.failure.scope : window);
                },
                waitMsg: 'Salvando dados...'
            })
        }
        
    }
);

toolkit.gfp.DependenciaForm = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title: 'Dependência',
                closable: true,
                resizable: true,
                modal: true,
                width: 550,
                // autoWidth:true,
                border: false,
                buttons: [
                {
                    text: 'Salvar',
                    scope: this,
                    handler: this.save
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: this.destroy
                }
                ]   
            });

            toolkit.gfp.DependenteForm.superclass.constructor.call(this, cfg);
            this.add(this.getFormPanel());
            if(this.values) this.getFormPanel().getForm().setValues(this.values);
            // console.log(this.values)
        },

        getFormPanel: function() {
            if(!this._formPanel)
                this._formPanel = new Ext.form.FormPanel({
                    frame: true,
                    resizable: true,
                    border: false,
                    items: [
                        {
                            xtype: 'combo',
                            width:350,
                            hiddenName: 'tipo',
                            allowBlank:false,
                            fieldLabel: 'Tipo',
                            store: [
                                [4, 'AUXÍLIO CRECHE'],
                                [6, 'AUXÍLIO ESPECIAL'],
                                [1, 'IMPOSTO DE RENDA'],
                                [2, 'PLAN SAÚDE'],
                                [5, 'PREVIDÊNCIA'],
                                [3, 'SALÁRIO FAMÍLIA'],
                            ],
                            triggerAction: 'all',
                        },
                        {
                            allowBlank: false,
                            width:350,
                            xtype: 'datefield',
                            name: 'data_inicio',
                            fieldLabel: 'Data de Início',
                        },
                        {
                            allowBlank: true,
                            width:350,
                            xtype: 'datefield',
                            name: 'data_fim',
                            fieldLabel: 'Data de Fim',
                        },
                        {
                            fieldLabel: 'Idade Limite',
                            name: 'idade_limite',
                            width:350,
                            xtype: 'numberfield',
                        },
                        {
                            xtype: 'checkbox',
                            fieldLabel: 'Estudante',
                            boxLabel: '',
                            name: 'estudante'
                        },
                        {
                            xtype: 'checkbox',
                            fieldLabel: 'Suspenso',
                            boxLabel: '',
                            name: 'suspenso'
                        },

                    ]
                });
        
            return this._formPanel;
        },

        getParams: function() {
            return this.params;
        },

        save: function() {
            var form = this.getFormPanel().getForm();
            form.waitMsgTarget = this.getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action('RHDependencia', this.action),
                params: this.getParams(),
                scope: this,
                success: function(form, action) {
                    // this.getStore().reload();
                    if(this.callback && this.callback.success)
                        this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                    Ext.Msg.alert('Sucesso', 'Dados salvos com sucesso!');
                    this.destroy()
                },
                failure: function(form, action) {
                    // console.debug(action);
                    var message = ''
                    if(action.failureType == 'connect')
                        message = 'Não consegui acessar o recurso no servidor.'
                    else
                        message = action.result.message

                    Ext.Msg.show({
                        title: 'Dependência',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });

                    if(this.callback && this.callback.failure)
                        this.callback.failure.handler.call(this.callback.failure.scope ? this.callback.failure.scope : window);
                },
                waitMsg: 'Salvando dados...'
            })
        }
        
    }
);
