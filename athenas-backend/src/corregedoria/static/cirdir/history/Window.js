Ext._define('corregedoria.cirdir.history.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.history.Restful',

    width: 600,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  {
                      xtype:'panel',
                      autoHeight:true,
                      layout: 'form',
                      labelWidth: 30,
                      items: [

                      ]
                  },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
        });
        corregedoria.cirdir.history.Window.superclass.constructor.call(this, cfg);
    },

});
