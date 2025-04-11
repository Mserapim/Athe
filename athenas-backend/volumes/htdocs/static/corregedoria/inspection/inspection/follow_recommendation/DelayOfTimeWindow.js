var storeCache = {};

Ext._define('corregedoria.inspection.inspection.follow_recommendation.DelayOfTimeWindow', {
    extend: 'Ext.Window',

    store: function(cfg) {
        if(!this._store) {
            this._store = Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONFollowRecommendation', 'get_recommendation')
                    }),
                    baseParams: {
                        recommendation: cfg.values.recommendation,
                        type_response: 'delayOfTime',
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "recommendation"},
                            {type: "auto", name: "deadline_grid"},
                            {type: "auto", name: "execution_organ_unicode"},
                            {type: "auto", name: "inspection_date_initial_formatted"},
                            {type: "auto", name: "inspection_date_final_formatted"},
                            {type: "auto", name: "deadlinerecommendation_id"},
                            {type: "auto", name: "deadlinerecommendation_response"},
                        ]
                    })
                });
                scache = this._store;
                // storeCache = this._store;
                this._store.load({
                    'scope': this,
                    'callback': function() {
                        if (scache.data.items["0"]) {
                        // if (storeCache.data.items["0"]) {
                            this.getFormPanel().getForm().setValues({
                                recommendation: scache.data.items["0"].data.recommendation,
                                // recommendation: storeCache.data.items["0"].data.recommendation,
                                deadline_grid: scache.data.items["0"].data.deadline_grid,
                                // deadline_grid: storeCache.data.items["0"].data.deadline_grid,
                                execution_organ: scache.data.items["0"].data.execution_organ_unicode,
                                // execution_organ: storeCache.data.items["0"].data.execution_organ_unicode,
                                inspection_period: scache.data.items["0"].data.inspection_date_initial_formatted + ' - ' + scache.data.items["0"].data.inspection_date_final_formatted,
                                // inspection_period: storeCache.data.items["0"].data.inspection_date_initial_formatted + ' - ' + storeCache.data.items["0"].data.inspection_date_final_formatted,
                                response: scache.data.items["0"].data.deadlinerecommendation_response,
                                // response: storeCache.data.items["0"].data.deadlinerecommendation_response,
                            });
                            cfg.values.deadlinerecommendation_id = scache.data.items["0"].data.deadlinerecommendation_id;
                            // cfg.values.deadlinerecommendation_id = storeCache.data.items["0"].data.deadlinerecommendation_id;
                            // this.getAttachmentsGrid().params = {deadlinerecommendation: cfg.values.deadlinerecommendation_id,};
                            // this.getAttachmentsGrid().setFilterProperty('deadlinerecommendation', cfg.values.deadlinerecommendation_id, 100);
                        }
                    }
                });
            }
            return this._store;
    },

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.inspection.inspection.follow_recommendation.attachments.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 160,
                gridAutoLoad: true,
                columnAction: false,
                disabled: true,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {deadlinerecommendation: cfg.values.deadlinerecommendation_id,},
            });
            this.getAttachmentsGrid().setFilterProperty('deadlinerecommendation', cfg.values.deadlinerecommendation_id, 100);
        }
        return this._attachmentsGrid;
    },

    getEditor: function (cfg) {
        if (!this._ckeditoField) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {
                allowBlank: true,
                startupFocus: false,
                editorConfig: {
                    forcePasteAsPlainText: true
                },
            });
            this._ckeditoField = Ext._create('toolkit.fields.CKEditor', cfg);
        }
        return this._ckeditoField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 755,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 115,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        name: 'execution_organ',
                                        fieldLabel: 'Órgão de Execução',
                                        style: {fontWeight: 'bold'},
                                    },
                                    {
                                        xtype: 'displayfield',
                                        name: 'inspection_period',
                                        fieldLabel: 'Período de Inspeção',
                                        style: {fontWeight: 'bold'},
                                    },
                                ]
                            },
                            {
                                xtype:'fieldset',
                                title: 'Recomendação',
                                collapsible: false,
                                collapsed: false,
                                height: 175,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 1,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'recommendation',
                                                hideLabel: true,
                                                style: {textAlign: 'justify', fontSize: '14px'},
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 35,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'deadline_grid',
                                                fieldLabel: 'Prazo',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            {
                                xtype:'fieldset',
                                title: 'Resposta',
                                collapsible: false,
                                collapsed: false,
                                height:505,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 1,
                                        items: [
                                            this.getEditor({
                                                name: 'response',
                                                width: 1145,
                                                height: 275
                                            }),

                                            {
                                                xtype:'fieldset',
                                                title: 'Anexos',
                                                collapsible: false,
                                                collapsed: false,
                                                height: 195,
                                                items:[
                                                    this.getAttachmentsGrid(cfg),
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._formPanel;
    },

    saveDelayOfTime: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Salvando solicitação de dilação de prazo...'});
        Ext.Msg.show({
            title: 'Solicitação Dilação de Prazo',
            msg: 'Tem certeza que deseja salvar a solicitação dilação de prazo?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendation', 'saveDelayOfTime'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Solicitação Dilação de Prazo',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                        } else {
                            Ext.Msg.show({
                                title: 'Solicitação Dilação de Prazo',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Solicitação Dilação de Prazo',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    params: values,
                });
            }
        });
    },

    sendDelayOfTime: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Solicitando dilação de prazo...'});
        Ext.Msg.show({
            title: 'Solicitação Dilação de Prazo',
            msg: 'Tem certeza que deseja solicitar dilação de prazo?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendation', 'sendDelayOfTime'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Solicitação Dilação de Prazo',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Solicitação Dilação de Prazo',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Solicitação Dilação de Prazo',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    params: values,
                });
            }
        });
    },

    cancelDelayOfTime: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Cancelando solicitação de dilação de prazo...'});
        Ext.Msg.show({
            title: 'Cancelar Solicitação Dilação de Prazo',
            msg: 'Tem certeza que deseja cancelar a solicitação de dilação de prazo?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendation', 'cancelDelayOfTime'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Cancelar Solicitação Dilação de Prazo',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Cancelar Solicitação Dilação de Prazo',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Solicitação Dilação de Prazo',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    },
                    params: values,
                });
            }
        });
    },

    cleanDelayOfTime: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('INSPECTIONFollowRecommendation', 'cancelDelayOfTime'),
            callback: function() {

            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if (rst.success == true) {
                    // Ext.Msg.show({
                    //     title: 'Limpando Solicitação Dilação de Prazo',
                    //     msg: rst.message,
                    //     icon: Ext.Msg.INFO,
                    //     buttons: Ext.Msg.OK
                    // });
                    core.invokeCallback((this.callback || {}).success);
                    cfg.values.recommendationsGrid.getStore().reload();
                    this.close();
                } else {
                    Ext.Msg.show({
                        title: 'Limpando Solicitação Dilação de Prazo',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Solicitação Dilação de Prazo',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            params: values,
        });
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    id: 'btn_save',
                    text: 'Salvar',
                    scope: this,
                    handler: function() {
                        this.saveDelayOfTime(cfg);
                    }
                },
                {
                    id: 'btn_send',
                    text: '<b>Enviar Solicitação de Dilação de Prazo</b>',
                    scope: this,
                    handler: function() {
                        this.sendDelayOfTime(cfg);
                    }
                },
                {
                    id: 'btn_cancel',
                    text: 'Cancelar solicitação',
                    scope: this,
                    handler: function() {
                        this.cancelDelayOfTime(cfg);
                    }
                },
                {
                    id: 'btn_close',
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                        // this.cleanDelayOfTime(cfg);
                        // cfg.values.recommendationsGrid.getStore().reload();
                    }
                },
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Solicitar Dilação de Prazo',
            width: 1200,
            height: 820,
            modal: true,
        });
        Ext.apply(cfg, {
            ds: this.store(cfg),
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.inspection.inspection.follow_recommendation.DelayOfTimeWindow.superclass.constructor.call(this, cfg);
    }

});
