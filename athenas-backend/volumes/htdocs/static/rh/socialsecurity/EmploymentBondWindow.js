Ext._define('rh.socialsecurity.EmploymentBondWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.socialsecurity.EmploymentBondRestful',
    width: 400,

    pensionSystemField: function(cfg) {
        if (!this._pensionSystemField)
            this._pensionSystemField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Regime',
                allowBlank: false,
                hiddenName: 'pension_system',
                width: 266,
                choiceId: 'rh.REGIME_PREVIDENCIARIO'
            });

        return this._pensionSystemField;
    },

    purposeField: function(cfg) {
        if (!this._purposeField)
            this._purposeField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Para Fins',
                allowBlank: false,
                hiddenName: 'purpose',
                width: 266,
                choiceId: 'rh.PURPOSES'
            });

        return this._purposeField;
    },

    beginDateField: function(cfg) {
        if (!this._beginDateField)
            this._beginDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Início',
                allowBlank: false,
                name: 'begin_date',
                width: 266,
                choiceId: 'rh.PURPOSES'

            });

        return this._beginDateField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    xtype: 'displayfield',
                    fieldLabel: 'Contribuinte',
                    name: 'contributor_unicode',
                    width: 266
                },
                {
                    maxLength: 512,
                    allowBlank: false,
                    fieldLabel: 'Empregador',
                    name: 'employer',
                    xtype: 'textfield',
                    width: 266
                },
                this.pensionSystemField(),
                this.beginDateField(),
                {
                    fieldLabel: 'Término',
                    name: 'end_date',
                    xtype: 'datefield',
                    width: 266
                },
                {
                    xtype: 'numberfield',
                    fieldLabel: 'Tempo Bruto',
                    allowBlank: true,
                    allowDecimals: false,
                    name: 'raw_days',
                    width: 266
                },
                {
                    xtype: 'numberfield',
                    fieldLabel: 'Deduções',
                    allowBlank: true,
                    allowDecimals: false,
                    name: 'deduction',
                    width: 266
                },
                {
                    xtype: 'numberfield',
                    fieldLabel: 'Tempo líquido',
                    allowBlank: true,
                    allowDecimals: false,
                    name: 'liquid_days',
                    width: 266
                },
                {
                    maxLength: 240,
                    fieldLabel: 'Cargo/Função',
                    name: 'function_name',
                    xtype: 'textfield',
                    width: 266
                },
                this.purposeField(),
                {
                    xtype: 'checkbox',
                    fieldLabel: '&nbsp;',
                    labelSeparator: '&nbsp;',
                    boxLabel: 'Tempo dobrado?',
                    allowBlank: true,
                    name: 'contribution_double'
                },
                {
                    xtype: 'checkbox',
                    fieldLabel: '&nbsp;',
                    labelSeparator: '&nbsp;',
                    boxLabel: 'Serviço público?',
                    allowBlank: true,
                    name: 'public_employee'
                },
            ]
            });

        return this._formPanel;
    }
});
