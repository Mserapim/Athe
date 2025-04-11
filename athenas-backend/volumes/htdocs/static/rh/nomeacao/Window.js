Ext._define('rh.nomeacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.nomeacao.Restful',

    width: 650,

    getProvimentoField: function(cfg) {
        var employee_pk = this.params ? this.params.employee : null;

        if(!this._provimentoField) {
            this._provimentoField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: 'Provimento',
                width: 500,
                allowBlank: true,
                rest: "rh.movimentacao.possession.AllPossessionsRestful",
                name: "provimento",
                disabled: false,
                preFilter: [
                ],
                gridConfig: {
                    columnAction: false,
                    allowCreate: false,
                    allowUpdate: false,
                    allowRemove: false,
                    configOrderToolBar: ['search', '->'],
                }
            });
        }

        return this._provimentoField;
    },

    getFormPanel: function(cfg) {
    
        var employee_pk = this.params ? this.params.employee : null;
        
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "textfield", 
                        fieldLabel: "CPF", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "cpf",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Tipo Nomeação", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "tipo_nomeacao",
                    },
                    {
                        xtype: "datefield", 
                        fieldLabel: "Data de Convocação", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "data_convocacao",
                    },
                    {
                        xtype: "datefield", 
                        fieldLabel: "Data de Resposta", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "data_resposta",
                    },
                    this.getProvimentoField(cfg),
                ]
            });

            if (employee_pk != null){
                this._provimentoField.setPreFilter([
                    {property: 'servidor__pk', value: employee_pk, stage: 1100,},
                ])
            }  

        return this._formPanel;
    }
});
