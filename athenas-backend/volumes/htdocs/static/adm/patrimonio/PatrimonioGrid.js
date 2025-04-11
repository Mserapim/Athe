/**
 *
 **/
Ext._define('adm.patrimonio.PatrimonioGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.PatrimonioRestfulWindow',

    configOrderToolBar: ['management', '-', 'reports', '-', 'search', '->', 'download'],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 105, menuDisabled: true, renderer: adm.daily.rendererIconGrid,
                    },
                    {
                        header: 'Plaqueta',
                        dataIndex: 'plaqueta_unicode',
                        width: 65,
                    },
                    {
                        header: 'Descrição',
                        dataIndex: 'descricao',
                        id: 'autoExpandColumn',
                        renderer: function(value) {
                            // Fix missing ellipsis
                            return Ext.util.Format.stripTags(value);
                        },
                    },
                    {
                        header: 'Especie',
                        dataIndex: 'especie_unicode',
                        width: 265,
                    },
                    {
                        header: 'Reavaliado',
                        dataIndex: 'total_reavaliacao',
                        width: 85, hidden: true, renderer: toolkit.util.formatCurrency,
                    },
                    {
                        header: 'Valor atual',
                        dataIndex: 'valor_atual',
                        width: 85, renderer: toolkit.util.formatCurrency,
                    },
                    {
                        header: 'Localização',
                        dataIndex: 'localizacao_unicode',
                        width: 265, hidden: true,
                    },
                ]
            );

        return this._columnModel;
    },

    showBaixado: function (enable, dispatch) {
        dispatch = core.nullValue(dispatch, true);

        if (enable) {
            this.removeFilterProperty('data_baixa__isnull', -1000);
        }
        else {
            this.setFilterProperty('data_baixa__isnull', false, -1000);
        }
    },

    toggleConservacao: function (tipo) {
        if (!this._filterConservacao)
            this._filterConservacao = [1, 2, 3, 4];

        if (this._filterConservacao.indexOf(tipo) >= 0)
            this._filterConservacao.remove(tipo);
        else
            this._filterConservacao.push(tipo);

        this.setFilterProperty('conservacao__in', this._filterConservacao, 1000);
    },

    filterSuspesao: function () {
        this._filterSuspenso = core.nullValue(this._filterSuspenso, 1);

        if (this._filterSuspenso == 1) {
            this.setFilterProperty('suspenso', true, 1011);
            this._filterSuspenso = 2;
        }
        else {
            this.removeFilterProperty('suspenso', 1011);
            this._filterSuspenso = 1;
        }
    },

    filterLocalizacao: function () {
        Ext._create('adm.patrimonio.localizacao.FilterWindow', {
            title: 'Selecionar Localização',
            modal: true,
            width: 450,
            callback: {
                scope: this,
                fn: function (tuple) {
                    if (tuple)
                        this.setFilterProperty('localizacao__in', tuple, 1001);
                    else
                        this.removeFilterProperty('localizacao__in', 1001);
                }
            }
        }).show();
    },

    filterResponsavel: function () {
        var wnd = Ext._create('Ext.Window', {
            title: 'Selecionar Responsável',
            width: 435,
            modal: true,
            resizable: false,
            border: false,
            buttons: [
                {
                    text: 'Limpar',
                    scope: this,
                    handler: function () {
                        this.removeFilterProperty('responsavel', 1002);
                        wnd.destroy();
                    }
                },
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function () {
                        var form = wnd.getComponent(0).getForm();

                        if (form.getValues().selecionado)
                            this.setFilterProperty('responsavel', form.getValues().selecionado, 1002);
                        else
                            this.removeFilterProperty('responsavel', 1002);

                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function () {
                        wnd.destroy();
                    }
                }
            ],
            items: Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Responsáveis",
                        allowBlank: true,
                        rest: "rh.employee.Restful",
                        name: "selecionado",
                        emptyText: 'Nome, matricula, cpf da pessoa física.'
                    },
                ]
            })
        }).show();
    },

    filterEspecie: function () {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.parametro.EspecieRestful',
            title: 'Selecione uma especie para filtrar',
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            callback: {
                scope: this,
                fn: function (instance) {
                    if (instance)
                        this.setFilterProperty("item_entrada__especie", instance.get('pk'), 1003);
                    else
                        this.removeFilterProperty('item_entrada__especie', 1003);
                }
            }
        }).show();
    },

    filterGrupoEspecie: function () {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.parametro.GrupoEspecieRestful',
            title: 'Selecione um grupo para filtrar',
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            callback: {
                scope: this,
                fn: function (instance) {
                    if (instance)
                        this.setFilterProperty("item_entrada__especie__grupo", instance.get('pk'), 1014);
                    else
                        this.removeFilterProperty('item_entrada__especie__grupo', 1014);
                }
            }
        }).show();
    },

    filterNotaEntrada: function () {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.entrada.Restful',
            title: 'Selecione um entrada para filtrar',
            region: 'center',
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            callback: {
                scope: this,
                fn: function (instance) {
                    if (instance)
                        this.setFilterProperty("item_entrada__nota", instance.get('pk'), 1004);
                    else
                        this.removeFilterProperty('item_entrada__nota', 1004);
                }
            }
        }).show();
    },

    filterNotaBaixa: function () {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.baixa.Restful',
            title: 'Selecione um baixa para filtrar',
            region: 'center',
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            callback: {
                scope: this,
                fn: function (instance) {
                    if (instance)
                        this.setFilterProperty("baixas__nota", instance.get('pk'), 1005);
                    else
                        this.removeFilterProperty('baixas__nota', 1005);
                }
            }
        }).show();
    },

    filterDataTombo: function () {
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
                            allowBlank: true
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'ate',
                            xtype: 'datefield',
                            allowBlank: true
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function () {
                        var form = wnd.getComponent(0).getForm();
                        var data = {
                            de: Ext.util.Format.date(form.findField('de').getValue(), 'Y-m-d'),
                            ate: Ext.util.Format.date(form.findField('ate').getValue(), 'Y-m-d')
                        };

                        if (data.de !== '')
                            this.setFilterProperty('data_tombo__gte', data.de, 1006, false);
                        else
                            this.removeFilterProperty('data_tombo__gte', 1006, false);

                        if (data.ate !== '')
                            this.setFilterProperty('data_tombo__lte', data.ate, 1007, false);
                        else
                            this.removeFilterProperty('data_tombo__lte', 1007, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function () { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterDataGarantia: function () {
        var wnd = Ext._create('Ext.Window', {
            title: 'Filtro por garantia',
            width: 250,
            modal: true,
            border: false,
            items: [
                Ext._create('Ext.form.FormPanel', {
                    border: false,
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'Prazo maior',
                            name: 'maior',
                            xtype: 'datefield',
                            allowBlank: true
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function () {
                        var form = wnd.getComponent(0).getForm();
                        var maior = Ext.util.Format.date(form.findField('maior').getValue(), 'Y-m-d');

                        if (maior)
                            this.setFilterProperty('prazo_garantia__gt', maior, 1008, true);
                        else
                            this.removeFilterProperty('prazo_garantia__gt', 1008, true);

                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function () { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterDataBaixa: function () {
        var wnd = Ext._create('Ext.Window', {
            title: 'Filtro por data de Baixa',
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
                            allowBlank: true
                        },
                        {
                            fieldLabel: 'Até',
                            name: 'ate',
                            xtype: 'datefield',
                            allowBlank: true
                        }
                    ]
                })
            ],
            buttons: [
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function () {
                        var form = wnd.getComponent(0).getForm();
                        var data = {
                            de: Ext.util.Format.date(form.findField('de').getValue(), 'Y-m-d'),
                            ate: Ext.util.Format.date(form.findField('ate').getValue(), 'Y-m-d')
                        };

                        if (data.de !== '')
                            this.setFilterProperty('data_baixa__gte', data.de, 1008, false);
                        else
                            this.removeFilterProperty('data_baixa__gte', 1008, false);

                        if (data.ate !== '')
                            this.setFilterProperty('data_baixa__lte', data.ate, 1009, false);
                        else
                            this.removeFilterProperty('data_baixa__lte', 1009, false);

                        this.getStore().load({});
                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    handler: function () { wnd.destroy(); }
                }
            ]
        }).show();
    },

    filterConta: function () {
        Ext._create('core.GridSelectWindow', {
            rest: 'adm.patrimonio.parametro.ContaRestful',
            title: 'Selecione um conta.',
            region: 'center',
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            callback: {
                scope: this,
                fn: function (instance) {
                    if (instance)
                        this.setFilterProperty("item_entrada__nota__conta", instance.get('pk'), 1010);
                    else
                        this.removeFilterProperty('item_entrada__nota__conta', 1010);
                }
            }
        }).show();
    },

    filterUtilizador: function () {
        var wnd = Ext._create('Ext.Window', {
            title: 'Selecionar Utilizador',
            width: 435,
            modal: true,
            resizable: false,
            border: false,
            buttons: [
                {
                    text: 'Limpar',
                    scope: this,
                    handler: function () {
                        this.removeFilterProperty('utilizado_por', 1011);
                        wnd.destroy();
                    }
                },
                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function () {
                        var form = wnd.getComponent(0).getForm();

                        if (form.getValues().selecionado)
                            this.setFilterProperty('utilizado_por', form.getValues().selecionado, 1011);
                        else
                            this.removeFilterProperty('utilizado_por', 1011);

                        wnd.destroy();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function () {
                        wnd.destroy();
                    }
                }
            ],
            items: Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Utilizador",
                        allowBlank: true,
                        rest: "rh.employee.Restful",
                        name: "selecionado",
                        emptyText: 'Nome, matricula, cpf da pessoa física.'
                    },
                ]
            })
        }).show();
    },

    filterPlaqueta: function () {
        var filter = this.getFilter();
        var plaqueta__iexact;

        var form = Ext._create('Ext.form.FormPanel', {
            frame: true,
            items: [
                {
                    xtype: 'textfield',
                    fieldLabel: 'Número',
                    name: 'iexact',
                    value: plaqueta__iexact
                },
            ]
        });

        var wnd = Ext._create('Ext.Window', {
            title: 'Filtro por plaqueta',
            modal: true,
            resizable: false,
            border: false,
            width: 300,
            items: [form],
            buttons: [
                {
                    text: 'Aplicar',
                    scope: this,
                    handler: function () {
                        var data = form.getForm().getValues();
                        this.removeFilterProperty('plaqueta__iexact', 1012, false);
                        this.removeFilterProperty('plaqueta__iexact', 1013, false);
                        if (data.iexact != '') {

                            this.setFilterProperty('plaqueta__iexact', data.iexact, 1012, false);
                        }
                        this.getStore().reload();
                        wnd.close();
                    }
                },
                {
                    text: 'Limpar',
                    scope: this,
                    handler: function () {
                        this.removeFilterProperty('plaqueta__iexact', 1012);
                        this.getStore().reload();
                        wnd.close();
                    }
                },
                {
                    text: 'Cancelar',
                    handler: function () {
                        wnd.close();
                    }
                }
            ]
        });

        wnd.show();
    },

    filterToggleInMovement: function (enable) {
        if (enable)
            this.setFilterProperty(
                'movement_items__movimento__status__in',
                [1, 2, 3, 4],
                1014
            );
        else
            this.removeFilterProperty(
                'movement_items__movimento__status__in',
                1014
            );
    },

    getFilterMenu: function () {
        return [
            {
                text: 'Por Plaqueta',
                scope: this,
                handler: this.filterPlaqueta
            },
            '-',
            {
                text: 'Por Data de Tombo',
                scope: this,
                handler: this.filterDataTombo
            },
            {
                text: 'Por Data de Baixa',
                scope: this,
                handler: this.filterDataBaixa
            },
            {
                text: 'Por Prazo de garantia',
                scope: this,
                handler: this.filterDataGarantia
            },
            '-',
            {
                text: 'Por Especie',
                scope: this,
                handler: this.filterEspecie
            },
            {
                text: 'Por Grupo Especie',
                scope: this,
                handler: this.filterGrupoEspecie
            },
            '-',
            {
                text: 'Por Nota de Entrada',
                scope: this,
                handler: this.filterNotaEntrada
            },
            {
                text: 'Por Nota de Baixa',
                scope: this,
                handler: this.filterNotaBaixa
            },
            {
                text: 'Por Conta Patrimonial',
                scope: this,
                handler: this.filterConta
            },
            '-',
            {
                text: 'Por Responsável',
                scope: this,
                handler: this.filterResponsavel
            },
            {
                text: 'Por Utilizador',
                scope: this,
                handler: this.filterUtilizador
            },
            {
                text: 'Por Localização',
                scope: this,
                handler: this.filterLocalizacao
            },
            '-',
            {
                text: 'Por Conservação',
                menu: [
                    {
                        text: 'Novo',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function () { this.toggleConservacao(1); }
                    },
                    {
                        text: 'Bom',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function () { this.toggleConservacao(2); }
                    },
                    {
                        text: 'Regular',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function () { this.toggleConservacao(3); }
                    },
                    {
                        text: 'Inservivel',
                        checked: true,
                        scope: this,
                        hideOnClick: false,
                        handler: function () { this.toggleConservacao(4); }
                    }
                ]
            },
            '-',
            {
                text: 'Mostra itens baixados',
                checked: false,
                hideOnClick: false,
                listeners: {
                    scope: this,
                    checkchange: function (menu, checked) {
                        this.showBaixado(checked);
                    }
                }
            },
            {
                text: 'Somente itens suspensos',
                checked: false,
                hideOnClick: false,
                scope: this,
                handler: this.filterSuspesao
            },
            '-',
            {
                text: 'Somente sem localização',
                checked: false,
                hideOnClick: false,
                scope: this,
                listeners: {
                    scope: this,
                    checkchange: function (menu, checked) {
                        this.filterWithoutLocation(checked);
                    }
                }
            },
            {
                text: 'Somente em movimentação',
                checked: false,
                hideOnClick: false,
                scope: this,
                listeners: {
                    scope: this,
                    checkchange: function (menu, checked) {
                        this.filterToggleInMovement(checked);
                    }
                }
            },
            {
                text: 'Somente sem responsável',
                checked: false,
                hideOnClick: false,
                scope: this,
                listeners: {
                    scope: this,
                    checkchange: function (menu, checked) {
                        this.filterWithoutOwner(checked);
                    }
                }
            },
            '-',
            {
                xtype: 'menuitem',
                text: 'Desfazer Todos os Filtros',
                scope: this,
                hideOnClick: false,
                handler: function () {
                    defaultFilter = [
                        { property: "conservacao__in", value: [1, 2, 3, 4], stage: 1000 },
                        { property: "data_baixa__isnull", value: false, stage: -1000 }
                    ];
                    this.setFilter(defaultFilter, true);
                }
            }
        ];
    },

    filterWithoutLocation: function (enable) {
        if (enable)
            this.setFilterProperty('localizacao__isnull', true, 1014);
        else
            this.removeFilterProperty('localizacao__isnull', 1014);
    },

    filterWithoutOwner: function (enable) {
        if (enable)
            this.setFilterProperty('responsavel__isnull', true, 1015);
        else
            this.removeFilterProperty('responsavel__isnull', 1015);
    },

    cleanFilter: function () {
        try {
            this.setFilterProperty('conservacao__in', [1, 2, 3, 4], 1000, false);
            this.setFilterProperty('data_baixa__isnull', false, -1000, true);
        }
        catch (e) { /* não faz nada */ }
    },

    openEntradaManage: function () {
        Ext._create('adm.patrimonio.entrada.Manage', {
            modal: true,
            draggable: false
        }).show();
    },

    openBaixaManage: function () {
        Ext._create('adm.patrimonio.baixa.Manage', {
            modal: true,
            draggable: false
        }).show();
    },

    openMovimentoManage: function () {
        Ext._create('adm.patrimonio.movimento.WindowManage', {
            modal: true,
            draggable: false
        }).show();
    },

    getManagementAction: function (cfg) {
        if (!this._managementAction)
            this._managementAction = Ext._create('Ext.Button', {
                text: 'Gerenciamento',
                menu: [
                    {
                        text: 'Entrada de Itens',
                        iconCls: 'icon-patrimonio icon-pat-entrada',
                        scope: this,
                        handler: this.openEntradaManage
                    },
                    {
                        text: 'Movimentação de Itens',
                        iconCls: 'icon-patrimonio icon-pat-em-movimento',
                        scope: this,
                        handler: this.openMovimentoManage
                    },
                    {
                        text: 'Baixa de Itens',
                        iconCls: 'icon-patrimonio icon-pat-nota-baixa',
                        scope: this,
                        handler: this.openBaixaManage
                    },
                    '-',
                    {
                        text: 'Alterar estado de conservação de bens',
                        scope: this,
                        handler: this.changeConservation
                    }
                ]
            });

        return this._managementAction;
    },

    changeConservation: function () {
        var selection = this.getSelectionModel().getSelections();

        if (selection.length > 0)
            Ext._create('adm.patrimonio.ChangeConservationWindow', {
                success: {
                    fn: function () {
                        this.getStore().reload();
                    },
                    scope: this
                },
                pkset: selection.map(function (data) { return data.get('pk'); })
            }).show();
        else
            Ext.Msg.show({
                title: 'Alterando estado de consevação',
                msg: 'Primeiro selecione os itens que deseja alterar o estado de conservação.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    getActiveAssetsMenuHandler: function(department) {
        return {
            text: 'de Bens Ativos',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.ActiveAssetsWindow', {
                    _report: '/to/mpe/adm/patrimonio/Contabil_de_Bens_Ativo',
                    _reportName: ' de Bens Ativos',
                    fields: { department: department, reportTypeValue: 0 }
                }).show();
            }
        };
    },

    getNetActiveAssetsMenuHandler: function(department)  {
        return {
            text: 'de Bens Ativos Liquido',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.ActiveAssetsWindow', {
                    _report: '/to/mpe/adm/patrimonio/Contabil_de_Bens_Ativo_Liquido',
                    _reportName: ' de Bens Ativos Liquido',
                    fields: { department: department }
                }).show();
            }
        };
    },

    getAcquiredAssetsMenuHandler: function(department) {
        return {
            text: 'de Bens Adquiridos',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.AcquiredAssetsWindow', {
                    _report: '/to/mpe/adm/patrimonio/Contabil_de_Bens_Adquirido',
                    _reportName: ' de Bens Adquiridos',
                    fields: { department: department, acquisition: true }
                }).show();
            }
        };
    },

    getRetirementAssetsMenuHandler: function(department) {
        return {
            text: 'de Bens Baixados',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.AcquiredAssetsWindow', {
                    _report: '/to/mpe/adm/patrimonio/Contabil_de_Bens_Baixado',
                    _reportName: ' de Bens Baixados',
                    fields: { department: department }
                }).show();
            }
        };
    },

    getRetirementAssetsLiquidMenuHandler: function(department) {
        return {
            text: 'de Bens Baixados - Liquídos',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.AcquiredAssetsWindow', {
                    _report: '/to/mpe/adm/patrimonio/Contabil_de_Bens_Baixado_Liquido',
                    _reportName: ' de Bens Baixados - Liquídos',
                    fields: { department: department }
                }).show();
            }
        };
    },

    getDepreciatedAssetsMenuHandler: function(department) {
        return {
            text: 'de Bens Depreciados',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.DepreciatedAssetsWindow', {
                    fields: { department: department, depreciated: 1, reportTypeExtended: true }
                }).show();
            }
        };
    },

    getReavaliatedAssetsMenuHandler: function(department) {
        return {
            text: 'de Bens Reavaliados',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.DepreciatedAssetsWindow', {
                    _reportName: ' de Bens Depreciados (Reavaliados)',
                    fields: { department: department, depreciated: 2, reportTypeExtended: true }
                }).show();
            }
        };
    },

    getAssetsWithLocationMenuHandler: function() {
        return {
            text: 'de Bens Ativos (Localização)',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.ActiveAssetsByLocationWindow', {
                    _report: '/to/mpe/adm/patrimonio/Analitico_de_Bens_Ativo_por_Localizacao',
                    _reportName: 'Bens Ativos Por Localizacao',
                    fields: { group: true, specie: true, location: true }
                }).show();
            }
        };
    },

    getAssetsWithoutLocationMenuHandler: function() {
        return {
            text: 'de Bens Ativos (sem Localização)',
            scope: this,
            handler: function () {
                Ext._create('adm.patrimonio.reports.ActiveAssetsByLocationWindow', {
                    _report: '/to/mpe/adm/patrimonio/Analitico_de_Bens_Ativo_sem_Localizacao',
                    _reportName: 'Bens Ativos Sem Localizacao',
                    fields: {}
                }).show();
            }
        };
    },

    getReportsAction: function (cfg) {
        if (!this._reportsAction)
            this._reportsAction = Ext._create('Ext.Button', {
                text: 'Relatórios',
                iconCls: 'icon-core icon-core-reports',
                menu: [
                    {
                        text: 'Contabil',
                        menu: [
                            this.getActiveAssetsMenuHandler(0),
                            this.getNetActiveAssetsMenuHandler(0),
                            this.getAcquiredAssetsMenuHandler(0),
                            this.getRetirementAssetsMenuHandler(0),
                            this.getRetirementAssetsLiquidMenuHandler(0),
                            this.getDepreciatedAssetsMenuHandler(0),
                            this.getReavaliatedAssetsMenuHandler(0)
                        ]
                    },
                    {
                        text: 'Patrimonial',
                        menu: [
                            this.getActiveAssetsMenuHandler(1),
                            this.getNetActiveAssetsMenuHandler(1),
                            this.getAcquiredAssetsMenuHandler(1),
                            this.getRetirementAssetsMenuHandler(1),
                            this.getRetirementAssetsLiquidMenuHandler(1),
                            this.getDepreciatedAssetsMenuHandler(1),
                            this.getAssetsWithLocationMenuHandler(),
                            this.getAssetsWithoutLocationMenuHandler()
                        ]
                    }
                ]
            });

        return this._reportsAction;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            viewConfig: {
                scope: this,
                getRowClass: function (record) {
                    css = [];

                    if (record.get('data_baixa') !== null)
                        css.push('x-grid3-red');

                    if (record.get('read_only'))
                        css.push('x-grid3-read-only');

                    return css.join(' ');
                }
            }
        });

        cfg.columnAction = false;
        cfg.gridAutoLoad = false;

        adm.patrimonio.PatrimonioGrid.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            render: function () {
                this.cleanFilter();
            }
        });
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.PatrimonioRestful',
    'adm.patrimonio.PatrimonioGrid'
);
