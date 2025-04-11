Ext._define('planning.hiring.corporatestructure.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.corporatestructure.Restful',

    width: 500,

    officeField: function () {
        if (!this._officeField)
            this._officeField = Ext._create('standard.fields.ChoiceField', {
                width: 350,
                allowBlank: false,
                fieldLabel: "Cargo",
                name: "CARGO_EMPRESA",
                choiceId: "contrato.CARGO_EMPRESA",
                hiddenName: "office",
            });
        return this._officeField;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "person",
                        fieldLabel: "Pessoa",
                        width: 358,
                        allowBlank: false,
                        xtype: "rest-autocompletefield",
                        rest: "rh.person.Restful",
                    },
                    this.officeField(),
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
                        fieldLabel: "Data de Desligamento",
                        name: "end_date",
                        xtype: "datefield",
                    }  
                ]
            });

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        planning.hiring.corporatestructure.Window.superclass.constructor.call(this, cfg);
    },
});
