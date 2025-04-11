Ext._define('planning.hiring.agreement.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.agreement.Window',

    configOrderToolBar: ['add', 'edit', '-', 'ask', 'report', '-', 'export', '-', 'search', 'filter', '-', 'active'],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Status', dataIndex: 'icons', sortable: false, renderer: core.rendererIconGrid, menuDisabled: true, width: 90 },
                    { header: 'Número', dataIndex: 'numero', sortable: true, width: 80 },
                    { header: 'Fiscal', dataIndex: 'main_agreementsupervisors', sortable: true, width: 95 },
                    { header: 'Tipo de Contrato', dataIndex: 'tipo_contrato_display', sortable: true, width: 95 },
                    { header: 'Processo', dataIndex: 'numero_processo', sortable: true, width: 100 },
                    { header: 'Vencimento', dataIndex: 'data_vencimento_flag', sortable: true, width: 70 },
                    { header: 'Serviço', dataIndex: 'objeto_contrato', sortable: true, id: 'autoExpandColumn' },
                ]
            );

        return this._columnModel;
    },

    getReportAction: function () {
        if (!this._reportAction)
            this._reportAction = Ext._create('Ext.Button', {
                text: 'Relatórios',
                iconCls: 'icon-agree icon-agree-application-pdf',
                scope: this,
                menu: [
                    {
                        text: 'Extrato de Pagamentos',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportPaymentStatement').show();
                        }
                    },
                    {
                        text: 'Listagem de Pagamentos',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportPaymentRoll').show();
                        }
                    },
                    {
                        text: 'Saldo de Contrato',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportAgreeBalance').show();
                        }
                    },
                    {
                        text: 'Pagamento por Contrato/OB',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportBankPayment').show();
                        }
                    },
                    {
                        text: 'Fiscais por Contrato',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportAgreeManager').show();
                        }
                    },
                    {
                        text: 'Contratações',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportAgreements').show();
                        }
                    },
                    {
                        text: 'Levantamento de Saldo de Contratos',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportContractBalance').show();
                        }
                    },
                    {
                        text: 'Listagem de Fiscais do Contrato',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportAgreeSupervisor').show();
                        }
                    },
                    {
                        text: 'Contratos por mês de reajuste',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.agreement.ReportMonthReadjustment').show();
                        }
                    },
                ]
            });

        return this._reportAction;
    },

    getExportAction: function () {
        if (!this._exportAction) {
            this._exportAction = Ext._create('Ext.Button', {
                text: 'Exportar XLS',
                iconCls: 'icon-core icon-core-csv',
                scope: this,
                handler: function () {
                    Ext._create('planning.hiring.minutereport.ContratoExportXLS').show();
                }
            });
        }

        return this._exportAction;
    },

    getActiveAction: function () {
        if (!this._activeAction)
            this._activeAction = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Incluir Inativos',
                scope: this,
                handler: function (c, v) {
                    var store = this.getStore();
                    if (!v) {
                        this.disable();
                        store.removeAll();
                        this.setFilterProperty('status__in', [100, 1, 2, 3], 1000);
                        this.enable();
                    }
                    else {
                        this.disable();
                        store.removeAll();
                        this.setFilterProperty('status__in', [100, 1, 2, 3, 4, 5, 6], 1000);
                        this.enable();
                    }
                }
            });

        return this._activeAction;
    },

    getAskAction: function () {
        if (!this._askAction)
            this._askAction = Ext._create('Ext.Button', {
                text: 'Alterar Status',
                iconCls: 'icon-core icon-core-refresh',
                scope: this,
                menu: [
                    {
                        text: 'Reativar',
                        scope: this,
                        iconCls: 'icon-core icon-core-success',
                        handler: function () {
                            this.execAgreementAction(14);
                        }
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        iconCls: 'icon-core icon-core-delete',
                        handler: function () {
                            this.execAgreementAction(15);
                        }
                    },
                    {
                        text: 'Anular',
                        scope: this,
                        iconCls: 'icon-core icon-core-minus',
                        handler: function () {
                            this.execAgreementAction(16);
                        }
                    },
                    {
                        text: 'Rescindir',
                        scope: this,
                        iconCls: 'icon-core icon-core-error',
                        handler: function () {
                            this.execAgreementAction(9);
                        }
                    },
                    {
                        text: 'Finalizar',
                        iconCls: 'icon-core icon-core-run-ok',
                        scope: this,
                        handler: function () {
                            this.execAgreementAction(7)
                        },
                    },  

                ]
            });

        return this._askAction;
    },

    execAgreementAction: function (action) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            var title = 'Alterando status de contratos...';
            var msg = 'Informe uma observação para alterar o(s) contrato(s)?';
            var scope = this;
            var multiline = true;
            var fn_callback = function (btn, text) {
                if (btn == 'cancel') return;

                Ext.Ajax.request({
                    url: core.callAction('PHAAgreementAction', 'finalize_agreement_action'),
                    scope: this,
                    params: {
                        agreements: this.getSelectionModel().getSelections().map(
                            function (record) {
                                return record.get('pk')
                            }
                        ).join(),
                        observation: text ? text : '',
                        type: action // propriedade tipo da classe AcaoContrato
                    },
                    success: function (request) {
                        var rst = Ext.decode(request.responseText);

                        if (rst.success)
                            this.getStore().reload();
                        else
                            Ext.Msg.show({
                                title: 'Alterando contrato',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    }
                });
            };

            Ext.Msg.prompt(title, msg, fn_callback, scope, multiline);

        } else {
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um contrato para alterar status.'
            });
        }
    },

    

    toggleType: function(type) {
        if (this.filterType.indexOf(type) >= 0)
            this.filterType.remove(type);
        else
            this.filterType.push(type);

        // this.disable();
        // this.store.removeAll();
        this.setFilterProperty('tipo_contrato__in', this.filterType, 1001);
        // this.enable();
    },

    getAgreementFilter: function() {
        if(!this._agreementFilter)
            this._agreementFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Contrato',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(1);
                }
            });

        return this._agreementFilter;
    },

    getNEFilter: function(){
        if(!this._NEFilter)
            this._NEFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'NE',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(3);
                }
            });

        return this._NEFilter;
    },

    getRentFilter: function() {
        if(!this._rentFilter)
            this._rentFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Locação',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(4);
                }
            });

        return this._rentFilter;
    },

    getServicesFilter: function() {
        if(!this._servicesFilter)
            this._servicesFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Serviços Contínuos',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(5);
                }
            });
        return this._servicesFilter;
    },

    getSupplyFilter: function() {
        if(!this._supplyFilter)
            this._supplyFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Fornecimento',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(6);
                }
            });

        return this._supplyFilter;
    },

    getExonerationFilter: function() {
            if(!this._exonerationFilter)
            this._exonerationFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Dispensa',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(7);
                }
            });

        return this._exonerationFilter;
    },

    getLackOfNeedFilter: function() {
        if(!this._lackOfNeedFilter)
            this._lackOfNeedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Inexigência',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(8);
                }
            });

        return this._lackOfNeedFilter;
    },

    getNESupplyFilter: function() {
        if(!this._neSupplyFilter)
            this._neSupplyFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'NE Fornecimento',
                scope: this,
                hideOnClick: false,
                checked: (this.filterType.indexOf(1) >= 0) ? true : false,
                handler: function() {
                    this.toggleType(9);
                }
            });

        return this._neSupplyFilter;
    },

    getFilterAction: function() {
        if(!this._filterAction)
            this._filterAction = Ext._create('Ext.Button', {
                text: 'Filtro',
                iconCls: 'icon-patrimonio icon-pat-filter',
                menu: [
                        this.getAgreementFilter(),
                        this.getNEFilter(),
                        this.getRentFilter(),
                        this.getServicesFilter(),
                        this.getSupplyFilter(),
                        this.getExonerationFilter(),
                        this.getLackOfNeedFilter(),
                        this.getNESupplyFilter(),
                ]
            });

        return this._filterAction;
    },

    constructor: function (cfg) {
        cfg = (cfg ? cfg : {});

        if (cfg.filterType)
            this.filterType = cfg.filterType;
        else {
            this.filterType = [1, 3, 4, 5, 6, 7, 8, 9];
        }

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.agreement.Grid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.agreement.Restful',
    'planning.hiring.agreement.Grid'
);
