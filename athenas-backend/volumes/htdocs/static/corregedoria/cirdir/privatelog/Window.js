Ext._define('corregedoria.cirdir.privatelog.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.privatelog.Restful',

    width: 800,


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
                        labelWidth: 70,
                        items: [
                            {
                                xtype: 'htmleditor',
                                fieldLabel: 'Log Privado',
                                name: "information",
                                height: 200,
                                width: 695,
                                enableLinks: false,
                                enableLists: false,
                                enableFont: false,
                                enableColors: false,
                                enableSourceEdit: false,
                                enableFontSize: false,
                                enableAlignments: false,
                                style: {fontSize: '11px'},
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
            disableSaveAndNew: true,
        });
        corregedoria.cirdir.privatelog.Window.superclass.constructor.call(this, cfg);
    },

});
