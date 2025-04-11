Ext._define('planning.hiring.rideitem.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.rideitem.Restful',

    width: 500,

    getFormPanel: function(cfg) {

        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        name: "item",
                        fieldLabel: "Descrição",
                        width: 358,
                        allowBlank: false,
                        xtype: "rest-autocompletefield",
                        rest: "planning.hiring.minuteitem.MinuteItemRestful",
                        preFilter: [
                            {property: 'minute', value: cfg.params.minute, stage: 100}
                        ]
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Quantidade",
                        name: "amount",
                        xtype: "textfield",
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        planning.hiring.rideitem.Window.superclass.constructor.call(this, cfg);
    },
});
