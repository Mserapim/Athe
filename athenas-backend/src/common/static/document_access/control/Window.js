Ext._define('common.document_access.control.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.document_access.control.Restful',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    name: "control_type",
                    fieldLabel: "Nível de acesso",
                    xtype: "rest-autocompletefield",
                    allowBlank: false,
                    rest: "common.document_access.controltype.Restful"
                },
                {
                    name: "document_type",
                    fieldLabel: "Tipo de Documento",
                    xtype: "rest-autocompletefield",
                    allowBlank: false,
                    rest: "common.document_access.documenttype.Restful"
                },
                {
                    name: "document_number",
                    fieldLabel: "Nº do Documento",
                    xtype: "textfield",
                    allowBlank: false,
                    maxLength: 100
                },
                {
                    name: "source",
                    fieldLabel: "Origem",
                    xtype: "rest-autocompletefield",
                    allowBlank: false,
                    rest: "rh.generalorgan.Restful"
                },
                {
                    name: "subject",
                    fieldLabel: "Assunto",
                    xtype: "textfield",
                    allowBlank: false,
                    maxLength: 200
                },
                {
                    name: "production_date",
                    fieldLabel: "Data de produção",
                    xtype: "tk-datetimefield",
                    allowBlank: false
                },
            ]
            });

        return this._formPanel;
    }
});

