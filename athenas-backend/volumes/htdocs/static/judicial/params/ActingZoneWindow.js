Ext._define('judicial.params.ActingZoneWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.params.ActingZoneRestful',

    width: 550,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 412,
                        maxLength: 60,
                        allowBlank: false,
                        fieldLabel: "Título",
                        name: "title",
                        xtype: "textfield"
                    },
                    {
                        xtype: "checkbox",
                        boxLabel: "Ativo",
                        name: "enabled",
                        allowBlank: true,
                        checked: true,
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        judicial.params.ActingZoneWindow.superclass.constructor.call(this, cfg);
    }
});

