
if(typeof(toolkit) != "undefined" && typeof(toolkit.iget) == "undefined") {

    toolkit.iget = {

    }

    toolkit.iget.Widget = Ext.extend(Ext.Panel,
        {
            showLoading: function() {

            },

            hideLoading: function() {

            },

            constructor: function(cf) {
                cf.autoScroll = true;

                var old = false;

                if(cf.tbar != undefined) {
                    old = cf.tbar;
                }

                cf.tbar = [
                    {
                        iconCls: true,
                        icon: "/" + global.Context + "/static/js/ext/resources/images/default/grid/refresh.gif",
                        scope: this,
                        tooltip: 'Recarregar informações',
                        handler: function() {
                            this.getTopToolbar().getComponent(0).icon = "/" + global.Context + "/static/js/ext/resources/images/default/grid/loading.gif";
                            this.getTopToolbar().getComponent(0).render();
                            console.debug(this.getTopToolbar().getComponent(0).icon);
                            this.refresh();
                        }
                    },
                    "-"
                ];

                if(old) {
                    for(var o in old) {
                        if(!isNaN(o)) {
                            cf.tbar.push(old[o]);
                        }
                    }
                }

                toolkit.iget.Widget.superclass.constructor.call(this, cf);
            },

            refresh: function() {
                console.debug("Refresh do iGet não foi implementado");
            },

            onRender: function(container, position) {
                toolkit.iget.Widget.superclass.onRender.call(this, container, position);

                var panel = this;

                new toolkit.thread.Simple({
                    period: 60000,
                    handler: function() {
                        panel.refresh()
                    }
                }).start();

                this.refresh();
            }
        }
    );

    toolkit.iget.ContactSearch = Ext.extend(toolkit.iget.Widget,
        {
            SEARCH_TYPE: {
                SERVIDOR: 'Servidor',
                LOTACAO: 'Lotacao'
            },

            search: function(type) {
                var pk = 0;

                if(type == this.SEARCH_TYPE.SERVIDOR)
                    pk = this.getServidorForm().getForm().getValues()['servidor'];
                else if(type == this.SEARCH_TYPE.LOTACAO)
                    pk = this.getDepartamentoForm().getForm().getValues()['departamento'];


                this.getGridPanel().getStore().baseParams['pk'] = pk;
                this.getGridPanel().getStore().baseParams['type'] = type;
                this.getGridPanel().getStore().load({
                    params: {
                        start: 0
                    }
                });
            },

            getServidorForm: function() {
                if(!this.servidorForm) {
                    this.servidorForm = new Ext.form.FormPanel({
                        labelAlign: 'top',
                        defaults: {
                            width: '100%'
                        },
                        items: [
                            {
                                xtype: 'autocomplete',
                                name: 'servidor',
                                fieldLabel: 'Servidor',
                                store: new Ext.data.JsonStore({
                                    url: toolkit.util.Normalize.controller_action(
                                        'ContactSearch',
                                        'autocomplete'
                                    ),
                                    method: 'POST',
                                    root: 'result',
                                    totalPropertie: 'totalRows',
                                    baseParams: {model: 'Servidor'},
                                    fields: ['pk', 'description']
                                }),
                                displayField: 'description',
                                valueField: 'pk',
                                triggerAction: 'all'
                            }
                        ],
                        buttons: [
                            {
                                text: 'Buscar',
                                scope: this,
                                handler: function() {this.search(this.SEARCH_TYPE.SERVIDOR)}
                            }
                        ]
                    });
                }

                return this.servidorForm;
            },

            getDepartamentoForm: function() {
                if(!this.departamentoForm) {
                    this.departamentoForm = new Ext.form.FormPanel({
                        labelAlign: 'top',
                        defaults: {
                            width: '98%'
                        },
                        items: [
                            {
                                xtype: 'autocomplete',
                                name: 'departamento',
                                fieldLabel: 'Departamento',
                                store: new Ext.data.JsonStore({
                                    url: toolkit.util.Normalize.controller_action(
                                        'ContactSearch',
                                        'autocomplete'
                                    ),
                                    method: 'POST',
                                    root: 'result',
                                    totalPropertie: 'totalRows',
                                    baseParams: {model: 'Lotacao'},
                                    fields: ['pk', 'description']
                                }),
                                displayField: 'description',
                                valueField: 'pk',
                                triggerAction: 'all'
                            }
                        ],
                        buttons: [
                            {
                                text: 'Buscar',
                                scope: this,
                                handler: function() {this.search(this.SEARCH_TYPE.LOTACAO)}
                            }
                        ]
                    });
                }

                return this.departamentoForm;
            },

            getTabPanel: function() {
                if(!this.tabPanel) {
                    this.tabPanel = new Ext.TabPanel({
                        height: 125,
                        border: false,
                        activeTab: 0,
                        items: [
                            new Ext.Panel({
                                title: 'Servidor',
                                frame: true,
                                items: this.getServidorForm()
                            }),
                            new Ext.Panel({
                                title: 'Departamento',
                                frame: true,
                                items: this.getDepartamentoForm()
                            })
                        ]
                    });
                }

                return this.tabPanel;
            },

            formatNumber: function(value) {
                return '(' + value.substring(0, 2) + ') ' + value.substring(2, 6) + '-' + value.substring(6);
            },

            getGridPanel: function() {
                if(!this.gridPanel) {
                    var store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            'ContactSearch',
                            'search'
                        ),
                        method: 'POST',
                        fields: ['pk', 'contact', 'type', 'pessoa'],
                        totalProperty: 'totalRows',
                        root: 'result'
                    });

                    this.gridPanel = new Ext.grid.GridPanel({
                        store: store,
                        frame: true,
                        cm: new Ext.grid.ColumnModel([
                            {header: 'Pessoa', dataIndex: 'pessoa', width: 155},
                            {header: 'Numero', dataIndex: 'contact', renderer: this.formatNumber, width: 90}
                            // {header: 'Tipo', dataIndex: 'type'},
                        ]),
                        bbar: [
                            new Ext.PagingToolbar({
                                store: store,
                                displayInfo: true
                            })
                        ]
                    });
                }

                return this.gridPanel;
            },

            constructor: function() {
                var cf = {
                    title: 'Busca de contatos',
                    items: [
                        this.getTabPanel(),
                        this.getGridPanel()
                    ],
                    listeners: {
                        scope: this,
                        afterlayout: function(panel) {
                            var gp = this.getGridPanel();
                            var tb = this.getTabPanel();

                            gp.setHeight(panel.getBox().height - (tb.getBox().height + 30));
                        }
                    }
                };

                toolkit.iget.ContactSearch.superclass.constructor.call(this, cf);

                this.getTopToolbar().destroy();
            },

            refresh: function() {}
        }
    )

    toolkit.iget.ServerInformation = Ext.extend(toolkit.iget.Widget,
        {
            constructor: function() {
                var cf = {
                    title: "Informações do Servidor"
                };

                toolkit.iget.ServerInformation.superclass.constructor.call(this, cf);
            },

            refresh: function() {
                Ext.Ajax.request({
                    method: "POST",
                    url: toolkit.util.Normalize.controller_action(
                        "ServerInformation",
                        "refresh"
                    ),
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);

                        var tpl = new Ext.XTemplate(
                            "<ul class=\"information\">",
                                "<li><span>Nome :</span></li>",
                                "<li><span>{hostname}</span></li>",
                            "</ul>",
                            "<ul class=\"information\">",
                                "<li><span>IP :</span></li>",
                                "<li><span>{ip}</span></li>",
                            "</ul>",
                            "<ul class=\"information\">",
                                "<li><span>Mem. Física :</span></li>",
                                "<li><span>{mem_phy}</span></li>",
                            "</ul>",
                            "<ul class=\"information\">",
                                "<li><span>Mem. Livre :</span></li>",
                                "<li><span>{mem_unused}</span></li>",
                            "</ul>",
                            "<ul class=\"information\">",
                                "<li><span>Mem. Cache :</span></li>",
                                "<li><span>{mem_cache}</span></li>",
                            "</ul>",
                            "<hr/>",
                            "<span class=\"iget-titulo\">Trafego de Rede (KB/s)</span>",
                            "<div class=\"iget-graph\"></div>",
                            "<span class=\"iget-titulo\">Carga do Sistema</span>",
                            "<div class=\"iget-graph\"></div>",
                            "<span class=\"iget-titulo\">Uso do disco (%)</span>",
                            "<div class=\"iget-graph\"></div>"
                        );

                        tpl.overwrite(this.body, obj);
                        this.doLayout();
                    },
                    scope: this
                });

            }
        }
    );

    // _TODEL_ A funcionalidade "Atualização de telefones" foi implementada no novo Dashboard utilizando o código Restful existente do modelo Telefone.
    toolkit.iget.RamalUserInformation = Ext.extend(Ext.Window,
        {
            getFormPanel: function(type, record) {
                if(!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        border: false,
                        defaults: {
                            width: 240
                        },
                        autoShow: false,
                        items: [
                            {
                                xtype: 'fonefield',
                                fieldLabel: 'Número',
                                name: 'numero',
                                value: record ? record.get('numero') : ''
                            },
                            {
                                xtype: 'combo',
                                fieldLabel: 'Tipo',
                                store: [
                                    [1, 'RESIDENCIAL'],
                                    [2, 'COMERCIAL'],
                                    [3, 'CELULAR'],
                                    [4, 'FAX'],
                                    [5, 'INSTITUCIONAL'],
                                ],
                                hiddenName: 'tipo_telefone',
                                triggerAction: 'all',
                                value: record ? record.get('tipo_telefone') : ''
                            },
                            {
                                xtype: 'checkbox',
                                name: 'publico',
                                fieldLabel: 'Público',
                                checked: record ? record.get('publico') : false
                            }
                        ],
                        buttons: [
                            {
                                text: 'Salvar',
                                scope: this,
                                handler: function() {
                                    this.formPanel.getForm().submit({
                                        url: toolkit.util.Normalize.controller_action(
                                            'UserInformation',
                                            type == 0 ? 'add_fone' : 'edit_fone'
                                        ),
                                        params: record ? {pk: record.get('pk')} : undefined,
                                        success: this.commitSuccess,
                                        failure: this.commitFailure,
                                        scope: this
                                    });
                                }
                            },
                            {
                                text: 'Cancelar',
                                scope: this,
                                handler: this.destroyFormPanel
                            }
                        ],
                        type: type,
                        record: record
                    });
                }

                return this.formPanel;
            },

            commitSuccess: function(form, action) {
                this.getGridPanel().getStore().reload({});
                this.userInformation.refresh();
                this.destroyFormPanel();
            },

            commitFailure: function(form, action) {
                console.debug(action);
            },

            createFormPanel: function(type, record) {
                if(this.formPanel == undefined) {
                    this.insert(
                        0,
                        new Ext.Panel({
                            frame: true,
                            items: [
                                this.getFormPanel(type, record)
                            ]
                        })
                    );
                    this.doLayout();
                }
            },

            destroyFormPanel: function() {
                if(this.formPanel != undefined) {
                    this.remove(this.formPanel.ownerCt);
                    this.formPanel = undefined;
                }
            },

            deleteFone: function(record) {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        'UserInformation',
                        'delete_fone'
                    ),
                    params: {pk: record.get('pk')},
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);

                        if(obj.success) {
                            this.getGridPanel().getStore().reload({});
                            this.userInformation.refresh();
                        }
                        else
                            alert(obj.msg);
                    },
                    failure: function(request) {
                        alert('Erro aplicando as modificações, favor tentar novamente mais tarde.');
                    },
                    scope: this
                })
            },

            getGridPanel: function()  {
                if(!this.gridPanel) {
                    var store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            'UserInformation',
                            'myfones'
                        ),
                        root: 'root',
                        totalProperie: 'totalRows',
                        fields: ['pk', 'numero', 'tipo', 'tipo_telefone', 'publico']
                    });

                    this.gridPanel = new Ext.grid.GridPanel({
                        tbar: [
                            {
                                text: 'Novo',
                                scope: this,
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                handler: function() {
                                    this.destroyFormPanel();
                                    this.createFormPanel(0);
                                }
                            },
                            '-',
                            {
                                text: 'Editar',
                                scope: this,
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/document-open.png',
                                handler: function() {
                                    var rec = this.getGridPanel().getSelectionModel().getSelected();
                                    this.destroyFormPanel();
                                    this.createFormPanel(1, rec);
                                }
                            },
                            '-',
                            {
                                text: 'Remover',
                                scope: this,
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/delete.png',
                                handler: function() {
                                    var rec = this.getGridPanel().getSelectionModel().getSelected();
                                    this.deleteFone(rec);
                                }
                            },
                            '-'
                        ],
                        store: store,
                        border:false,
                        sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
                        cm: new Ext.grid.ColumnModel([
                            {header: 'Chave', dataIndex: 'pk'},
                            {header: 'Número', dataIndex: 'numero'},
                            {header: 'Tipo', dataIndex: 'tipo'},
                            {header: 'Publico', dataIndex: 'publico', renderer: function(value) { return (value ? 'SIM' : 'NÃO'); } }
                        ]),
                        height: 230,
                        bbar: [
                            new Ext.PagingToolbar({
                                store: store,
                                displayInfo: true
                            })
                        ]
                    });

                    store.load({});
                }

                return this.gridPanel;
            },

            constructor: function(userInformation) {
                var cf = {
                    title: 'Atualização de Telefones',
                    closable: true,
                    modal: true,
                    resizable: false,
                    userInformation: userInformation,
                    width: 390,
                    items: [
                        this.getGridPanel()
                    ]
                };

                toolkit.iget.RamalUserInformation.superclass.constructor.call(this, cf);
            }
        }
    )

    toolkit.iget.UserInformation = Ext.extend(toolkit.iget.Widget,
        {
            updateRamal: function() {
                new toolkit.iget.RamalUserInformation(this).show();
            },

            updateDoador: function(enable) {
                Ext.Ajax.request({
                    method: "POST",
                    url: toolkit.util.Normalize.controller_action(
                        "UserInformation",
                        "update_doador"
                    ),
                    params: {doador: enable},
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);

                        if(obj.success) {
                            this.refresh();
                            alert('Informações de doador atualizadas com sucesso.');
                        }
                        else alert('Não conseguir atualizar as informações de doador. Pessoa física não encontrada.');
                    },
                    failure: function() {
                        alert('Erro tentando atualizar informações de doador, por favor tente mais tarde.');
                    },
                    scope: this
                })
            },

            constructor: function(cfg) {
                cfg = cfg || {};

                Ext.apply(cfg, {
                    bodyStyle: {
                        border: 0,
                        padding: 10,
                    },
                });

                toolkit.iget.UserInformation.superclass.constructor.call(this, cfg);

                var tool = this.getTopToolbar();

                tool.add(
                    {
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/pda.png",
                        scope: this,
                        text: 'Telefone',
                        tooltip: 'Atualizar Telefone',
                        handler: this.updateRamal
                    },
                    '-',
                    {
                        iconCls: true,
                        icon: "/" + global.Context + "/static/images/emblem-favorite.png",
                        text: 'Doador',
                        tooltip: 'Sou doador de orgãos',
                        menu: [
                            {
                                text: 'Sim',
                                scope: this,
                                icon: "/" + global.Context + "/static/images/accept.png",
                                handler: function() { this.updateDoador(true) }
                            },
                            {
                                text: 'Não',
                                scope: this,
                                icon: "/" + global.Context + "/static/images/delete.png",
                                handler: function() { this.updateDoador(false) }
                            }
                        ]
                    },
                    '-'
                );
            },

            getTpl: function(data)
            {
                var tpl = new Ext.XTemplate(
                    '<table class="iget-user-information">',
                        '<tr>',
                            '<td><span>Foto :</span></td>',
                            '<td style="width:150px;"><div class="foto" style="background: url({foto}) no-repeat"></div></td>',
                        '</tr>',
                        '<tpl if="nome">',
                            '<tr>',
                                '<td><span>Nome :</span></td>',
                                '<td style="width:200px;"><span>{nome}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="username">',
                            '<tr>',
                                '<td><span>Usuário :</span></td>',
                                '<td style="width:200px;"><span>{username}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="matricula">',
                            '<tr>',
                                '<td><span>Matrícula :</span></td>',
                                '<td style="width:200px;"><span>{matricula}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="mail">',
                            '<tr>',
                                '<td><span>E-Mail :</span></td>',
                                '<td style="width:200px;"><span>{mail}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl for="ramais">',
                            '<tr>',
                                '<td><tpl if="xindex == 1"><span>Telefones :</span></tpl></td>',
                                '<td style="width:200px;"><span>{.}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl for="lotacao">',
                            '<tr>',
                                '<td><tpl if="xindex == 1"><span>Lotação :</span></tpl></td>',
                                '<td style="width:200px;"><span>{.}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl for="cargo">',
                            '<tr>',
                                '<td><tpl if="xindex == 1"><span>Cargo :</span></tpl></td>',
                                '<td style="width:200px;"><span>{.}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="funcao">',
                            '<tr>',
                                '<td><span>Função :</span></td>',
                                '<td style="width:200px;"><span>{funcao}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tr>',
                            '<td><span>Data base : (progressão e férias)</span></td>',
                            '<td style="width:200px;"><span>{dataReferenciaFerias}</span></td>',
                        '</tr>',
                        '<tpl if="natural">',
                            '<tr>',
                                '<td><span>Natural de :</span></td>',
                                '<td style="width:200px;"><span>{natural}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="ecivil">',
                            '<tr>',
                                '<td><span>Estado Civil :</span></td>',
                                '<td style="width:200px;"><span>{ecivil}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="tsangue">',
                            '<tr>',
                                '<td><span>Sangue :</span></td>',
                                '<td style="width:200px;"><span>{tsangue}</span></td>',
                            '</tr>',
                        '</tpl>',
                        '<tpl if="dorgao">',
                            '<tr>',
                                '<td><span>Doador :</span></td>',
                                '<td style="width:200px;"><span>{dorgao}</span></td>',
                            '</tr>',
                        '</tpl>',
                    '</table>'
                );

                return tpl;
            },

            renderInfo: function(data)
            {
                this.getTpl().overwrite(this.body, data);
                this.doLayout();
            },

            refresh: function() {
                if(localStorage && localStorage.getItem('user-info'))
                {
                    var data = JSON.parse(localStorage.getItem('user-info'));
                    this.renderInfo(data);
                    console.log('using cache');
                }
                else
                {
                    Ext.Ajax.request({
                        method: "POST",
                        url: toolkit.util.Normalize.controller_action(
                            "UserInformation",
                            "refresh"
                        ),
                        success: function(request) {
                            console.log('renew information');
                            var data = Ext.decode(request.responseText);
                            this.renderInfo(data);
                        },
                        scope: this
                    });
                }
            }
        }
    );

    toolkit.iget.UserActive = Ext.extend(toolkit.iget.Widget,
        {
            constructor: function() {
                var cf = {
                    title: "Usuário Ativos"
                };

                toolkit.iget.UserInformation.superclass.constructor.call(this, cf);
            },

            refresh: function() {
                Ext.Ajax.request({
                    method: "POST",
                    url: toolkit.util.Normalize.controller_action(
                        "UserActive",
                        "refresh"
                    ),
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);

                        var tpl = new Ext.XTemplate(
                            "<tpl for=\"info\">",
                                "<tpl if=\"this.igual(count, 0)\">",
                                    "<ul class=\"information\"><li><span>{title} :</span></li><li><span>Nenhum usuário</span></li></ul>",
                                "</tpl>",
                                "<tpl if=\"this.igual(count, 1)\">",
                                    "<ul class=\"information\"><li><span>{title} :</span></li><li><span>{count} usuário</span></li></ul>",
                                "</tpl>",
                                "<tpl if=\"count &gt; 1\">",
                                    "<ul class=\"information\"><li><span>{title} :</span></li><li><span>{count} usuários</span></li></ul>",
                                "</tpl>",
                            "</tpl>",
                            {
                                igual: function(x, y) {return x == y}
                            }
                        );

                        tpl.overwrite(this.body, obj);
                        this.doLayout();
                    },
                    scope: this
                });
            }
        }
    );

    toolkit.iget.Manager = Ext.extend(Ext.Panel,
        {
            addPanel: function(cls) {
                var flag = false;
                var item = "";

                for(var i in this._items) {
                    item = this._items[i];
                    if(item.name == cls) {
                        flag = true;
                        break;
                    }
                }

                if(!flag) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            cls,
                            "json"
                        ),
                        method: 'POST',
                        success: function(request) {
                            var object = Ext.decode(request.responseText);

                            this.add(object);
                            this.doLayout();
                            setTimeout(function() {object.doLayout();}, 50)

                            this._items.push({
                                name: cls,
                                object: object
                            });
                        },
                        scope: this
                    });

                }
                else {
                    alert("Este item já esta presente.")
                }
            },

            constructor: function() {
                var cf = {
                    tbar: [
                        {
                            text: "Adicionar",
                            menu: [
                                {
                                    text: "Informações do Usuário",
                                    scope: this,
                                    handler: function() {
                                        this.addPanel("UserInformation");
                                    }
                                },
                                {
                                    text: "Buscar contatos",
                                    scope: this,
                                    handler: function() {
                                        this.addPanel("ContactSearch");
                                    }
                                },
                                {
                                    text: "Usuários Ativos",
                                    scope: this,
                                    handler: function() {
                                        this.addPanel("UserActive");
                                    }
                                },
                                {
                                    text: "Informações do Servidor",
                                    scope: this,
                                    handler: function() {
                                        this.addPanel("ServerInformation");
                                    }
                                }
                            ]
                        }
                    ],
                    border: false,
                    layout: "accordion"
                };

                this._items = [];

                toolkit.iget.Manager.superclass.constructor.call(this, cf);

                this.addPanel("UserInformation");
                this.addPanel("ContactSearch");
            }
        }
    );

    toolkit.iget.ChangePasswordForm = Ext.extend(Ext.form.FormPanel, {

        constructor: function()
        {
            toolkit.iget.ChangePasswordForm.superclass.constructor.call(this, {
                height: 130,
                padding: 5,
                border: false,
                labelWidth: 125,
                labelAlign: 'right',
                items: this._getFields(),
                buttons: this._getButtons()
            });

        },

        _getUserData: function(callback)
        {
            Ext.Ajax.request({
                method: "POST",
                url: toolkit.util.Normalize.controller_action(
                    "UserInformation",
                    "refresh"
                ),
                success: function(request)
                {
                    var data = Ext.decode(request.responseText);
                    callback(data);
                }
            });
        },

        _getButtons: function()
        {
            return [
                {
                    text: 'Alterar',
                    scope: this,
                    handler: function()
                    {
                        var changePasswordForm = this.getForm(),
                            scope = this;

                        this._getUserData(function(data) {

                            changePasswordForm.setValues({username: data.username});

                            scope._submitForm({
                                form: changePasswordForm,
                                url: 'AuthBase/change_password',
                                success: function(form, action)
                                {
                                    r = action.result;

                                    if(r.success)
                                    {
                                        toolkit.util.messageDialog('Alerta', r.msg);
                                        scope.ownerCt.close();
                                    }
                                }
                            });
                        })

                    }
                }
            ];
        },

        _getFields: function()
        {
            return [
                {
                    xtype: 'hidden',
                    name: 'username',
                    width: 250
                },
                {
                    xtype: 'textfield',
                    fieldLabel: 'Senha atual',
                    name: 'current_password',
                    inputType: 'password',
                    width: 250
                },
                {
                    xtype: 'textfield',
                    fieldLabel: 'Nova senha',
                    name: 'new_password',
                    inputType: 'password',
                    width: 250
                },
                {
                    xtype: 'textfield',
                    fieldLabel: 'Confirmação de senha',
                    name: 'password_confirmation',
                    inputType: 'password',
                    width: 250
                }
            ];
        },

        _submitForm: function(params)
        {
            var overrides = params || {},
                defaults = {
                    waitMsg: 'Aguarde...',
                    form: null,
                    url: null,
                    success: null,
                    failure: null
                },
                config = Ext.apply(defaults, overrides);

            params.form.submit({
                scope: this,
                // clientValidation: true,
                url: toolkit.util.action(config.url),
                method: 'POST',
                success: function(form, action)
                {
                    if(config.success)
                        config.success(form, action);
                },
                failure: function(form, action)
                {
                    if(config.failure)
                        config.failure(form, action)
                    else
                    {
                        var msg = action.result.msg || 'Verifique o preenchimento do formulário.';
                        toolkit.util.errorDialog(msg, action.result.errors, params.form);
                    }
                },
                waitMsg: config.waitMsg
            });
        }
    });
}
