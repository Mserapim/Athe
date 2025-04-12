
Ext._define('planning.hiring.agreementaction.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.agreementaction.Restful',

    width: 640,

    ACTIONS: {},

    getActionsList: function(params) {
        Ext.Ajax.request({
            url: core.callAction('PHAAgreementAction', 'get_actions_list'),
            scope: this,
            success: function(response, options) {
                var obj = Ext.decode(response.responseText);

                if (obj.success)
                    this.ACTIONS = obj.actions_list;
            },
            failure: function(response, options) {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: response.status
                });
            },
            callback: function(options, success, response) {
                this.setTitle("Ação - " + this.ACTIONS[params.tipo]);
            },
        });
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 500,
                        allowBlank: false,
                        fieldLabel: "Observação",
                        name: "observacao",
                        xtype: "ckeditor",
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        if(cfg.params)
            this.getActionsList(cfg.params);

        planning.hiring.agreementaction.Window.superclass.constructor.call(this, cfg);
    },
});
