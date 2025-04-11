Ext._define('edocs.protocolo.requestform.funeralallowance.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormFuneralAllowance',

    rest: 'edocs.protocolo.requestform.funeralallowance.Restful',

    width: 900,

    getDegreeOfKinshipField: function (cfg) {
        if (!this._degreeOfKinshipField) {
            this._degreeOfKinshipField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Grau de parentesco com o(a) falecido(a)',
                name: 'degree_of_kinship',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._degreeOfKinshipField;
    },

    getDeceasedNameField: function (cfg) {
        if (!this._deceasedNameField) {
            this._deceasedNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome do(a) falecido(a)',
                name: 'deceased_name',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._deceasedNameField;
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
                        value: 'Requerimento Auxílio Funeral',
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
                                labelWidth: 230,
                                flex: 2.0,
                                items: this.getDegreeOfKinshipField(cfg)
                            },
                        ]
                    },
                    {
                        xtype: 'container',
                        layout: 'form',
                        labelWidth: 140,
                        items: this.getDeceasedNameField(cfg)
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
    title: 'Requerimento Auxílio Funeral',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.funeralallowance.Window',
    specialType: 'funeralallowance',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
