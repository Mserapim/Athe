 Ext._define('rh.telefone.emergency.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.telefone.emergency.Restful',

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 80,
                items: [
                    {
                        xtype: 'fonefield',
                        fieldLabel: 'Número',
                        name: 'numero',
                        allowBlank: false,
                        width: '97%',
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo telefone',
                        hiddenName: 'tipo_telefone',
                        choiceId: 'rh.TYPE_PHONE',
                        // TODO: Passar a variável de emengency_type em substituição ao valor constante
                        value: 6,
                        anchor: '99%',
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Nome/Contato Emergência:",
                        name: "description",
                        allowBlank: false,
                        maxLength: 80,
                        anchor: '99%',
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Grau de Parentesco:",
                        name: "kinship",
                        allowBlank: true,
                        maxLength: 80,
                        anchor: '99%',
                    },
                    {
                        xtype: "checkbox",
                        fieldLabel: "Público",
                        boxLabel: "Público",
                        name: "publico",
                        hideLabel: true,
                        allowBlank: true,
                    },
                    {
                        xtype: "checkbox",
                        fieldLabel: "Principal",
                        boxLabel: "Principal",
                        name: "main",
                        hideLabel: true,
                        allowBlank: true,
                    },
                ],
            });
        }
        return this._formPanel;
    },
});
