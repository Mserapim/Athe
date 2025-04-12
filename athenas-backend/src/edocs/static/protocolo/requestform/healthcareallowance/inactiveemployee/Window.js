Ext._define('edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RFHealthcareInactiveEmployee',

    rest: 'edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Restful',

    width: 900,

    getAddressField: function (cfg) {
        if (this._addressField) {
            return this._addressField;
        }

        this._addressField = Ext._create('Ext.form.TextField', {
            fieldLabel: 'Endereço',
            name: 'address',
            anchor: '99%',
            allowBlank: false,
        });

        return this._addressField;
    },

    getBeneficiaryTypeFieldSet: function (cfg) {
        if (this._beneficiaryTypeField) {
            return this._beneficiaryTypeField;
        }

        this._beneficiaryTypeField = Ext._create('Ext.form.FieldSet', {
            title: 'Tipo de beneficiário',
            items: [
                {
                    xtype: 'radiogroup',
                    //fieldLabel: 'Tipo de requerimento',
                    //hideLabel: true,
                    columns: 5,
                    name: 'beneficiary_type',
                    hideLabel: true,
                    items: [
                        {
                            xtype: 'radio',
                            boxLabel: 'Aposentado(a)',
                            name: 'beneficiary_type',
                            inputValue: 1,
                            hideLabel: true,
                            checked: true,
                        },
                        {
                            xtype: 'radio',
                            boxLabel: 'Pensionista',
                            name: 'beneficiary_type',
                            inputValue: 2,
                            hideLabel: true,
                            checked: false,
                        },
                    ],
                },
            ],
        });

        return this._beneficiaryTypeField;
    },

    getContactNumberField: function (cfg) {
        if (this._contactNumberField) {
            return this._contactNumberField;
        }

        this._contactNumberField = Ext._create('core.fields.PhoneField', {
            fieldLabel: 'Telefone para contato',
            name: 'contact_number',
            width: '25%',
            allowBlank: false,
        });

        return this._contactNumberField;
    },

    getRequestTypeField: function (cfg) {
        return this.getChoiceFieldSet({
            title: 'Tipo de requerimento',
            name: 'request_type',
            value: (cfg.values || {}).request_type,
            choiceId: 'requestform.HEALTHCARE_INACTIVE_EMP_REQTYPE',
        });
    },

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 92,
            items: [
                {
                    xtype: 'fieldset',
                    items: [
                        this.getCodeField(cfg),
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    flex: 2.75,
                                    layout: 'form',
                                    items: this.getHomeCourtField(cfg),
                                },
                                {
                                    xtype: 'container',
                                    style: 'margin-left: 15px',
                                    flex: 1.25,
                                    layout: 'form',
                                    labelWidth: 30,
                                    items: this.getDocumentTypeField('REQUERIMENTO'),  // mixin
                                },
                            ]
                        },
                        this.getSubjectField(cfg, {
                            value: 'Requerimento - Programa de Assistência à Saúde Suplementar - Membro / Servidor inativo ou pensionista',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                    ],
                },
                {
                    xtype: 'fieldset',
                    layout: 'form',
                    labelWidth: 130,
                    items: [
                        this.getAddressField(cfg),
                        this.getContactNumberField(cfg),
                    ],
                },
                this.getBeneficiaryTypeFieldSet(cfg),
                this.getRequestTypeField(cfg),
            ],
        });

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (this._formPanel) {
            return this._formPanel;
        }

        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            items: [
                this.getMainPanel(cfg),
            ],
        });

        return this._formPanel;
    },
});

// REMOVIDO ITEM DE MENU, CONFORME SOLICITADO NO CHAMADO
// _TODO_: Futuramente, remover modelo Django, API, Template e arquivos JS
// edocs.protocolo.box.MainGrid.registerSpecialType({
//     title: 'Requerimento Auxílio-Saúde - Membro/Servidor inativo',
//     iconCls: '',
//     restWindow: 'edocs.protocolo.requestform.healthcareallowance.inactiveemployee.Window',
//     specialType: 'healthcareallowanceforinactiveemployee',
// });
