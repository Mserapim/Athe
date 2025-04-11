/**
 *
 **/
Ext._define('adm.patrimonio.entrada.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.entrada.Window',

    singleton: {
        types: [],

        register: function(name, label, iconCls, Class) {
            adm.patrimonio.entrada.Grid.types.push({
                name: name,
                label: label,
                iconCls: iconCls,
                Class: Class
            });
        },

        getClassByName: function(name) {
            var Class = false;

            adm.patrimonio.entrada.Grid.types.forEach(
                function(item) {
                    if(item.name == name) {
                        Class = item.Class;
                        return false;
                    }
                }
            );

            return Class;
        },

        getNewMenu: function(scope) {
            if(adm.patrimonio.entrada.Grid.types.length > 0) {
                return adm.patrimonio.entrada.Grid.types.map(
                    function(item) {
                        return {
                            text: item.label,
                            scope: scope,
                            iconCls: item.iconCls,
                            handler: function() {
                                this.createItem(item.Class);
                            }
                        };
                    }
                );
            }
            else
                return [
                    {
                        text: 'Nenhum tipo foi especificado',
                        enable: false
                    }
                ];
        }
    },

    filterConta: function() {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.parametro.ContaRestful',
            region: 'center',
            width: 650,
            callback: {
                scope: this,
                fn: function(instance) {
                    if(instance)
                        this.setFilterProperty("conta", instance.get('pk'), 1000);
                    else
                        this.removeFilterProperty('conta', 1000);
                }
            }
        }).show();
    },

    filterFornecedor: function() {
        var wnd = Ext._create('Ext.Window', {
            title: 'Selecionar Fornecedor',
            modal: true,
            resizable: false,
            width: 450,
            border: false,
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();

                        if(form.getValues().selecionado)
                            this.setFilterProperty('fornecedor', form.getValues().selecionado, 1001);
                        else
                            this.removeFilterProperty('fornecedor', 1001);

                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        wnd.destroy();
                    }
                }
            ],
            items: Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Fornecedor",
                        allowBlank: true,
                        rest: "rh.person.Restful",
                        name: "selecionado",
                        emptyText: 'Fornecedor'
                    }
                ]
            })
        }).show();
    },

    filterDataCompra: function() {
        var filter = this.getFilter();
        var data_de, data_ate;

        Ext.each(filter, function(c) {
            if(c.property == 'data_compra__gte')
                data_de = c.value;
            else if(c.property == 'data_compra__lte')
                data_ate = c.value;
        });

        var wnd = Ext._create('Ext.Window', {
            title: 'Filtro por data de Compra',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'De',
                            name: 'de',
                            xtype: 'datefield',
                            allowBlank: true,
                            value: data_de
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'ate',
                            xtype: 'datefield',
                            allowBlank: true,
                            value: data_ate
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var data = {
                            de: Ext.util.Format.date(form.findField('de').getValue(), 'Y-m-d'),
                            ate: Ext.util.Format.date(form.findField('ate').getValue(), 'Y-m-d')
                        };

                        if(data.de != '')
                            this.setFilterProperty('data_compra__gte', data.de, 1002, false);
                        else
                            this.removeFilterProperty('data_compra__gte', 1002, false);

                        if(data.ate != '')
                            this.setFilterProperty('data_compra__lte', data.ate, 1003, false);
                        else
                            this.removeFilterProperty('data_compra__lte', 1003, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function() { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterDataTombo: function() {
        var filter = this.getFilter();
        var data_de, data_ate;

        Ext.each(filter, function(c) {
            if(c.property == 'tombado__gte')
                data_de = c.value;
            else if(c.property == 'tombado__lte')
                data_ate = c.value;
        });

        var wnd = Ext._create('Ext.Window', {
            title: 'Filtro por data de Tombo',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'De',
                            name: 'de',
                            xtype: 'datefield',
                            allowBlank: true,
                            value: data_de
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'ate',
                            xtype: 'datefield',
                            allowBlank: true,
                            value: data_ate
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var data = {
                            de: Ext.util.Format.date(form.findField('de').getValue(), 'Y-m-d'),
                            ate: Ext.util.Format.date(form.findField('ate').getValue(), 'Y-m-d')
                        };

                        if(data.de != '')
                            this.setFilterProperty('tombado__gte', data.de, 1010, false);
                        else
                            this.removeFilterProperty('tombado__gte', 1010, false);

                        if(data.ate != '')
                            this.setFilterProperty('tombado__lte', data.ate, 1011, false);
                        else
                            this.removeFilterProperty('tombado__lte', 1011, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function() { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterDataNota: function() {
        var filter = this.getFilter();
        var data_de, data_ate;

        Ext.each(filter, function(c) {
            if(c.property == 'data_nota__gte')
                data_de = c.value;
            else if(c.property == 'data_nota__lte')
                data_ate = c.value;
        });

        var wnd = Ext._create('Ext.Window', {
            title: 'Filtro por data da Nota',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'De',
                            name: 'de',
                            xtype: 'datefield',
                            allowBlank: true,
                            value: data_de
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'ate',
                            xtype: 'datefield',
                            allowBlank: true,
                            value: data_ate
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var form = wnd.getComponent(0).getForm();
                        var data = {
                            de: Ext.util.Format.date(form.findField('de').getValue(), 'Y-m-d'),
                            ate: Ext.util.Format.date(form.findField('ate').getValue(), 'Y-m-d')
                        };

                        if(data.de != '')
                            this.setFilterProperty('data_nota__gte', data.de, 1002, false);
                        else
                            this.removeFilterProperty('data_nota__gte', 1002, false);

                        if(data.ate != '')
                            this.setFilterProperty('data_nota__lte', data.ate, 1003, false);
                        else
                            this.removeFilterProperty('data_nota__lte', 1003, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function() { wnd.destroy(); }
                }
            ]
        }).show();
    },

    getFilterMenu: function() {
        return [
            {
                text: 'Por Conta',
                scope: this,
                handler: this.filterConta
            },
            {
                text: 'Periodo de Tombo',
                scope: this,
                handler: this.filterDataTombo
            },
            {
                text: 'Periodo de Compra',
                scope: this,
                handler: this.filterDataCompra
            },
            {
                text: 'Periodo da Nota Fiscal',
                scope: this,
                handler: this.filterDataNota
            },
            {
                text: 'Fornecedor',
                scope: this,
                handler: this.filterFornecedor
            },
            '-',
            {
                text: 'Somente suspensos',
                checked: false,
                hideOnClick: false,
                scope: this,
                handler: this.filterSuspesao
            }
        ];
    },

    filterSuspesao: function() {
        this._filterSuspenso = core.nullValue(this._filterSuspenso, 1);

        if(this._filterSuspenso == 1) {
            this.setFilterProperty('suspensoes__ativo', true, 1004);
            this._filterSuspenso = 2;
        }
        else {
            this.removeFilterProperty('suspensoes__ativo', 1004);
            this._filterSuspenso = 1;
        }
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 70,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {
                        header: 'Controle',
                        dataIndex: 'formated_number',
                        width: 75
                    },
                    {header: 'Fornecedor', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {
                        header: 'Execução',
                        dataIndex: 'execucao_orcamentaria',
                        width: 75,
                        renderer: function(value) {
                            return value == 1 ? 'DEO' : 'IEO';
                        }
                    },
                    {header: 'Conta', dataIndex: 'conta_unicode', width: 160},
                    {header: 'Processo', dataIndex: 'processo', width: 95},
                    {
                        header: 'Data Compra',
                        dataIndex: 'data_compra',
                        width: 95,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y')
                    },
                    {
                        header: 'Data Cadastro',
                        dataIndex: 'data_compra',
                        width: 95,
                        hidden: true,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y')
                    },
                    {header: 'Empenho', dataIndex: 'empenho_unicode', width: 95}
                ]
            );

        return this._columnModel;
    },

    createItem: function(classDef) {
        var values = {};
        var ClassBase;

        if(classDef.type) {
            ClassBase = adm.patrimonio.entrada.Grid.getClassByName(classDef.type);
            values = classDef;
        }
        else {
            ClassBase = classDef;
        }

        Ext._create(
            ClassBase,
            {
                action: 'create',
                params: this.getParams(),
                values: {},
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }
        ).show();
    },

    updateItem: function(record) {
        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            var Class = adm.patrimonio.entrada.Grid.getClassByName(selected.get('type'));
            Ext._create(Class, {
                action: 'update',
                oId: selected.get('pk'),
                values: 'remote',
                params: this.getParams(),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });
    },

    changeState: function(state) {
        var selection = this.getSelectionModel().getSelections();
        var cfg = false;
        var rest;

        if(selection.length == 1) {
            var Klass = eval(
                adm.patrimonio.entrada.Grid.getClassByName(selection[0].get('type'))
            );

            rest = Ext._create(Klass.prototype.rest);

            cfg = {
                params: {
                    state: state
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            };

            rest.update(
                selection[0].get('pk'),
                cfg,
                {
                    el: this.getEl(),
                    message: 'Atualizando o estado da nota de entrada.'
                }
            );
        }
        else if(selection.length > 1) {
            cfg = {
                params: {
                    state: state,
                    filter: Ext.encode([
                        {
                            property: 'pk__in',
                            value: selection.map(
                                function(s) { return s.get('pk'); }
                            )
                        }
                    ])
                },
                externalCallback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            };

            rest.update(
                false,
                cfg,
                {
                    el: this.getEl(),
                    message: 'Atualizando o estado da nota de entrada.'
                }
            );
        }
        else {
            Ext.Msg.show({
                title: 'Nota de Entrada',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione os itens que deseja mudar o estado.'
            });
        }
    },

    getToolbar: function(cfg) {
        var novoComponent;

        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.entrada.Grid.superclass.getToolbar.call(this, cfg);

            this._toolbar.findBy(
                function(item) {
                    if(item.text == 'Novo')
                        novoComponent = item;
                }
            );

            this._toolbar.remove(novoComponent);
            this._toolbar.insert(0, {
                text: 'Nova Entrada',
                iconCls: 'icon-core icon-core-add',
                menu: adm.patrimonio.entrada.Grid.getNewMenu(this)
            });

            this._toolbar.insert(
                3,
                {
                    text: 'Status',
                    iconCls: 'icon-patrimonio icon-pat-nota',
                    menu: [
                        {
                            text: 'Nota Aberta',
                            iconCls: 'icon-patrimonio icon-pat-nota-aberta',
                            scope: this,
                            handler: function() { this.changeState(1); }
                        },
                        {
                            text: 'Nota Finalizada',
                            iconCls: 'icon-patrimonio icon-pat-nota-finalizada',
                            scope: this,
                            handler: function() { this.changeState(2); }
                        },
                        {
                            text: 'Nota Cancelada',
                            iconCls: 'icon-patrimonio icon-pat-nota-cancelada',
                            scope: this,
                            handler: function() { this.changeState(3); }
                        }
                    ]
                }
            );

            this._toolbar.insert(
                3, '-'
            );
        }

        return this._toolbar;
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.entrada.Restful',
    'adm.patrimonio.entrada.Grid'
);
