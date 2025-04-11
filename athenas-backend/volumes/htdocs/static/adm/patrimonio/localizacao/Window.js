/**
 *
 **/
Ext._define('adm.patrimonio.localizacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.localizacao.Restful',

    width: 450,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                defaults: {
                    width: this.width - 137
                },
                items: [
                    {
                        fieldLabel: 'Título',
                        xtype: 'textfield',
                        name: 'titulo'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Relacionada a",
                        allowBlank: true,
                        rest: "rh.workplace.Restful",
                        name: "lotacao_relacionada"
                    },
                    {
                        fieldLabel: 'Endereço',
                        xtype: 'textarea',
                        name: 'endereco',
                        height: 125
                    },
                    {
                        boxLabel: 'Apto a receber itens patrimoniais.',
                        xtype: 'checkbox',
                        name: 'ativo'
                    },
                    {
                        fieldLabel: 'Caminho',
                        xtype: 'textarea',
                        name: 'path',
                        readOnly: true,
                        submitValue: false,
                        height: 45
                    }
                ]
            });

        return this._formPanel;
    },
});
