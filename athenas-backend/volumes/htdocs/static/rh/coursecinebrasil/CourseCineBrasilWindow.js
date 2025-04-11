Ext._define('rh.coursecinebrasil.CourseCineBrasilWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.coursecinebrasil.CourseCineBrasilRestful',

    width: 440,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    maxLength: 200, 
                    allowBlank: false, 
                    fieldLabel: "Código", 
                    name: "code", 
                    xtype: "textfield",
                    width: 300
                },
                {
                    maxLength: 200, 
                    allowBlank: false, 
                    fieldLabel: "Rótulo", 
                    name: "label", 
                    xtype: "textfield",
                    width: 300
                }
                ]
            });

        return this._formPanel;
    }
});
