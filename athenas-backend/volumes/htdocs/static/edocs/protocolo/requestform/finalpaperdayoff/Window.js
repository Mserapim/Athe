Ext._define('edocs.protocolo.requestform.finalpaperdayoff.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormFinalPaperDayOff',

    rest: 'edocs.protocolo.requestform.finalpaperdayoff.Restful',

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
                        value: 'Requerimento Concessão para Conclusão de Trabalho de Final de Curso',
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
                                labelWidth: 90,
                                items: this.getStartDateField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 100,
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
    title: 'Requerimento Concessão para Conclusão de TCC',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.finalpaperdayoff.Window',
    specialType: 'finalpaperdayoff',
    group: 'Licenças e afastamentos'
});
