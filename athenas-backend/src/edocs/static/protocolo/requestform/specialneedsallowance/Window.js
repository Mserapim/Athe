Ext._define('edocs.protocolo.requestform.specialneedsallowance.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormSpecialNeedsAllowance',

    rest: 'edocs.protocolo.requestform.specialneedsallowance.Restful',

    width: 900,

    getDependentNameField: function (cfg) {
        if (!this._dependentNameField) {
            this._dependentNameField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome',
                name: 'dependent_name',
                anchor: '99.7%',
                allowBlank: false
            });
        }

        return this._dependentNameField;
    },

    getDependentAddressField: function (cfg) {
        if (!this._dependentAddressField) {
            this._dependentAddressField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Endereço',
                name: 'dependent_address',
                anchor: '99.7%'
            });
        }

        return this._dependentAddressField;
    },

    getDependentBirthDateField: function (cfg) {
        if (!this._dependentBirthDateField) {
            this._dependentBirthDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Data de nascimento',
                name: 'dependent_birth_date',
                width: 130,
                allowBlank: false
            });
        }

        return this._dependentBirthDateField;
    },

    getDependentCpfField: function (cfg) {
        if (!this._dependentCpfField) {
            this._dependentCpfField = Ext._create('core.fields.CpfField', {
                fieldLabel: 'CPF',
                name: 'dependent_cpf',
                width: '70%',
                allowBlank: true
            });
        }

        return this._dependentCpfField;
    },

    getDependentRgField: function (cfg) {
        if (!this._dependentRgField) {
            this._dependentRgField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'RG',
                name: 'dependent_rg',
                width: 150
            });
        }

        return this._dependentRgField;
    },

    getDependentUfField: function (cfg) {
        if (!this._dependentUfField) {
            this._dependentUfField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'UF',
                name: 'dependent_uf',
                width: 100,
                emptyText: '',
                displayField: 'sigla',
                rest: 'rh.estado.Restful'
            });
        }

        return this._dependentUfField;
    },

    getDisabilityTypeField: function (cfg) {
        if (!this._disabilityTypeField) {
            this._disabilityTypeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo de deficiência',
                editable: false,
                hiddenName: 'disability_type',
                anchor: '95%',
                choiceId: 'requestform.SPECIALNEEDSALLOWANCE_DISABILITY_TYPE',
                allowBlank: false
            });
        }

        return this._disabilityTypeField;
    },

    getIcdField: function (cfg) {
        if (!this._icdField) {
            this._icdField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'CID-10 (Código Internacional da Doença)',
                name: 'icd',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._icdField;
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

    getDependentPanel: function (cfg) {
        if (!this._dependentPanel) {
            this._dependentPanel = Ext._create('Ext.Panel', {
                title: 'Dependente',
                frame: true,
                height: 346,
                layout: 'form',
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Identificação do dependente com deficiência',
                        layout: 'form',
                        labelWidth: 60,
                        items: [
                            this.getDependentNameField(cfg),
                            this.getDependentAddressField(cfg),
                            {
                                xtype: 'container',
                                anchor: '100%',
                                layout: 'hbox',
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.5,
                                        labelWidth: 120,
                                        items: this.getDependentBirthDateField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        labelWidth: 30,
                                        flex: 1.0,
                                        items: this.getDependentCpfField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        labelWidth: 25,
                                        flex: 1.0,
                                        items: this.getDependentRgField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        labelWidth: 25,
                                        flex: 1.0,
                                        items: this.getDependentUfField(cfg)
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                anchor: '100%',
                                layout: 'hbox',
                                items: [
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        labelWidth: 115,
                                        flex: 1.2,
                                        items: this.getDisabilityTypeField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        labelWidth: 230,
                                        flex: 0.8,
                                        items: this.getIcdField(cfg)
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Cônjuge ou companheiro(a), se servidor(a) do MP',
                        layout: 'form',
                        height: 180,
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 58,
                                items: this.getSpouseField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 180,
                                items: this.getReceiverField(cfg)
                            }
                        ]
                    }
                ]
            });
        }

        return this._dependentPanel;
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
                        value: 'Requerimento Auxílio-Especial',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getContactNumberField(cfg)
                ]
            });
        }

        return this._mainPanel;
    },

    getInformationPanel: function (cfg) {
        if (!this._informationPanel) {
            this._informationPanel = Ext._create('Ext.Panel', {
                title: 'Informações',
                frame: false,
                items: [
                    this.getMainPanel(cfg),
                    {
                        xtype: 'panel',
                        layout: 'vbox',
                        height: 200,
                        border: false,
                        items: this.getAttachmentPanel(cfg)
                    },
                ]
            });
        }

        return this._informationPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                deferredRender: true,
                items: [
                    this.getInformationPanel(cfg),
                    this.getDependentPanel(cfg)
                ]
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg)
            });
        }

        return this._formPanel;
    },
});


edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Auxílio-Especial',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.specialneedsallowance.Window',
    specialType: 'specialneedsallowance',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
