var storeCache = {};

Ext._define('corregedoria.inspection.inspection.follow_recommendation.ReportComplianceWindow', {
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
                        type_response: 'reportCompliance',
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
                storeCache = this._store;
                this._store.load({
                    'scope': this,
                    'callback': function() {
                        if (storeCache.data.items["0"]) {
                            this.getFormPanel().getForm().setValues({
                                recommendation: storeCache.data.items["0"].data.recommendation,
                                deadline_grid: storeCache.data.items["0"].data.deadline_grid,
                                execution_organ: storeCache.data.items["0"].data.execution_organ_unicode,
                                inspection_period: storeCache.data.items["0"].data.inspection_date_initial_formatted + ' - ' + storeCache.data.items["0"].data.inspection_date_final_formatted,
                                response: storeCache.data.items["0"].data.deadlinerecommendation_response,
                            });
                            cfg.values.deadlinerecommendation_id = storeCache.data.items["0"].data.deadlinerecommendation_id;
                        }
                    }
                });
            }
            return this._store;
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
                hideItemsToolbar: ['edit', 'download', '-', 'search'],
                params: {deadlinerecommendation: cfg.values.deadlinerecommendation_id,},
            });
            this.getAttachmentsGrid().setFilterProperty('deadlinerecommendation', cfg.values.deadlinerecommendation_id, 100);
        }
        return this._attachmentsGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 555,
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
                                height:405,
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

    saveReportCompliance: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Salvando a informação de cumprimento de recomendação...'});
        Ext.Msg.show({
            title: 'Informar Cumprimento de Recomendação',
            msg: 'Tem certeza que deseja salvar a informação de cumprimento de recomendação?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendation', 'saveReportCompliance'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Informar Cumprimento de Recomendação',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                        } else {
                            Ext.Msg.show({
                                title: 'Informar Cumprimento de Recomendação',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Informar Cumprimento de Recomendação',
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

    sendReportCompliance: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Informar Cumprimento de Recomendação...'});
        Ext.Msg.show({
            title: 'Informar Cumprimento de Recomendação',
            msg: 'Tem certeza que deseja enviar as informações de cumprimento de recomendação?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendation', 'sendReportCompliance'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Informar Cumprimento de Recomendação',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Informar Cumprimento de Recomendação',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Informar Cumprimento de Recomendação',
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

    cancelReportCompliance: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Cancelando a informação de cumprimento de recomendação...'});
        Ext.Msg.show({
            title: 'Cancelar Informar Cumprimento de Recomendação',
            msg: 'Tem certeza que deseja cancelar a a informação de cumprimento de recomendação?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendation', 'cancelReportCompliance'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Cancelar Informar Cumprimento de Recomendação',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Cancelar Informar Cumprimento de Recomendação',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Informar Cumprimento de Recomendação',
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

    cleanReportCompliance: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('INSPECTIONFollowRecommendation', 'cancelReportCompliance'),
            callback: function() {
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if (rst.success == true) {
                    // Ext.Msg.show({
                    //     title: 'Limpando Informar Cumprimento de Recomendação',
                    //     msg: rst.message,
                    //     icon: Ext.Msg.INFO,
                    //     buttons: Ext.Msg.OK
                    // });
                    core.invokeCallback((this.callback || {}).success);
                    cfg.values.recommendationsGrid.getStore().reload();
                    this.close();
                } else {
                    Ext.Msg.show({
                        title: 'Limpando Informar Cumprimento de Recomendação',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Informar Cumprimento de Recomendação',
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
                        this.saveReportCompliance(cfg);
                    }
                },
                {
                    id: 'btn_send',
                    text: '<b>Enviar Informação de Cumprimento de Recomendação</b>',
                    scope: this,
                    handler: function() {
                        this.sendReportCompliance(cfg);
                    }
                },
                {
                    id: 'btn_cancel',
                    text: 'Cancelar envio',
                    scope: this,
                    handler: function() {
                        this.cancelReportCompliance(cfg);
                    }
                },
                {
                    id: 'btn_close',
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                        // this.cleanReportCompliance(cfg);
                        // cfg.values.recommendationsGrid.getStore().reload();
                    }
                },
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Informar Cumprimento de Recomendação',
            width: 1200,
            height: 625,
            modal: true,
        });
        Ext.apply(cfg, {
            ds: this.store(cfg),
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.inspection.inspection.follow_recommendation.ReportComplianceWindow.superclass.constructor.call(this, cfg);
    }

});
