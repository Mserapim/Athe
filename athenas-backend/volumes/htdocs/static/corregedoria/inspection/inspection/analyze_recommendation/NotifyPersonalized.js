Ext._define('corregedoria.inspection.inspection.follow_recommendation.NotifyPersonalized', {
    extend: 'Ext.Window',

    getNotifyGrid: function() {
        if(!this._notifyGrid) {
            this._notifyGrid = Ext._create('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Grid', {
                region: 'north',
                title: 'Histórico de Noticações',
                height: 500,
                columnAction: false,
                configOrderToolBar: ['search'],
                hiddenFilter: true,
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });
        }
        return this._notifyGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        items: [
                            {
                                xtype:'fieldset',
                                title: 'Inspeção/Correição',
                                collapsible: false,
                                collapsed: false,
                                autoHeight:true,
                                items:[
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 110,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'execution_organ',
                                                fieldLabel: 'Órgão de Execução',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                    {
                                        xtype:'panel',
                                        autoHeight:true,
                                        layout: 'form',
                                        labelWidth: 155,
                                        items: [
                                            {
                                                xtype: 'displayfield',
                                                name: 'inspection_date',
                                                fieldLabel: 'Data da Inspeção/Correição',
                                                style: {fontWeight: 'bold'},
                                            },
                                        ]
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype: 'panel',
                        // title: 'Protocolo para envio...',
                        layout: 'form',
                        // height: 500,
                        items: [
                            {
                                xtype: 'ckeditor',
                                hideLabel: true,
                                allowBlank: false,
                                name: 'message',
                                height: 420,
                                submit: true,
                                toolbarGroups: [
                                    {name: 'styles', itens: ['Format']},
                                    {name: 'clipboard'},
                                    {name: 'editing'},
                                    {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                                    {
                                        name: 'paragraph',
                                        groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                                    },
                                ],
                                value: 'Vencido(s) o(s) prazo(s) fixado(s), solicito a Vossa Excelência, no <b>prazo de 5 (cinco) dias</b>, informações a respeito do cumprimento da(s) recomendação(ões) expedida(s) pela Corregedoria-Geral por ocasião da última inspeção realizada na <b>'+ cfg.values.execution_organ+'</b>.'
                            },
                            {
                                xtype: 'datefield',
                                fieldLabel: 'Vencimento em',
                                name: 'deadline',
                                allowBlank: false,
                            },
                        ]
                    },
                ]
            });
        }
        return this._formPanel;
    },

    send: function(cfg) {
        Ext.Msg.show({
            title: 'Preencher Inspeção/Correição',
            msg: 'Em desenvolvimento...',
            icon: Ext.Msg.INFO,
            buttons: Ext.Msg.OK
        });

        var values = this.getFormPanel().getForm().getValues();
        values.inspection = cfg.values.inspection;
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando notificação de atraso (via e-Doc)...'});
        Ext.Msg.show({
            title: 'Enviar notificação de atraso (via e-Doc)',
            msg: 'Tem certeza que deseja enviar notificação?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn=='no') return;
                mask.show();
                Ext.Ajax.request({
                    scope: this,
                    url: core.callAction('INSPECTIONFollowRecommendationCorregedoria', 'notify_delay'),
                    callback: function() {
                        mask.hide();
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        if (rst.success == true) {
                            Ext.Msg.show({
                                title: 'Enviar notificação de atraso (via e-Doc)',
                                msg: rst.message,
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK
                            });
                            this.close();
                        } else {
                            Ext.Msg.show({
                                title: 'Enviar notificação de atraso (via e-Doc)',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    failure: function(request) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Enviar notificação de atraso (via e-Doc)',
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
                    text: '<b>Enviar</b>',
                    scope: this,
                    handler: function() {
                        this.send(cfg);
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
            title: 'Enviar Notificação de Atraso (via e-Doc)',
            width: 900,
            height: 700,
            modal: true,
        });
        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.inspection.inspection.follow_recommendation.NotifyPersonalized.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().setValues(
            {
                execution_organ: cfg.values.execution_organ,
                inspection_date: cfg.values.inspection_date_initial + ' à ' + cfg.values.inspection_date_final,
            }
        );
        this.getNotifyGrid().setFilterProperty('inspection', cfg.values.inspection, 101, true);
    }

});
