Ext._define('edocs.protocolo.requestform.functionalidentity.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormFunctionalIdentity',

    rest: 'edocs.protocolo.requestform.functionalidentity.Restful',

    width: 900,

    getIsReissueField: function (cfg) {
        if (!this._isReissueField) {
            this._isReissueField = Ext._create('Ext.form.Checkbox', {
                boxLabel: '2ª Via',
                name: 'is_reissue',
                value: 'off'
            });
        }

        return this._isReissueField;
    },

    getReissueReasonField: function (cfg) {
        if (!this._reissueReasonField) {
            this._reissueReasonField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Motivo da 2ª via',
                editable: false,
                hiddenName: 'reissue_reason',
                width: 200,
                choiceId: 'requestform.FUNCTIONALIDENTITY_REISSUE_REASON'
            });
        }

        return this._reissueReasonField;
    },

    getOriginalPublicInstitutionField: function (cfg) {
        if (!this._originalPublicInstitutionField) {
            this._originalPublicInstitutionField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Órgão de origem',
                name: 'original_public_institution',
                anchor: '99%'
            });
        }

        return this._originalPublicInstitutionField;
    },

    getOriginalJobPositionField: function (cfg) {
        if (!this._originalJobPositionField) {
            this._originalJobPositionField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Cargo de origem',
                name: 'original_job_position',
                anchor: '99%'
            });
        }

        return this._originalJobPositionField;
    },

    getOriginalEmploymentDateField: function (cfg) {
        if (!this._originalEmploymentDateField) {
            this._originalEmploymentDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data admissão origem",
                name: "original_employment_date",
                width: 200
            });
        }

        return this._originalEmploymentDateField;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                layout: 'form',
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
                                        layout: 'form',
                                        flex: 2.75,
                                        labelWidth: 60,
                                        items: this.getHomeCourtField(cfg)
                                    },
                                    {
                                        xtype: 'container',
                                        layout: 'form',
                                        flex: 1.25,
                                        labelWidth: 40,
                                        items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                                    }
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 60,
                                items: this.getSubjectField(cfg, {
                                    value: 'Requerimento Solicitação de Emissão de Cédula de Identidade Funcional',
                                    readOnly: true,
                                }),
                            },
                            this.getControlContainer(cfg),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 1,
                                items: this.getIsReissueField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 6.0,
                                labelWidth: 100,
                                items: this.getReissueReasonField(cfg)
                            }
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Servidor à disposição',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 100,
                                items: this.getOriginalPublicInstitutionField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 100,
                                items: this.getOriginalJobPositionField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                labelWidth: 130,
                                items: this.getOriginalEmploymentDateField(cfg)
                            }
                        ]
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
                items: this.getMainPanel(cfg)
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento Cédula Identidade Funcional',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.functionalidentity.Window',
    specialType: 'functionalidentity',
    group: 'Requerimento gerais para integrantes'
});
