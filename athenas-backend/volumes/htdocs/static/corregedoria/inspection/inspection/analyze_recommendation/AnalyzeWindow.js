var storeCache = {};

Ext._define('corregedoria.inspection.inspection.analyze_recommendation.AnalyzeWindow', {
    extend: 'Ext.Window',

    store: function(cfg) {
        if(!this._store) {
            this._store = Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('INSPECTIONFollowRecommendationCorregedoria', 'get_recommendation')
                    }),
                    baseParams: {
                        recommendation: cfg.values.recommendation,
                    },
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {type: "auto", name: "recommendation"},
                            {type: "auto", name: "deadline"},
                            {type: "auto", name: "deadline_grid"},
                            {type: "auto", name: "execution_organ_unicode"},
                            {type: "auto", name: "inspection_date_initial_formatted"},
                            {type: "auto", name: "inspection_date_final_formatted"},
                            {type: "auto", name: "deadlinerecommendation_id"},
                            // {type: "auto", name: "deadlinerecommendation_response"},
                            {type: "auto", name: "deadlinerecommendation_decision"},
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
                            deadline: storeCache.data.items["0"].data.deadline,
                            deadline_grid: storeCache.data.items["0"].data.deadline_grid,
                            execution_organ: storeCache.data.items["0"].data.execution_organ_unicode,
                            inspection_period: storeCache.data.items["0"].data.inspection_date_initial_formatted + ' - ' + storeCache.data.items["0"].data.inspection_date_final_formatted,
                            decision: storeCache.data.items["0"].data.deadlinerecommendation_decision,
                            // deadlinerecommendation_id: storeCache.data.items["0"].data.deadlinerecommendation_id,
                            // response: storeCache.data.items["0"].data.deadlinerecommendation_response,
                        });
                        cfg.values.deadlinerecommendation_id = storeCache.data.items["0"].data.deadlinerecommendation_id;
                        // this.getAttachmentsGrid().params = {deadlinerecommendation: cfg.values.deadlinerecommendation_id,};
                        // this.getAttachmentsGrid().setFilterProperty('deadlinerecommendation', cfg.values.deadlinerecommendation_id, 100);
                        // if (cfg.values.delayoftime == false) {
                        //     Ext.getCmp('deadline').disable();
                        // }
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
                        xtype:'fieldset',
                        title: 'Decisão',
                        collapsible: false,
                        collapsed: false,
                        height:620,
                        items:[
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'column',
                                items: [
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 1,
                                        columnWidth: 0.8,
                                        items: [
                                            this.getEditor({
                                                name: 'decision',
                                                width: 905,
                                                height: 385
                                            })
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        columnWidth: 0.2,
                                        items: [
                                            {
                                                xtype:'fieldset',
                                                title: 'Configurações',
                                                hideLabel: true,
                                                collapsible: false,
                                                autoHeight:true,
                                                width: 230,
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        labelWidth: 70,
                                                        items: [
                                                            {
                                                                xtype:'panel',
                                                                autoHeight:true,
                                                                layout: 'form',
                                                                labelWidth: 65,
                                                                items: [
                                                                    {
                                                                        xtype: 'displayfield',
                                                                        name: 'deadline_grid',
                                                                        fieldLabel: 'Prazo atual',
                                                                        style: {fontWeight: 'bold'},
                                                                    },
                                                                ],
                                                            },
                                                            {
                                                                xtype: 'datefield',
                                                                id: 'deadline',
                                                                name: 'deadline',
                                                                fieldLabel: 'Novo prazo',
                                                                allowBlank: true,
                                                                width: 125,
                                                            },
                                                        ]
                                                    },
                                                ],
                                            },
                                            {
                                                xtype:'fieldset',
                                                title: 'Marcar como Finalizada',
                                                hideLabel: true,
                                                collapsible: false,
                                                autoHeight:true,
                                                width: 230,
                                                items: [
                                                    {
                                                        xtype:'panel',
                                                        autoHeight:true,
                                                        layout: 'form',
                                                        labelWidth: 1,
                                                        items: [
                                                            {
                                                                xtype: 'combo',
                                                                hiddenName: 'finalized',
                                                                width: 195,
                                                                value: 1,
                                                                editable: false,
                                                                triggerAction: 'all',
                                                                store: [
                                                                    [1, ''],
                                                                    [2, 'SIM'],
                                                                    [3, 'NÃO'],
                                                                ],
                                                            }
                                                        ]
                                                    },
                                                ],
                                            },
                                        ]
                                    },
                                ]
                            },
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
            });
        }
        return this._formPanel;
    },

    saveDecision: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Salvando análise de recomendação...'});
        console.log(values);
        Ext.Msg.show({
            title: 'Análise de Recomendações',
            msg: 'Tem certeza que deseja salvar a decisão?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendationCorregedoria', 'saveDecision'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Análise de Recomendações',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                        } else {
                            Ext.Msg.show({
                                title: 'Análise de Recomendações',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Análise de Recomendações',
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

    sendDecision: function(cfg) {
        var values = this.getFormPanel().getForm().getValues();
        values.recommendation = cfg.values.recommendation;
        values.deadlinerecommendation_id = cfg.values.deadlinerecommendation_id;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando Decisão de Recomendação...'});
        Ext.Msg.show({
            title: 'Análise de Recomendações',
            msg: 'Tem certeza que deseja enviar a Decisão?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendationCorregedoria', 'sendDecision'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Análise de Recomendações',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            core.invokeCallback((this.callback || {}).success);
                            cfg.values.recommendationsGrid.getStore().reload();
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Análise de Recomendações',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Análise de Recomendações',
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

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    id: 'btn_save',
                    text: 'Salvar',
                    scope: this,
                    handler: function() {
                        this.saveDecision(cfg);
                    }
                },
                {
                    id: 'btn_send',
                    text: '<b>Assinar/Enviar Decisão</b>',
                    scope: this,
                    handler: function() {
                        this.sendDecision(cfg);
                    }
                },
                {
                    id: 'btn_close',
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
            title: 'Análise de Recomendações',
            width: 1200,
            height: 700,
            modal: true,
        });
        Ext.apply(cfg, {
            ds: this.store(cfg),
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.inspection.inspection.analyze_recommendation.AnalyzeWindow.superclass.constructor.call(this, cfg);
        // console.log(cfg);
    }

});
