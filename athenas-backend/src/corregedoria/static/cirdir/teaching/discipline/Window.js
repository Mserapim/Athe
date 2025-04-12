Ext._define('corregedoria.cirdir.teaching.discipline.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.teaching.discipline.Restful',

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
                          {
                              xtype: 'textfield',
                              fieldLabel: 'Nome',
                              width: 550,
                              name: 'name',
                          },
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
        corregedoria.cirdir.teaching.discipline.Window.superclass.constructor.call(this, cfg);
    },

});
