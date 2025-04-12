Ext._define('planning.hiring.hired.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.hired.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "person",
                        fieldLabel: "Nome",
                        width: 358,
                        allowBlank: false,
                        xtype: "rest-autocompletefield",
                        rest: "rh.person.Restful",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Data de Início",
                        name: "start_date",
                        xtype: "datefield",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Data de Encerramento",
                        name: "end_date",
                        xtype: "datefield",
                    }  
                ]
            });

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        planning.hiring.hired.Window.superclass.constructor.call(this, cfg);
    },
});
