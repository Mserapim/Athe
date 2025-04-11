
Ext.ns('toolkit.rh.servidor.provimentos');

Ext.apply(
    toolkit.rh.servidor.provimentos,
    {
        GestorProvimentos: Ext.extend(toolkit.rh.utils.CustomGridPanel,{
            constructor: function(args) {
                this.layout_show = args.layou_show;
                this.servidor = args.servidor;
                var cf = {
                    title: 'Provimentos',
                    layout: 'fit',
                    searchable: true,
                    border: false,
                    toSearch: [
                        {dataIndex: 'quadro', header: 'Cargo', sortable: false, width: 250}
                    ],
                    pageSize: 50,
                    controller: 'RHGestorProvimentos',
                    readerFields: [
                        {name: 'pk'},
                        {name: 'quadro'},
                        {name: 'tipo_cargo'},
                        {name: 'data_exercicio'},
                        {name: 'data_desligamento'},
                        {name: 'provimento'},
                        {name: 'status'},
                        {name: 'publicacao_link'},
                        {name: 'desligamento_publicacao_link'},
                        {name: 'controller'},
                        {name: 'desligamento'},
                        {name: 'controller_desligamento'},
                        {name: 'dados_desligamento'},
                        {name: 'dados_provimento'},
                        {name: 'bond'}
                    ],
                    listeners: {
                        scope: this,
                        dblclick: function() {
                            new toolkit.rh.utils.ExtCrudCall({
                                controller: this.getSelectionModel().getSelected().get("controller"),
                                pk: this.getSelectionModel().getSelected().get("pk"),
                                tipo: 'EDIT',
                                fields: [
                                    { name: "servidor", enabled: false }
                                ],
                                store: this.getStore()
                            }).call();
                        },
                        beforeshow: function(component){
                            this.getStore().reload();
                        }
                    }
                };
                toolkit.rh.servidor.provimentos.GestorProvimentos.superclass.constructor.call(this, cf);
            },

            getStore: function(){
                if(!this.storeGridPanel){
                        this.storeGridPanel = new Ext.data.Store({
                            id: 'store',
                            autoLoad: true,
                            proxy: this.getProxy(),
                            reader: this.getReader(),
                            writer: this.getWriter(),
                            autoSave: true,
                            baseParams: {
                                servidor: this.servidor,
                                tipoServidor: '',
                                onlyAfastamento: true,
                                onlyAusencia: true,
                                onlyFerias: true,
                                onlyLicenca: true,
                                onlyRecesso: true,
                                onlyViagem: true,
                                onlyAtivo: true,
                                onlyAgendado: true,
                                onlyCancelado: false,
                                onlyEncerrado: true
                            }
                        });
                    if(this.cf.readerFields[0].name == '_pk')
                        this.storeGridPanel.loadData({"totalRows": 11, "result": [{'_pk':'1', '_nome':'Fulano'},{'_pk':'2', '_nome':'Cicrano'}]});
                }
                return this.storeGridPanel;
            },

            getColumnModel: function(){
                if(!this.colModelGridPanel){
                    this.colModelGridPanel = new Ext.grid.ColumnModel({
                        columns: [
                            {header: "Código", sortable: true, dataIndex: "pk", key: "pk", id: "pk", width: 50},
                            {
                                align: 'center',
                                header: 'Ativo',
                                dataIndex: 'status',
                                id: 'status',
                                width: 40,
                                menuDisabled: true,
                                renderer: toolkit.util.formatStatus
                            },
                            {header: "Cargo", sortable: true, dataIndex: "quadro", key: "quadro", id: "quadro", width: 370},
                            {align: 'center', header: "Publicação", sortable: true, dataIndex: "dados_provimento", key: "dados_provimento", id: "dados_provimento", width: 140},
                            {
                                align: 'center',
                                header: 'Arq.',
                                dataIndex: 'publicacao_link',
                                id: 'publicacao_link',
                                width: 30,
                                menuDisabled: true,
                                renderer: toolkit.util.formatLinks
                            },
                            {align: 'center', header: "Provimento", sortable: true, dataIndex: "provimento", key: "provimento", id: "provimento", width: 80},
                            {align: 'center', header: "Tipo", sortable: true, dataIndex: "tipo_cargo", key: "tipo_cargo", id: "tipo_cargo", width: 35},
                            {align: 'center', header: "Exercício", sortable: true, dataIndex: "data_exercicio", key: "data_exercicio", id: "data_exercicio", width: 80},
                            {header: "Desligamento", sortable: true, dataIndex: "data_desligamento", key: "data_desligamento", id: "data_desligamento", width: 80},
                            {align: 'center', header: "Publicação Desligamento", sortable: true, dataIndex: "dados_desligamento", key: "dados_desligamento", id: "dados_desligamento", width: 140},
                            {
                                align: 'center',
                                header: 'Arq. Desligamento',
                                dataIndex: 'desligamento_publicacao_link',
                                id: 'desligamento_publicacao_link',
                                width: 130,
                                menuDisabled: true,
                                renderer: toolkit.util.formatLinks
                            },
                            {
                                align: 'center',
                                header: 'Gera vínculo',
                                dataIndex: 'bond',
                                id: 'bond',
                                width: 130,
                                menuDisabled: true,
                                renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }
                            }

                        ]
                    });
                }
                return this.colModelGridPanel;
            },

            getMenuNovo: function(){
                if(!this.gridMenuNovo){
                    this.gridMenuNovo = new Ext.menu.Menu({
                        id: 'menuNovo',
                        split: true,
                        defaultStyle: 'splitbutton',
                        style: { overflow: 'visible' },
                        scope: this,
                        items: [
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Aproveitamento---',
                                controller: 'RHMovimentacaoAproveitamento',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Nomeação',
                                controller: 'RHMovimentacaoPosse',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Promoção',
                                controller: 'RHMovimentacaoPromocao',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Readaptação',
                                controller: 'RHMovimentacaoReadaptacao',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Recondução',
                                controller: 'RHMovimentacaoReconducao',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Reintegração',
                                controller: 'RHMovimentacaoReintegracao',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Remoção',
                                controller: 'RHMovimentacaoRemocaoMembro',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Reversão',
                                controller: 'RHMovimentacaoReversao',
                                scope: this,
                                store: this.getStore()
                            }),
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Titularização',
                                controller: 'RHMovimentacaoTitularizacao',
                                scope: this,
                                store: this.getStore()
                            }),
                            '-',
                            new toolkit.rh.servidor.provimentos.CustomActionCrud({
                                text: 'Benefício',
                                controller: 'RHMovimentacaoTitularizacao',
                                scope: this,
                                store: this.getStore()
                            })
                        ]
                    });
                    return this.gridMenuNovo;
                }
            },

            setFilter: function() {
                var store = this.getStore();
                var fields = [];

                if (this.fieldsToSearch.menu)
                    this.fieldsToSearch.menu.items.each(
                        function(item) {
                            if (item.checked) fields.push(item.dataIndex);
                        }
                    );

                var keyword = this.findText.getValue();

                if (keyword != undefined && keyword != '') {
                    store.baseParams.keyword = keyword;
                    if (fields.length > 0) store.baseParams.toSearch = fields;
                }
                else {
                    store.baseParams.keyword = undefined;
                    store.baseParams.toSearch = undefined;
                }
                var dataInicio = Ext.util.Format.date(this.dataExercicioFind.getValue());
                var dataFim = Ext.util.Format.date(this.dataDesligamentoFind.getValue());
                if (dataInicio != undefined && dataInicio != '')
                    store.baseParams.dataInicio = dataInicio;
                else
                    store.baseParams.dataInicio = undefined;
                if (dataFim != undefined && dataFim != '')
                    store.baseParams.dataFim = dataFim;
                else
                    store.baseParams.dataFim = undefined;

                store.reload({params: {start: 0}});
            },

            getToolbar: function(cf) {
                if (!this.toolbar) {
                    this.toolbar = this.getToolbarClass();
                }
                return this.toolbar;
            },

            getToolbarClass: function(){
                this.dataExercicioFind = new Ext.form.DateField({
                    emptyText: 'Exercício',
                    format: 'd/m/Y',
                    id: 'data_exercicio',
                    width: 90,
                    enableKeyEvents: true,
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });
                this.dataDesligamentoFind = new Ext.form.DateField({
                    emptyText: 'Desligamento',
                    format: 'd/m/Y',
                    id: 'data_desligamento',
                    width: 90,
                    enableKeyEvents: true,
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });
                return [
                    {
                        text:'Novo',
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/add.png",
                        menu: this.getMenuNovo()
                    },
                    '-',
                    {
                        text: 'Editar',
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/edit.png",
                        handler: function() {
                            new toolkit.rh.utils.ExtCrudCall({
                                controller: this.getSelectionModel().getSelected().get("controller"),
                                pk: this.getSelectionModel().getSelected().get("pk"),
                                tipo: 'EDIT',
                                fields: [{ name: "servidor", enabled: false }],
                                store: this.getStore()
                            }).call();
                        },
                        scope: this
                    },
                    '-',
                    {
                        text:'Apagar',
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/delete.png",
                        scope: this,
                        handler: function() {
                            if(this.getSelectionModel().getSelected()){
                                var id = this.getSelectionModel().getSelected().get("pk");
                                var fn = function(bnt, text, opts) {
                                    if(bnt == "yes") {
                                        var obj = toolkit.util.Ajax.request_json(
                                            "POST",
                                            toolkit.util.Normalize.controller_action(
                                                this.getSelectionModel().getSelected().get("controller"),
                                                "commit",
                                                ["DELETE", id, 0])
                                        );
                                        var store = this.getStore();
                                        setTimeout(function() { store.load(); }, 100);
                                    }
                                    else if(bnt == "no") {
                                        new toolkit.rh.utils.ExtCrudCall({
                                            controller: this.getSelectionModel().getSelected().get("controller"),
                                            pk: this.getSelectionModel().getSelected().get("pk"),
                                            tipo: 'DELETE',
                                            fields: [{ name: "servidor", enabled: false }],
                                            store: this.getStore()
                                        }).call();
                                    }
                                    else {
                                        Ext.MessageBox.show({
                                            title: "Sistema Administrativo",
                                            msg : "A ação de remoção foi cancelada.",
                                            buttons: Ext.MessageBox.OK,
                                            icon: Ext.MessageBox.INFO
                                        });
                                    }
                                };

                                Ext.MessageBox.show({
                                    title: "ManagerNetWork",
                                    msg : "Tem certeza que deseja remover o item com id " + id + ", \n\
                                        caso não tenha certeza clique em <b>Não</b> para visualizar os dados. \n\
                                        <b>TODAS substituições</b> agendadas para este afastamento serão apagadas!",
                                    fn : fn,
                                    scope: this,
                                    buttons: Ext.MessageBox.YESNOCANCEL,
                                    icon: Ext.MessageBox.QUESTION
                                });
                            }else{ alert('Escolha um Afastamento!');}
                        }
                    },
                    '-',
                    {
                        text: 'Desligar',
                        iconCls: 'icon-fopag icon-user-inactive',
                        scope: this,
                        menu: new Ext.menu.Menu({
                            id: 'menuNovo',
                            split: true,
                            defaultStyle: 'splitbutton',
                            style: { overflow: 'visible' },
                            scope: this,
                            items: [
                                {
                                    text: 'Desligar',
                                    handler: function() {
                                        if(this.getSelectionModel().getSelected() && (this.getSelectionModel().getSelected().get("desligamento") == '' ||
                                                this.getSelectionModel().getSelected().get("desligamento") == undefined)){
                                            new toolkit.rh.utils.ExtCrudCall({
                                                controller: 'RHMovimentacaoDesligamento',
                                                fields: [{ name: "movimentacao_posse", enabled: false, value: this.getSelectionModel().getSelected().get("pk") }],
                                                store: this.getStore()
                                            }).call();
                                        }else alert('Este provimento já possui um desligamento!');
                                    },
                                    scope: this
                                },
                                {
                                    text: 'Aposentar',
                                    handler: function() {
                                        if(this.getSelectionModel().getSelected() && (this.getSelectionModel().getSelected().get("desligamento") == '' ||
                                                this.getSelectionModel().getSelected().get("desligamento") == undefined)){
                                            new toolkit.rh.utils.ExtCrudCall({
                                                controller: 'RHMovimentacaoAposentadoria',
                                                fields: [{ name: "movimentacao_posse", enabled: false, value: this.getSelectionModel().getSelected().get("pk") }],
                                                store: this.getStore()
                                            }).call();
                                        }else alert('Este provimento já possui um desligamento!');
                                    },
                                    scope: this
                                }
                            ]
                        })
                    },
                    '-',
                    {
                        text:'Remover Desligamento',
                        iconCls: 'icon-fopag icon-user-active',
                        scope: this,
                        handler: function() {
                            if(this.getSelectionModel().getSelected() && this.getSelectionModel().getSelected().get("desligamento") != '' &&
                                    this.getSelectionModel().getSelected().get("desligamento") != undefined){
                                var id = this.getSelectionModel().getSelected().get("desligamento");
                                var fn = function(bnt, text, opts) {
                                    if(bnt == "yes") {
                                        var obj = toolkit.util.Ajax.request_json(
                                            "POST",
                                            toolkit.util.Normalize.controller_action(
                                                "RHMovimentacaoDesligamento",
                                                "commit",
                                                ["DELETE", id, 0])
                                        );
                                        var store = this.getStore();
                                        setTimeout(function() { store.load(); }, 100);
                                    }
                                    else if(bnt == "no") {
                                        new toolkit.rh.utils.ExtCrudCall({
                                            controller: 'RHMovimentacaoDesligamento',
                                            pk: id,
                                            tipo: 'DELETE',
                                            fields: [{ name: "servidor", enabled: false }]
                                        }).call();
                                    }
                                    else {
                                        Ext.MessageBox.show({
                                            title: "Sistema Administrativo",
                                            msg : "A ação de remoção foi cancelada.",
                                            buttons: Ext.MessageBox.OK,
                                            icon: Ext.MessageBox.INFO
                                        });
                                    }

                                };

                                Ext.MessageBox.show({
                                    title: "ManagerNetWork",
                                    msg : "Tem certeza que deseja remover o item com id " + id + ", \n\
                                        caso não tenha certeza clique em <b>Não</b> para visualizar os dados. \n\
                                        <b>TODAS substituições</b> agendadas para este afastamento serão apagadas!",
                                    fn : fn,
                                    scope: this,
                                    buttons: Ext.MessageBox.YESNOCANCEL,
                                    icon: Ext.MessageBox.QUESTION
                                });
                            }else{ alert('Escolha um provimento que possua desligamento!');}
                        }
                    },
                    '-',
                    {
                        text: 'Mostrar Desligamento',
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/edit.png",
                        handler: function() {
                            if(this.getSelectionModel().getSelected() &&
                                this.getSelectionModel().getSelected().get("desligamento") != '' &&
                                    this.getSelectionModel().getSelected().get("desligamento") != undefined){
                                new toolkit.rh.utils.ExtCrudCall({
                                    controller: this.getSelectionModel().getSelected().get("controller_desligamento"),
                                    pk: this.getSelectionModel().getSelected().get("desligamento"),
                                    tipo: 'EDIT',
                                    fields: [{ name: "movimentacao_posse", enabled: false }],
                                    store: this.getStore()
                                }).call();
                            }else{ alert('Escolha um provimento que possua desligamento!');}
                        },
                        scope: this
                    }
                ];
            }
        }),

        CustomActionCrud: Ext.extend(Ext.Action,{
            constructor: function(cf) {
                cf.fields = [{ name: "servidor", enabled: false, value: cf.scope.servidor }];
                cf.handler = function(){
                    new toolkit.rh.utils.ExtCrudCall(cf).call();
                };
                toolkit.rh.servidor.provimentos.CustomActionCrud.superclass.constructor.call(this, cf);
            }
        })
    }
);