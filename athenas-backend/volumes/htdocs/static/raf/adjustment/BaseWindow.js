Ext._define('raf.adjustment.BaseWindow', {
    extend: 'core.RestfulWindow',

    rest: 'raf.adjustment.BaseRestful',

    activity: function(cfg) {
        var ret = 0;
        if (cfg.hasOwnProperty("params")) {
            if (cfg.params.hasOwnProperty("activity")) {
                ret = cfg.params.activity;
            }
        }
        return ret;
    },

    adjustment: function(cfg) {
        var ret = 0;
        if (cfg.hasOwnProperty("params")) {
            if (cfg.params.hasOwnProperty("adjustment")) {
                ret = cfg.params.adjustment;
            }
        }
        return ret;
    },

    situation: function(cfg) {
        var ret = 5;
        if (cfg.hasOwnProperty("params")) {
            if (cfg.params.hasOwnProperty("situation")) {
                ret = cfg.params.situation;
            }
        }
        return ret;
    },

    quiz: function(cfg) {
        var ret = 0;
        if (cfg.hasOwnProperty("params")) {
            if (cfg.params.hasOwnProperty("quiz")) {
                ret = cfg.params.quiz;
            }
        }
        return ret;
    },

    getNewAmount: function(cfg) {
        var rest = this.factoryRestful();
        adj = this.adjustment(cfg);
        if (adj != 0) {
            rest.newAmount(
                {
                    adjustment: adj,
                },
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            this.getFormPanel(cfg).getForm().setValues(
                                {activity_amount: rst.newAmount, }
                            );
                        }
                        else
                        Ext.Msg.show({
                            title: 'Recálculo da nova quantidade',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    scope: this,
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Recálculo da nova quantidade',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    scope: this,
                    fn: function() {
                    }
                }
            );
        }
    },

    getDataAdjustmentGrid: function(cfg) {
        if(!this._dataAdjustmentGrid) {
            this._dataAdjustmentGrid = Ext._create('raf.adjustment.dataadjustment.Grid', {
                 region: 'center',
                 layout: 'form',
                 border: true,
                 height: 230,
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar:['edit', 'download', '-', 'search', 'accept', 'requestInformation', 'reject'],
                 hideColumns: ['conversation_last_content'],
                 doubleClickHandler: function() { },
                 sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                 params: {
                     activityadjustment: this.adjustment(cfg),
                     activity: this.activity(cfg),
                     adjustmentsituation: this.situation(cfg),
                     quiz: this.quiz(cfg),
                 },
            });
            this.getDataAdjustmentGrid().setFilterProperty('activityadjustment', this.adjustment(cfg), 100, true);
            this.getDataAdjustmentGrid().getStore().on({
                'load': {
                    scope: this,
                    fn: function(store, records) {
                        this.getNewAmount(cfg);
                    }
                },
                'remove': {
                    scope: this,
                    fn: function(record, index) {
                        this.getNewAmount(cfg);
                    }
                },
            });
        }
        return this._dataAdjustmentGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        height: 420,
                        layout: 'form',
                        autoScroll: true,
                        overflow: 'auto',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.58,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Promotoria',
                                                name: 'workerlocation_unicode',
                                                hideLabel: true,
                                                style: {fontWeight: 'bold'},
                                            },
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Questionário',
                                                name: 'quiz_unicode',
                                                hideLabel: true,
                                                style: {fontWeight: 'bold'},
                                            },
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'Item',
                                                name: 'item_unicode',
                                                hideLabel: true,
                                                style: {fontWeight: 'bold'},
                                            },
                                            {
                                                xtype: 'displayfield',
                                                fieldLabel: 'SubItem',
                                                name: 'subitem_unicode',
                                                hideLabel: true,
                                                style: {fontWeight: 'bold'},
                                            },
                                            {
                                                xtype: 'hidden',
                                                name: 'activity',
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.2,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'QUANTIDADE ATUAL',
                                                collapsible: false,
                                                autoHeight:true,
                                                width: 170,
                                                items:[
                                                    {
                                                        xtype: "displayfield",
                                                        name: "activity_amount_submitted",
                                                        hideLabel: true,
                                                        width: '100%',
                                                        style: {textAlign: 'center', fontSize: '32px', fontWeight: 'bolder', color: 'blue'},
                                                    },
                                                ]
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 220,
                                        columnWidth: 0.2,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'NOVA QUANTIDADE',
                                                collapsible: false,
                                                autoHeight:true,
                                                width: 170,
                                                items:[
                                                    {
                                                        xtype: "displayfield",
                                                        id: "new-amount-displayfield",
                                                        name: "activity_amount",
                                                        hideLabel: true,
                                                        width: '100%',
                                                        style: {textAlign: 'center', fontSize: '32px', fontWeight: 'bolder', color: 'red'},
                                                    },
                                                ]
                                            },
                                        ]
                                    }
                                ]
                            },
                            {
                                xtype:'fieldset',
                                title: 'Justificativa (Solicitações anteriores a 01/03/2018)',
                                collapsible: true,
                                collapsed: true,
                                autoHeight:true,
                                width: 855,
                                items:[
                                    {
                                        xtype: "htmleditor",
                                        name: "initial_message",
                                        hideLabel: true,
                                        width: 830,
                                        height: 230,
                                        disabled: true,
                                        enableAlignments : false,
                                        enableColors : false,
                                        enableFont : false,
                                        enableFontSize : false,
                                        enableFormat : false,
                                        enableLinks : false,
                                        enableLists : false,
                                        enableSourceEdit : false,
                                    },
                                ]
                            },
                            {
                                xtype:'fieldset',
                                title: 'Alterações solicitadas',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                width: 855,
                                items:[
                                    this.getDataAdjustmentGrid(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    sendAction: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando Solcitação de Ajustes...'});
        mask.show();
        rest.sendAction(
            {
                adjustment: this.params.adjustment,
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        // getDataAdjustmentGrid().getStore().reload();
                        Ext.Msg.show({
                            title: 'Enviar solicitação de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Ajuste de Atividade',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Ajuste de Atividade',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    cancel: function(cfg) {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Cancelando solicitação...'});
        mask.show();
        rest.action(
            {
                adjustment_list: this.adjustment(cfg),
                answer: 'Solictação cancelada pelo usuário.',
                situation: 4
            },
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        // core.invokeCallback((this.callback || {}).success);
                        Ext.Msg.show({
                            title: 'Cancelar solicitação de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Cancelar solicitação de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Cancelar solicitação de ajuste',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    close: function() {
        if ([0, 1, 5].indexOf(this.params.situation) >= 0) {
            var rest = this.factoryRestful();
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Fechando Solcitação de Ajustes...'});
            mask.show();
            rest.close(
                {
                    adjustment: this.params.adjustment,
                },
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            core.invokeCallback((this.callback || {}).success);
                        }
                        else
                            Ext.Msg.show({
                                title: 'Ajuste de Atividade',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                    }
                },
                {
                    scope: this,
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Ajuste de Atividade',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    scope: this,
                    fn: function() {
                        mask.hide();
                    }
                }
            );
        }
        raf.adjustment.BaseWindow.superclass.close.call(this);
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Enviar solicitação',
                    scope: this,
                    disabled: [5].indexOf(this.situation(cfg)) >= 0 ? false : true,
                    handler: function() {
                        this.sendAction();
                        this.close();
                    }
                },
                {
                    text: 'Cancelar solicitação',
                    scope: this,
                    disabled: true,
                    // disabled: [0/, 1].indexOf(this.situation(cfg)) >= 0 ? false : true,
                    handler: function() {
                        this.cancel(cfg);
                        this.close();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                },
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Ajuste de atividade',
            disableSaveAndNew: true,
            width: 900,
            height: 470,
        });
        raf.adjustment.BaseWindow.superclass.constructor.call(this, cfg);
    }
});
