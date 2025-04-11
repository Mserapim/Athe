Ext._define('corregedoria.inspection.inspection.follow_recommendation.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.inspection.inspection.follow_recommendation.Restful',
    restWindow: 'corregedoria.inspection.inspection.follow_recommendation.Window',

    configOrderToolBar: ['search', 'menu', '-'],

    getDelayOfTimeWindow: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (selected.data.finalized == true) {
                Ext.Msg.show({
                    title: 'Solicitar Dilação de Prazo',
                    msg: 'Recomendação já finalizada pela Corregedoria-geral.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            } else {
                if (selected.data.reportcompliance_pending == true) {
                    Ext.Msg.show({
                        title: 'Solicitar Dilação de Prazo',
                        msg: 'Existe um Envio de Informações de Cumprimento pendente de análise.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                } else {
                    if (selected.data.reportcompliance_editing == true) {
                        Ext.Msg.show({
                            title: 'Solicitar Dilação de Prazo',
                            msg: 'Existe um Envio de Informações de Cumprimento em edição.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    } else {
                        if (selected.data.delayoftime_pending != true) {
                            if (selected.data.deadline_grid != '') {
                                Ext._create('corregedoria.inspection.inspection.follow_recommendation.DelayOfTimeWindow', {
                                    values: {
                                        recommendation: selected.data.pk,
                                        recommendationsGrid: this,
                                    },
                                }).show();
                            } else {
                                Ext.Msg.show({
                                    title: 'Solicitar Dilação de Prazo',
                                    msg: 'Recomendação sem prazo definido.',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        } else {
                            Ext.Msg.show({
                                title: 'Solicitar Dilação de Prazo',
                                msg: 'Existe uma Solicitação de Dilação de Prazo pendente de análise.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    }
                }
            }
        } else {
            Ext.Msg.show({
                title: 'Solicitar Dilação de Prazo',
                msg: 'Primeiro selecione uma Recomendação.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getReportComplianceWindow: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (selected.data.finalized == true) {
                Ext.Msg.show({
                    title: 'Solicitar Dilação de Prazo',
                    msg: 'Recomendação já finalizada pela Corregedoria-geral.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            } else {
                if (selected.data.delayoftime_pending == true) {
                    Ext.Msg.show({
                        title: 'Informar Cumprimento de Recomendação',
                        msg: 'Existe uma Solicitação de Dilação de Prazo pendente de análise.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                } else {
                    if (selected.data.delayoftime_editing == true) {
                        Ext.Msg.show({
                            title: 'Informar Cumprimento de Recomendação',
                            msg: 'Existe uma Solicitação de Dilação de Prazo em edição.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    } else {
                        if (selected.data.reportcompliance_pending != true) {
                            if (selected.data.deadline_grid != '') {
                                Ext._create('corregedoria.inspection.inspection.follow_recommendation.ReportComplianceWindow', {
                                    values: {
                                        recommendation: selected.data.pk,
                                        recommendationsGrid: this,
                                    },
                                }).show();
                            } else {
                                Ext.Msg.show({
                                    title: 'Informar Cumprimento de Recomendação',
                                    msg: 'Recomendação sem prazo definido.',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        } else {
                            Ext.Msg.show({
                                title: 'Informar Cumprimento de Recomendação',
                                msg: 'Existe um Envio de Informações de Cumprimento pendente de análise.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });

                        }
                    }
                }
            }
        } else {
            Ext.Msg.show({
                title: 'Informar Cumprimento de Recomendação',
                msg: 'Primeiro selecione uma Recomendação.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getMenuAction: function() {
        if(!this._downmenuAction){
            this._downmenuAction = new Ext.Button({
                xtype: 'button',
                text: 'Opções',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                menu: [
                    {
                        text: 'Informar cumprimento',
                        iconCls: 'icon-crgmpe icon-crgmpe-witness',
                        scope: this,
                        handler: function() { this.getReportComplianceWindow(); }
                    },
                    '-',
                    {
                        text: 'Solicitar Dilação de Prazo',
                        iconCls: 'icon-crgmpe icon-crgmpe-calendar-plus',
                        scope: this,
                        handler: function() { this.getDelayOfTimeWindow(); }
                    },
                ]
            });
        }
        return this._downmenuAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 70, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Recomendação', dataIndex: 'recommendation', id: 'autoExpandColumn', },
                    {header: 'Prazo', dataIndex: 'deadline_grid', width: 80, },
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                columnAction: false
            }
        );
        corregedoria.inspection.inspection.follow_recommendation.Grid.superclass.constructor.call(this, cfg);
    }
});
core.RestfulGrid.register(
    'corregedoria.inspection.inspection.follow_recommendation.Restful',
    'corregedoria.inspection.inspection.follow_recommendation.Grid'
);
