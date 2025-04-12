Ext._define('rh.nomeacao.anexo_nomeacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.nomeacao.anexo_nomeacao.Restful',

    width: 650,

    getFormPanel: function(cfg) {
    
        var employee_pk = this.params ? this.params.employee : null;
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    
                    {
                        xtype: "textfield", 
                        fieldLabel: "Tipo Documento", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "tipo_documento_display",
                    },
                ]
            });

        return this._formPanel;
    }
});
