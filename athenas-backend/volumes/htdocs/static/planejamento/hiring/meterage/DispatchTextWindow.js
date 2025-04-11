
Ext._define('planning.hiring.meterage.DispatchTextWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.meterage.Restful',

    setMessage: function(message) {
        console.log(this.getFormPanel().getForm().findField('dispatch').setValue(message));
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                layout: 'fit',
                items: [
                    {
                        width: 1180,
                        height: 680,
                        allowBlank: true,
                        name: "dispatch",
                        xtype: "ckeditor",
                    },
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [

                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Solicitação de Pagamento',
            width: 1200,
            height: 700,
        });

        Ext.apply(cfg, {
            items: this.getFormPanel(),
        });

        planning.hiring.meterage.DispatchTextWindow.superclass.constructor.call(this, cfg);
    },
});
