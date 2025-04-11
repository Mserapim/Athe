Ext._define('rh.highereducationinstitution.HigherEducationInstitutionWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.highereducationinstitution.HigherEducationInstitutionRestful',

    width: 440,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    maxLength: 200, 
                    allowBlank: false, 
                    fieldLabel: "Código", 
                    name: "code", 
                    xtype: "textfield",
                    width: 300
                },
                {
                    maxLength: 200, 
                    allowBlank: false, 
                    fieldLabel: "Nome", 
                    name: "name", 
                    xtype: "textfield",
                    width: 300
                },
                {
                    maxLength: 200, 
                    allowBlank: false, 
                    fieldLabel: "Sigla", 
                    name: "acronym", 
                    xtype: "textfield",
                    width: 300
                },
                {
                    width: 300,
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Município *',
                    name: 'municipality',
                    allowBlank: false,
                    rest: 'rh.localidade.Restful',
                    blankText: 'É necessário preencher o campo Município.',
                }
                ]
            });

        return this._formPanel;
    }
});
