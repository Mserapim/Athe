Ext._define('rh.teletrabalho.gestor_relatorio_semestral.gestor.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.teletrabalho.gestor_relatorio_semestral.gestor.Restful',

    width: 550,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Pessoa Física *',
                        name: 'pessoa_fisica',
                        displayField: 'unicode',
                        allowBlank: false,
                        rest: 'rh.person.naturalperson.Restful'
                    },
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Matrícula *',
                        name: 'matricula'
                    },
                    {
                        xtype: 'datefield',
                        fieldLabel: 'Data de referência de férias',
                        name: 'data_referencia_ferias',
                        format: 'd/m/Y'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Chefe Imediato',
                        name: 'chefe_imediato',
                        displayField: 'unicode',
                        allowBlank: true,
                        rest: 'rh.employee.Restful'
                    }
                ],

            });

        return this._formPanel;
    },
});