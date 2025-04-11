/**
 *
 **/
Ext._define('edocs.processo.movprocessoWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.Restful',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        name: "codigo_processo",
                        fieldLabel: "Processo",
                        xtype: "textfield",
                        readOnly: true,
                    },
                    {
                        allowBlank: false,
                        xtype: "textfield",
                        name: "volume",
                        maxLenght: 255,
                        fieldLabel: "Volume",
                        // regex: "^[a-zA-Z_]*$",
                        regex: /^[mdclxviMDCLXVI]*$/,
                        regexText: "<b>Erro:</b></br>Favor utilizar algarismos romanos.",
                        validator: function(v) {
                            return /^[mdclxviMDCLXVI]*$/.test(v)?true:"Favor utilizar algarismos romanos";
                        }
                    },   
                    {
                        xtype: 'numberfield',
                        name: 'paginas',
                        fieldLabel: 'Página',
                        allowBlank: false,
                    },
                ]
            });

        return this._formPanel;
    }
});
