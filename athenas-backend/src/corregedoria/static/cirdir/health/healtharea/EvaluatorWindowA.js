Ext._define('corregedoria.cirdir.health.healtharea.EvaluatorWindow', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.health.healtharea.EvaluatorRestful',

    width: 600,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 40,
                items: [
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Nome',
                        name: 'name',
                        width: 500,
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
        });
        corregedoria.cirdir.health.healtharea.EvaluatorWindow.superclass.constructor.call(this, cfg);
    },

});
