
Ext._define('judicial.params.GlosaryWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.params.GlosaryRestful',

    width: 750,

    getClassificationField: function() {
        if(!this._classificationField)
            this._classificationField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Classificação",
                allowBlank: false,
                rest: "judicial.taxonomy.LegalClassificationRestful",
                name: "legal_classification",
                disabled: true
            });

        return this._classificationField;
    },

    classification: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._classification = value;

            !prevent && this.observeClassification();
        }

        return this._classification;
    },

    observeClassification: function() {
        var value = this.classification();

        if(value) {
            this.getClassificationField().enable();

            switch(value) {
                case 1:
                    this.getClassificationField().rest = 'judicial.taxonomy.LegalMovimentRestful';
                    break;
                case 2:
                    this.getClassificationField().rest = 'judicial.taxonomy.LegalProcedureRestful';
                    break;
                default:
                    this.getClassificationField().rest = 'judicial.taxonomy.LegalClassificationRestful';
                    break;
            }
        }
        else {
            this.getClassificationField().disable();
            this.getClassificationField().rest = 'judicial.taxonomy.LegalClassificationRestful';
        }
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Tipo',
                        name: 'meaning_type_display',
                        value: 'meaning_type_display'
                    },
                    {
                        xtype: 'checkbox',
                        name: 'active',
                        boxLabel: 'Ativo',
                        allowBlank: true
                    },
                    {
                        xtype: "choicefield",
                        fieldLabel: "Classificação como",
                        hiddenName: "classification_type",
                        allowBlank: true,
                        choiceId: 'judicial.GLOSARY_CLASSIFICATION_TYPE',
                        listeners: {
                            scope: this,
                            select: function(combo, record) {
                                this.classification(
                                    record.get('value')
                                );
                                this.getClassificationField().setValue(null);
                            }
                        }
                    },
                    this.getClassificationField(),
                    {
                        xtype: 'rest-relatedfield',
                        hideLabel: true,
                        name: 'allowed_for',
                        relatedname: 'permissions',
                        width: 729,
                        height: 215,
                        rest: this.rest,
                        padding: '5 0 0 0',
                        sourceRest: 'judicial.params.CharacterRestful',
                        oId: cfg.oId
                    }
                ],
                listeners: {
                    scope: this,
                    render: function() {
                        this.observeClassification();
                    }
                }
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().findField('allowed_for').objectId(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        judicial.params.GlosaryWindow.superclass.constructor.call(this, cfg);
    }
});
