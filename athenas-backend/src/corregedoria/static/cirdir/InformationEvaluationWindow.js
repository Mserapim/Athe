Ext._define('corregedoria.cirdir.InformationEvaluationWindow', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.InformationEvaluationRestful',

    width: 750,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                    width: 615
                },
                items: [
                    {
                        allowBlank: false,
                        name: "observation",
                        xtype: "ckeditor",
                        height: 600
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
        });
        
        corregedoria.cirdir.InformationEvaluationWindow.superclass.constructor.call(this, cfg);

    },

});
