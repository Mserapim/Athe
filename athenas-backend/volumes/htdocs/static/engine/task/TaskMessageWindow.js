/**
 *
 **/
Ext._define('engine.TaskMessageWindow', {
    extend: 'core.RestfulWindow',

    rest: 'engine.TaskMessageRestful',

    width: 575,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                // items: [
                //     this.getTabPanel(cfg)
                // ]
                items: [
                    {
                        fieldLabel: 'SID',
                        xype: 'displayfield',
                        name: 'session_unicode',
                        maxLenght: 100,
                        allowBlank: false,
                        width: 300
                    },{
                        fieldLabel: 'Message',
                        xype: 'textfield',
                        name: 'message',
                        maxLenght: 250,
                        allowBlank: false,
                        width: 300
                    },
                ]                
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
        });

        engine.TaskMessageWindow.superclass.constructor.call(this, cfg);
    }
});

