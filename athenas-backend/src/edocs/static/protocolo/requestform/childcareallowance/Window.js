Ext._define('edocs.protocolo.requestform.childcareallowance.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormChildcareAllowance',

    rest: 'edocs.protocolo.requestform.childcareallowance.Restful',

    width: 900,

    getBankField: function (cfg) {
        if (!this._bankField) {
            this._bankField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Banco',
                name: 'bank',
                anchor: '90%',
                allowBlank: false
            });
        }

        return this._bankField;
    },

    getAgencyField: function (cfg) {
        if (!this._agencyField) {
            this._agencyField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Agência',
                name: 'agency',
                anchor: '90%',
                allowBlank: false
            });
        }

        return this._agencyField;
    },

    getAccountField: function (cfg) {
        if (!this._accountField) {
            this._accountField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Conta',
                name: 'account',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._accountField;
    },

    getChildNameField: function (cfg) {
        if (!this._childNameField) {
            this._childNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome da criança',
                name: 'child_name',
                anchor: '99.7%',
                allowBlank: false
            });
        }

        return this._childNameField;
    },

    getChildTypeField: function (cfg) {
        if (!this._childTypeField) {
            this._childTypeField = Ext._create('Ext.form.ComboBox', {
                hiddenName: 'child_type',
                fieldLabel: 'Tipo vínculo',
                triggerAction: 'all',
                editable: false,
                allowBlank: false,
                anchor: '95%',
                mode: 'local',
                store: [
                    ['0', 'Filho(a)'],
                    ['1', 'Dependente'],
                ]
            });
        }

        return this._childTypeField;
    },

    getChildBirthDateField: function (cfg) {
        if (!this._childBirthDateField) {
            this._childBirthDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de nascimento",
                name: "child_birth_date",
                anchor: '95%',
                allowBlank: false
            });
        }

        return this._childBirthDateField;
    },

    getChildCpfField: function (cfg) {
        if (!this._childCpfField) {
            this._childCpfField = Ext._create('core.fields.CpfField', {
                fieldLabel: 'CPF',
                name: 'child_cpf',
                width: '70%',
                allowBlank: true
            });
        }

        return this._childCpfField;
    },

    getSpouseField: function (cfg) {
        if (!this._spouseField) {
            this._spouseField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Cônjuge',
                name: 'spouse',
                rest: 'rh.employee.Restful',
                anchor: '100%'
            });
        }

        return this._spouseField;
    },

    getReceiverField: function (cfg) {
        if (!this._receiverField) {
            this._receiverField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Responsável pelo recebimento',
                name: 'receiver',
                rest: 'rh.employee.Restful',
                anchor: '100%'
            });
        }

        return this._receiverField;
    },

    getMainFieldSet: function (cfg) {
        return {
            xtype: 'fieldset',
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
                            labelWidth: 60,
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
                    value: 'Requerimento Auxílio Creche',
                    readOnly: true,
                }),
                this.getControlContainer(cfg),
                this.getContactNumberField(cfg)
            ]
        };
    },

    getBankFieldSet: function (cfg) {
        return {
            xtype: 'fieldset',
            title: 'Dados bancários',
            anchor: '100%',
            layout: {
                type: 'hbox',
                align: 'stretchmax'
            },
            items: [
                {
                    xtype: 'container',
                    layout: 'form',
                    labelWidth: 50,
                    flex: 1.1,
                    items: this.getBankField(cfg)
                },
                {
                    xtype: 'container',
                    layout: 'form',
                    labelWidth: 60,
                    flex: 1.1,
                    items: this.getAgencyField(cfg)
                },
                {
                    xtype: 'container',
                    layout: 'form',
                    labelWidth: 50,
                    flex: 1.0,
                    items: this.getAccountField(cfg)
                }
            ]
        };
    },

    getChildFieldSet: function (cfg) {
        return {
            xtype: 'fieldset',
            title: 'Identificação da criança',
            layout: 'form',
            items: [
                this.getChildNameField(cfg),
                {
                    xtype: 'container',
                    anchor: '100%',
                    layout: {
                        type: 'hbox',
                        align: 'stretchmax'
                    },
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 1.0,
                            items: this.getChildTypeField(cfg)
                        },
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 1.2,
                            labelWidth: 120,
                            items: this.getChildBirthDateField(cfg)
                        },
                        {
                            xtype: 'container',
                            layout: 'form',
                            labelWidth: 35,
                            flex: 0.8,
                            items: this.getChildCpfField(cfg)
                        }
                    ]
                }
            ]
        };
    },

    getSpouseFieldSet: function (cfg) {
        return {
            xtype: 'fieldset',
            title: 'Cônjuge (se servidor(a) do MP)',
            layout: 'form',
            items: [
                {
                    xtype: 'panel',
                    layout: 'form',
                    labelWidth: 58,
                    items: this.getSpouseField(cfg)
                },
                {
                    xtype: 'panel',
                    layout: 'form',
                    labelWidth: 180,
                    items: this.getReceiverField(cfg)
                }
            ]
        };
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
                items: [
                    this.getMainFieldSet(cfg),
                    this.getBankFieldSet(cfg),
                    this.getChildFieldSet(cfg),
                    this.getSpouseFieldSet(cfg)
                ]
            });

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
    title: 'Requerimento Auxílio Creche',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.childcareallowance.Window',
    specialType: 'childcareallowance',
    group: "Auxílios, indenizações, vales e valores a receber e a antecipar",
});
