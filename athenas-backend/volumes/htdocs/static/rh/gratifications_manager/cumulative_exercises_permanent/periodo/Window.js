 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.periodo.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gratifications_manager.cumulative_exercises_permanent.periodo.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    maxLength: 40, 
                    allowBlank: false, 
                    fieldLabel: "Ano", 
                    name: "ano", 
                    width: 100,
                    xtype: "textfield"
                },
                {
                    xtype: "combo", 
                    fieldLabel: "Mês", 
                    allowBlank: false, 
                    lazyRender: true, 
                    hiddenName: "mes", 
                    mode: "local", 
                    triggerAction: "all", 
                    store: [
                        [1, "JANEIRO"], 
                        [2, "FEVEREIRO"], 
                        [3, "MARÇO"], 
                        [4, "ABRIL"], 
                        [5, "MAIO"], 
                        [6, "JUNHO"], 
                        [7, "JULHO"], 
                        [8, "AGOSTO"], 
                        [9, "SETEMBRO"], 
                        [10, "OUTUBRO"], 
                        [11, "NOVEMBRO"], 
                        [12, "DEZEMBRO"], 
                    ], 
                    name: "mes",
                    width: 300
                },
                ]
            });

        return this._formPanel;
    }
});
