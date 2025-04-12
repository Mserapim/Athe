Ext._define('edocs.protocolo.requestform.weddingdayoff.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormWeddingDayOff',

    rest: 'edocs.protocolo.requestform.weddingdayoff.Restful',

    width: 900,

    getStartDateField: function (cfg) {
        if (!this._startDateField) {
            this._startDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de início",
                name: "start_date",
                width: 150,
                allowBlank: false
            });
        }

        return this._startDateField;
    },

    getEndDateField: function (cfg) {
        if (!this._endDateField) {
            this._endDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de término",
                name: "end_date",
                width: 150,
                allowBlank: false
            });
        }

        return this._endDateField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                items: [
                    this.getCodeField(cfg),
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 2.75,
                                items: this.getHomeCourtField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.25,
                                labelWidth: 50,
                                items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                            }
                        ]
                    },
                    this.getSubjectField(cfg, {
                        value: 'Requerimento Concessão por Motivo de Casamento',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                items: this.getContactNumberField(cfg, { width: '80%' })
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 85,
                                items: this.getStartDateField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 95,
                                items: this.getEndDateField(cfg)
                            }
                        ]
                    },
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 'auto',
                autoHeight: true,
                items: [
                    this.getMainPanel(cfg),
                    {
                        layout: 'vbox',
                        border: false,
                        height: 200,
                        items: this.getAttachmentPanel(cfg)
                    }
                ]
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Concessão por Motivo de Casamento',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.weddingdayoff.Window',
    specialType: 'weddingdayoff',
    group: 'Licenças e afastamentos'
});
