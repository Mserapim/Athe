Ext._define('judicial.search.person.Window', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.search.person.Restful',

    width:535,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [ ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true
        });

        judicial.search.Window.superclass.constructor.call(this, cfg);
    }
});

