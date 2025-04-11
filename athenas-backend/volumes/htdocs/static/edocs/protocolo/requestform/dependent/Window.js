Ext._define('edocs.protocolo.requestform.dependent.Window', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.protocolo.requestform.dependent.Restful',

    width: 900,

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 135,
                items: [
                    {
                        xtype: "textfield",
                        name: "name",
                        fieldLabel: "Nome do dependente",
                        allowBlank: false,
                        maxLength: 100,
                        anchor: '99%'
                    },
                    {
                        xtype: 'choicefield',
                        hiddenName: 'degree_of_kinship',
                        fieldLabel: 'Grau de parentesco',
                        editable: false,
                        anchor: '99%',
                        choiceId: 'rh.DEPENDENT_TYPE',
                        allowBlank: false
                    },
                    {
                        xtype: "cpffield",
                        name: "cpf",
                        fieldLabel: "CPF do dependente",
                        allowBlank: false,
                        width: '25%',
                    },
                    {
                        xtype: 'checkbox',
                        boxLabel: 'Declaro, para os fins de direito, que essa pessoa não é declarada como dependente de outro contribuinte, para efeitos de tributação de Imposto de Renda.',
                        name: 'unimpeded_as_taxpayer_dependent',
                        fieldLabel: '&nbsp;',
                        labelSeparator: '&nbsp;',
                        allowBlank: true,
                    }
                ]
            });
        }

        return this._formPanel;
    }
});
