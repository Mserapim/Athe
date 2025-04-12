Ext._define('common.document_access.control.changes.Reclassify', {
    extend: 'common.document_access.control.changes.BaseJustification',

    getControlTypeField: function (cfg) {
        if (!this._controlTypeField) {
            this._controlTypeField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Nível de acesso',
                allowBlank: false,
                displayField: 'title',
                valueField: 'pk',
                hiddenName: 'control_type',
                rest: 'common.document_access.controltype.Restful',
                anchor: '99%',
                listeners: {
                    scope: this,
                    select: function (combo, record, index, is_custom_event) {
                        if (is_custom_event) {
                            this.getLegalPrerogativeField().reset();
                            this.getLegalPrerogativeField().setPreFilter([
                                {property: 'control_type', value: record.data.pk, stage: 1001},
                            ]);
                            this.getLegalPrerogativeField().getStore().load({});
                        }
                    },
                }
            });
        }

        return this._controlTypeField;
    },

    getLegalPrerogativeField: function (cfg) {
        if (!this._legalPrerogativeField) {
            this._legalPrerogativeField = Ext._create('core.fields.ComboField', {
                hiddenName: 'legal_prerogative',
                fieldLabel: 'Hipótese legal',
                displayField: 'title',
                valueField: 'pk',
                rest: 'common.document_access.legalprerogative.Restful',
                allowBlank: true,
                anchor: '99%',
                preFilter: [
                    {property: 'control_type', value: null, stage: 1001},
                ],
                style: {marginBottom: '15px'},
            });
        }

        return this._legalPrerogativeField;
    },

    getFormFields: function() {
        var formFields = [
            this.getControlTypeField(),
            this.getLegalPrerogativeField()
        ].concat(
            common.document_access.control.changes.Reclassify.superclass.getFormFields.call(this, {})
        );

        return formFields;
    },

    validateFields: function () {
        var exception = {title: 'Erro de validação'};

        if (!this.getControlTypeField().getValue()) {
            exception.message = 'Por favor, selecione corretamente o Nível de Acesso.';
            throw exception;
        }

        if (!this.getLegalPrerogativeField().getValue()) {
            exception.message = 'Por favor, selecione corretamente o Hipótese Legal.';
            throw exception;
        }

        common.document_access.control.changes.Reclassify.superclass.validateFields.call(this, {});
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            action: 'reclassify',
        });
        Ext.applyIf(cfg, {});

        common.document_access.control.changes.Reclassify.superclass.constructor.call(this, cfg);
    }
});
