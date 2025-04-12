Ext._define('common.usefulday.nonworkingday.NonWorkingDayCopy', {
    extend: 'Ext.Window',

    getStore: function() {
        if (!this._store) {
            this._store = Ext._create('Ext.data.Store', {
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('CUNNonWorkingDay', 'get_year_list'),
                }),
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {name: 'value', type: 'int'},
                        {name: 'display', type: 'string'},
                    ]
                }),
            });
        }

        return this._store;
    },

    getBaseYearField: function() {
        if (!this._baseYearField) {
            this._baseYearField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Base',
                hiddenName: 'base_year',
                allowBlank: false,
                width: 100,
                valueField: 'value',
                displayField: 'display',
                store: this.getStore(),
                autoLoad: false,
            });
        }

        return this._baseYearField;
    },

    getDestinyYearField: function() {
        if (!this._destinyYearField) {
            this._destinyYearField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Destino',
                hiddenName: 'destiny_year',
                allowBlank: false,
                width: 100,
                valueField: 'value',
                displayField: 'display',
                store: this.getStore(),
                autoLoad: false,
            });
        }

        return this._destinyYearField;
    },

    getFormPanel: function() {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                autoHeight: true,
                items: [
                    {
                        layout: 'column',
                        defaults: {
                            border: false,
                            bodyStyle: 'padding:4px'
                        },
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        title: 'Ano',
                                        xtype: 'fieldset',
                                        collapsible: true,
                                        labelSeparator: '&nbsp;',
                                        labelWidth: 50,
                                        height: 110,
                                        items: [
                                            this.getBaseYearField(),
                                            this.getDestinyYearField()
                                        ]
                                    }
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        title: 'Tipo',
                                        xtype: 'fieldset',
                                        collapsible: true,
                                        labelSeparator: '&nbsp;',
                                        labelWidth: 120,
                                        height: 145,
                                        items: [
                                            {
                                                xtype: "checkbox",
                                                fieldLabel: "Feriados",
                                                allowBlank: true,
                                                name: "holiday",
                                            },
                                            {
                                                xtype: "checkbox",
                                                fieldLabel: "Pontos Facultativos",
                                                allowBlank: true,
                                                name: "facultative",
                                            },
                                            {
                                                xtype: "checkbox",
                                                fieldLabel: "Suspensões",
                                                allowBlank: true,
                                                name: "suspension",
                                            },
                                            {
                                                xtype: "checkbox",
                                                fieldLabel: "Recesso",
                                                allowBlank: true,
                                                name: "recess",
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },

            ]
        });

        return this._formPanel;
    },

    runCopy: function() {
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('CUNNonWorkingDay', 'copy'),
            params: this.getFormPanel().getForm().getValues(),
            success: function(response, opts) {
                var obj = Ext.decode(response.responseText);

                if (obj.success) {
                    this.nonWorkingDayGrid.getStore().reload();
                    Ext.Msg.show({
                        title: 'Concluído',
                        msg: obj.message,
                        buttons: Ext.Msg.OK,
                        icon: Ext.MessageBox.INFO
                    });
                } else {
                    Ext.Msg.show({
                        title: 'Atenção!',
                        msg: obj.message,
                        buttons: Ext.Msg.OK,
                        icon: Ext.MessageBox.WARNING
                    });
                }
            },
            failure: function(response, opts) {
                Ext.Msg.show({
                    title: 'Copiar Calendário',
                    msg: 'Ocorreu um erro ao encerrar fiscal selecionado',
                    buttons: Ext.Msg.OK
                });
            },
            callback: function() {
                // this.destroy();
            }
        });
    },

    doConfirmation: function() {
        ERROR_MAP = {
            'base_year': 'Informe o ano base',
            'destiny_year': 'Informe o ano de destino',
            'equals_year': 'Os anos base e destino devem ser diferentes',
        };

        var alert = [];

        if (!this.getBaseYearField().getValue())
            alert.push(ERROR_MAP.base_year);
        if (!this.getDestinyYearField().getValue())
            alert.push(ERROR_MAP.destiny_year);
        if (this.getBaseYearField().getValue() == this.getDestinyYearField().getValue())
            alert.push(ERROR_MAP.equals_year);

        if (alert.length > 0)
            Ext.Msg.show({
                title: 'Erros encontrados',
                msg: alert.join('<br />'),
                buttons: Ext.Msg.OK,
                icon: Ext.MessageBox.ERROR
            });
        else
            Ext.Msg.show({
                title: 'Confirmação',
                msg: 'Está certo disso?',
                buttons: Ext.Msg.YESNO,
                icon: Ext.MessageBox.QUESTION,
                scope: this,
                fn: function(b) {
                    if (b == 'no')
                        return;
                    else if (b == 'yes')
                        this.runCopy();
                }
            });
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(cfg, {
            title: 'Copiar calendário',
            autoHeight: true,
            width: 400,
            modal: true,
            labelAlign: 'top',
            items: this.getFormPanel(),
            buttons: [
                {
                    text: 'Copiar',
                    iconCls: 'icon-usefulday icon-usefulday-copy-calendar',
                    scope: this,
                    handler: this.doConfirmation
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ]
        });

        common.usefulday.nonworkingday.NonWorkingDayCopy.superclass.constructor.call(this, cfg);
    }
});
