Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerGrid', {
    extend: 'planning.hiring.minutesolicitation.MinuteSolicitationGrid',

    rest: 'planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerRestful',

    configOrderToolBar: ['addsolicitation', 'remove', '-', 'generateOrder', 'situation', 'generateAgreement', 'rebalancing', '-', 'report', '-', 'search', 'filter', '->', 'download'],

    getColumnModel: function () {
        if (!this._columnModel) 
        {
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Ata', dataIndex: 'minute_unicode', width: 90 },
                    { header: 'Número do Processo', dataIndex: 'minute_process_number_display', width: 200 },
                    { header: 'Número do Pedido', dataIndex: 'number', width: 120 },
                    { header: 'Situação', dataIndex: 'situation_display', width: 120 },
                    { header: 'Fiscal', dataIndex: 'main_supervisors_display', width: 120, id: 'autoExpandColumn' },
                    { header: 'Edoc', dataIndex: 'edoc_display', hidden: true },
                    { header: 'Descricao', dataIndex: 'unicode', hidden: true },
                    { header: 'Justificativa', dataIndex: 'justification', width: 90, hidden: true },
                ]
            );
        }
        return this._columnModel;
    },

    getRebalancingAction: function() {
        if (!this._rebalancing) {
            this._rebalancing = Ext._create('Ext.Button', {
                text: 'Reequilibrar',
                iconCls: 'icon-agree icon-agree-ne-reinforcement',
                scope: this,
                handler: function () {
                    var selected = this.getSelectionModel().getSelected();

                    if(selected) {
                        let rebalancingWindow = Ext._create(
                            'planning.hiring.minutesolicitationmanager.MinuteSolicitationRebalancingWindow',
                            {
                                title: 'Itens da Ata',
                                params: {
                                    minute: selected.data.minute,
                                    solicitation: selected.data.pk
                                }
                            }
                        );

                        rebalancingWindow.show();
                    }
                    else {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Primeiro selecione um pedido.'
                        });
                    }
                }
            });
        }

        return this._rebalancing;
    },

    generateEdoc: function(id) {
        var rest = Ext._create('planning.hiring.minutesolicitationrequisition.MinuteSolicitationRequisitionRestful');
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Gerando Edoc...' });

        mask.show();
        rest.rendererEdoc(
            id,
            {
                scope: this,
                fn: function(message) {
                    var _window = Ext._create(
                        'planning.hiring.minutesolicitationmanager.EdocTextWindow'
                    );

                    // Refactoring
                    _window.insertText(message);

                    _window.oId = id;

                    _window.show();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Gerando Edoc',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    mask.hide();
                }
            },
            {
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getGenerateOrderAction: function () {
        if (!this._generateOrder)  {
            this._generateOrder = Ext._create('Ext.Button', {
                text: 'Gerar Pedido',
                iconCls: 'icon-agree icon-agree-appointment-new',
                scope: this,
                handler: function () {
                    var selected = this.getSelectionModel().getSelected();

                    if(selected) {
                        this.generateEdoc(selected.id);
                    }
                    else {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Primeiro selecione um pedido.'
                        });
                    }
                }
            });
        }
        return this._generateOrder;
    },

    getGenerateAgreementAction: function () {
        if (!this._generateAgreementAction)  {
            this._generateAgreementAction = Ext._create('Ext.Button', {
                text: 'Contratar',
                iconCls: 'icon-core icon-core-document-arrow',
                scope: this,
                handler: function () {
                    var selection = this.getSelectionModel().getSelections();
                    var solicitations = selection.map(
                        function(item) { return item.get('pk') }
                    );

                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('PHMMinuteSolicitationAction', 'verify_generate_agreement'),
                        params: {
                            solicitation: solicitations
                        },

                        success: function (request) {
                            var obj = Ext.decode(request.responseText);
                            if (obj.before_generate_agreement){
                                Ext.Msg.show({
                                    title: 'Alerta de geração de contrato',
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.YESNO,
                                    msg: obj.message,
                                    fn: function (bnt) {
                                        if (bnt == 'yes'){
                                            Ext._create('planning.hiring.minutesolicitationmanager.MinuteSolicitationAgreementParameterWindow', {
                                                solicitations: solicitations,
                                                grid: this
                                            }).show();
                                        }
                                    }
                                });
                            }else{
                                Ext._create('planning.hiring.minutesolicitationmanager.MinuteSolicitationAgreementParameterWindow', {
                                    solicitations: solicitations,
                                    grid: this
                                }).show();
                            }
                        }
                    })
                }
            });
        }
        return this._generateAgreementAction;
    },

    getAddsolicitationAction: function () {
        if (!this._addSolicitationAction) {
            this._addSolicitationAction = Ext._create('Ext.Button', {
                text: 'Novo Pedido',
                iconCls: 'icon-agree icon-agree-add',
                scope: this,
                handler: function () {
                    Ext._create('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerWindow', {
                        action: 'create'
                        }).show();
                    }
            });
        }

        return this._addSolicitationAction;
    },

    execMinuteSolicitationAction: function (num) {
        var selected = this.getSelectionModel().getSelected();
        if (selected)
            Ext.Ajax.request({
                scope: this,
                url: toolkit.util.Normalize.controller_action(
                    'PHMMinuteSolicitationAction',
                    'minute_within_validity'
                ),
                params: {
                    action: num,
                    solicitation: selected.get('pk'),
                },
                success: function (response) {
                    var obj = Ext.decode(response.responseText);
                    if (obj.success) {
                        var wnd = Ext._create('planning.hiring.minutesolicitationaction.MinuteSolicitationActionWindow', {
                            params: {
                                action: num,
                                solicitation: selected.get('pk'),
                                user: 845
                            },
                            callback: {
                                success: {
                                    scope: this,
                                    fn: function (args) {
                                        this.getStore().reload();
                                    }
                                }
                            },
                            action: 'create',
                        });

                        if (obj.display_info)
                            Ext.Msg.show({
                                title: 'Ata vencida',
                                icon: Ext.Msg.QUESTION,
                                buttons: Ext.Msg.YESNO,
                                msg: obj.message,
                                fn: function (bnt) {
                                    if (bnt == 'no') return;
                                    wnd.show();
                                }
                            });
                        else
                            wnd.show();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Erro na geração do EDOC.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                },
                failure: function (response) {
                    Ext.Msg.show({
                        title: 'Não foi possível preencher o conteúdo do EDOC.',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
                }

            });
        else
            Ext.Msg.show({
                title: '',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um pedido para executar a ação.'
            });

    },

    getSituationAction: function () {
        if (!this._situationAction)
            this._situationAction = Ext._create('Ext.Button', {
                text: 'Situação',
                iconCls: 'icon-agree icon-agree-view-calendar',
                scope: this,
                menu: [
                    {
                        text: 'Aprovar',
                        scope: this,
                        group: 'solicitacao',
                        iconCls: 'icon-agree icon-agree-appointment-new',
                        handler: function () {
                            this.execMinuteSolicitationAction(3);
                        }
                    },
                    {
                        text: 'Recusar',
                        scope: this,
                        group: 'solicitacao',
                        iconCls: 'icon-agree icon-agree-emblem-important',
                        handler: function () {
                            this.execMinuteSolicitationAction(4);
                        }
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        group: 'solicitacao',
                        iconCls: 'icon-agree icon-agree-delete',
                        handler: function () {
                            this.execMinuteSolicitationAction(5);
                        }
                    },
                ]
            });

        return this._situationAction;
    },

    getReportAction: function () {
        if (!this._reportAction)
            this._reportAction = Ext._create('Ext.Button', {
                text: 'Relatórios',
                iconCls: 'icon-agree icon-agree-application-pdf',
                scope: this,
                menu: [
                    {
                        text: 'Listagem de Pedidos',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.minutereport.SolicitationListReport').show();
                        }
                    },
                    {
                        text: 'Listagem de Pedidos por Ata',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.minutereport.SolicitationListByMinuteReport').show();
                        }
                    },
                ]
            });

        return this._reportAction;
    },

    toggleStatus: function (status) {
        if (this.filterStatus.indexOf(status) >= 0)
            this.filterStatus.remove(status);
        else
            this.filterStatus.push(status);

        this.setFilterProperty('situation__in', this.filterStatus, 1000);
    },

    getEditionFilter: function () {
        if (!this._editionFilter) {
            this._editionFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Em Edição',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(1);
                }
            });
        }

        return this._editionFilter;
    },

    getRequestedFilter: function () {
        if (!this._requestedFilter) {
            this._requestedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Solicitado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(2);
                }
            });
        }

        return this._requestedFilter;
    },

    getApprovedFilter: function () {
        if (!this._approvedFilter) {
            this._approvedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Aprovado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(3);
                }
            });
        }

        return this._approvedFilter;
    },

    getRefusedFilter: function () {
        if (!this._refusedFilter) {
            this._refusedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Recusado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(4);
                }
            });
        }

        return this._refusedFilter;
    },

    getCanceledFilter: function () {
        if (!this._canceledFilter) {
            this._canceledFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Cancelado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(5);
                }
            });
        }

        return this._canceledFilter;
    },

    getRequiredFilter: function () {
        if (!this._requiredFilter) {
            this._requiredFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Requisitado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(6);
                }
            });
        }

        return this._requiredFilter;
    },

    getEngagedFilter: function () {
        if (!this._engagedFilter) {
            this._engagedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Contratado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(7);
                }
            });
        }

        return this._engagedFilter;
    },

    getRebalancedFilter: function () {
        if (!this._rebalancedFilter) {
            this._rebalancedFilter = Ext._create('Ext.menu.CheckItem', {
                text: 'Reequilibrado',
                checked: (this.filterStatus.indexOf(1) >= 0) ? true : false,
                scope: this,
                hideOnClick: false,
                handler: function () {
                    this.toggleStatus(8);
                }
            });
        }

        return this._rebalancedFilter;
    },

    getFilterAction: function () {
        if (!this._filterAction)
            this._filterAction = Ext._create('Ext.Button', {
                text: 'Filtro',
                iconCls: 'icon-patrimonio icon-pat-filter',
                menu: [
                    this.getEditionFilter(),
                    this.getRequestedFilter(),
                    this.getApprovedFilter(),
                    this.getRefusedFilter(),
                    this.getCanceledFilter(),
                    this.getRequiredFilter(),
                    this.getEngagedFilter(),
                    this.getRebalancedFilter()

                ]
            });

        return this._filterAction;
    },

    doubleClick: function (grid) {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            Ext._create('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerWindow', {
                action: 'update',
                oId: selected.get('pk'),
                params: this.getParams(),
                values: selected.data
            }).show();
        }
    },

    constructor: function (cfg) {
        cfg = (cfg ? cfg : {});
        if (cfg.filterStatus)
            this.filterStatus = cfg.filterStatus;
        else {
            this.filterStatus = [1, 2, 3, 4, 5, 6, 7, 8];
        }

        Ext.applyIf(cfg, {
            doubleClickHandler: this.doubleClick,
            columnAction: false,
            allowCreate: false,
            allowUpdate: false,
            allowRemove: true,
        });

        planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerGrid.superclass.constructor.call(this, cfg);
    },
});

core.RestfulGrid.register(
    'planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerRestful',
    'planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerGrid'
);
