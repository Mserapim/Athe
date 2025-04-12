Ext._define('edocs.protocolo.requestform.mealallowance.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormMealAllowance',

    rest: 'edocs.protocolo.requestform.mealallowance.Restful',

    width: 900,

    getEmailField: function (cfg) {
        if (!this._emailField) {
            this._emailField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Email',
                name: 'email',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._emailField;
    },

    getWorkingTimeField: function (cfg) {
        if (!this._workingTimeField) {
            this._workingTimeField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Carga horária',
                name: 'working_time',
                width: 200,
                allowBlank: false,
            });
        }

        return this._workingTimeField;
    },

    getPreviousInstitutionField: function (cfg) {
        if (!this._previousInstitutionTimeField) {
            this._previousInstitutionTimeField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome do órgão de origem',
                name: 'previous_public_institution',
                anchor: '99%',
            });
        }

        return this._previousInstitutionTimeField;
    },

    getOptionTermField: function (cfg) {
        if (!this._optionTermField) {
            this._optionTermField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Termo de opção',
                editable: false,
                hiddenName: 'option_term',
                anchor: '99%',
                choiceId: 'requestform.MEALALLOWANCE_OPTION_TERM',
                allowBlank: false
            });
        }

        return this._optionTermField;
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
                        value: 'Requerimento Concessão de Auxílio Alimentação',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getEmailField(cfg),
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 0.40,
                                labelWidth: 100,
                                items: this.getWorkingTimeField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 0.60,
                                items: this.getContactNumberField(cfg, { width: '50%' })
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        layout: 'form',
                        labelWidth: 160,
                        items: this.getPreviousInstitutionField(cfg)
                    },
                    {
                        xtype: 'panel',
                        layout: 'form',
                        labelWidth: 100,
                        items: this.getOptionTermField(cfg)
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
    title: 'Requerimento Concessão de Auxílio Alimentação',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.mealallowance.Window',
    specialType: 'mealallowance',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
