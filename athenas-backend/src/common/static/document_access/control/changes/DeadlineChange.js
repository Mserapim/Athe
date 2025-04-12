Ext._define('common.document_access.control.changes.DeadlineChange', {
    extend: 'common.document_access.control.changes.BaseJustification',

    getActualFinalTermField: function() {
        if (!this._actualFinalTermField) {
            this._actualFinalTermField = Ext._create('core.fields.DisplayDatetimeField', {
                fieldLabel: 'Atual',
                name: 'actual_final_term'
            });
        }

        return this._actualFinalTermField;
    },

    getNewFinalTermField: function() {
        if (!this._newFinalTermField) {
            this._newFinalTermField = Ext._create('toolkit.fields.DateTimeField', {
                fieldLabel: 'Novo',
                name: 'final_term',
                allowBlank: false,
            });

            this._newFinalTermField.getDateField().setMinValue(new Date());
        }

        return this._newFinalTermField;
    },

    getColumnsDeadlineChange: function() {
        return {
            xtype: 'fieldset',
            title: 'Termo final',
            layout: 'column',
            align: 'center',
            defaults: {
                columnWidth: '0.5',
                layout: 'form',
                labelWidth: 40,
            },
            items: [
                {
                    items: this.getActualFinalTermField()
                },
                {
                    items: this.getNewFinalTermField()
                },
            ]
        };
    },

    getFormFields: function() {
        var formFields = common.document_access.control.changes.DeadlineChange.superclass.getFormFields.call(this, {});
        formFields.splice(0, 0, this.getColumnsDeadlineChange());

        return formFields;
    },

    validateFields: function () {
        var exception = {title: 'Erro de validação'};

        if (!this.getNewFinalTermField().getValue()) {
            exception.message = 'Por favor, preencha corretamente o Termo Final (Novo).';
            throw exception;
        }

        common.document_access.control.changes.DeadlineChange.superclass.validateFields.call(this, {});
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            action: 'deadline_change',
        });
        Ext.applyIf(cfg, {});

        common.document_access.control.changes.DeadlineChange.superclass.constructor.call(this, cfg);
        this._final_terms = this.selections.map(function(row) { return row.get('final_term');});
        this.getFormPanel().getForm().findField('actual_final_term').setValue(this._final_terms[0]);
    }
});
