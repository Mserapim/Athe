Ext._define('corregedoria.cirdir.irscode.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.irscode.Restful',

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
        
        corregedoria.cirdir.irscode.Window.superclass.constructor.call(this, cfg);
    },

});
