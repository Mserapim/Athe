Ext._define('rh.gfp.familysalary.FamilySalaryWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.familysalary.FamilySalaryRestful',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    maxLength: 50,
                    allowBlank: false,
                    fieldLabel: "Descrição",
                    name: "description",
                    xtype: "textfield",
                    width: 200
                },
                {
                    allowBlank: false, 
                    fieldLabel: "Início Vigência", 
                    name: "start_date", 
                    xtype: "datefield"
                },
                {
                    allowBlank: false, 
                    fieldLabel: "Fim Vigência", 
                    name: "end_date", 
                    xtype: "datefield"
                }, 
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: "Publicação",
                    allowBlank: true,
                    rest: "rh.publicacao.Restful",
                    name: "publication",
                    width: 445
                }
                ]
            });

        return this._formPanel;
    }
});

