Ext._define('edocs.protocolo.requestform.childbirthallowance.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormChildbirthAllowance',

    rest: 'edocs.protocolo.requestform.childbirthallowance.Restful',

    width: 900,

    getChildNameField: function (cfg) {
        if (!this._childNameField) {
            this._childNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome da criança',
                name: 'child_name',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._childNameField;
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
                        value: 'Requerimento Auxílio Natalidade',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getContactNumberField(cfg),
                    {
                        xtype: 'container',
                        layout: 'form',
                        labelWidth: 100,
                        items: this.getChildNameField(cfg)
                    }
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
    title: 'Requerimento Auxílio Natalidade',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.childbirthallowance.Window',
    specialType: 'childbirthallowance',
    group: "Auxílios, indenizações, vales e valores a receber e a antecipar"
});
