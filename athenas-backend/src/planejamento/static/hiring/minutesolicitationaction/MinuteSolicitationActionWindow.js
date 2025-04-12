
Ext._define('planning.hiring.minutesolicitationaction.MinuteSolicitationActionWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitationaction.MinuteSolicitationActionRestful',

    width: 640,

    ACTIONS: {},

    getActionsList: function(params) {
        Ext.Ajax.request({
            url: core.callAction('PHMMinuteSolicitationAction', 'get_actions_list'),
            scope: this,
            success: function(response, options) {
                var obj = Ext.decode(response.responseText);
                if (obj.success) {
                    this.ACTIONS = obj.actions_list;
                }
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
                this.setTitle("Ação - " + this.ACTIONS[params.action]);
            },
        });
    },

    save: function() {
        var form = this.getFormPanel().getForm();
        form.waitMsgTarget = this.getEl();
        form.submit({
            url: toolkit.util.Normalize.controller_action(
                'PHMMinuteSolicitationAction',
                'do_post'
            ),
            params: this.params,
            scope: this,
            waitMsg: 'Salvando informações...',
            success: function(form, action) {
                var success = this.success;
                success && success.callback && success.callback.call(success.scope ? success.scope : window);
                this.destroy();
            },
            failure: function(form, action) {
                var message = '';
                var failure = this.failure;

                var responseText = action.response.responseText.split("\n");

                failure && failure.callback && failure.callback.call(failure.scope ? failure.scope : window);

                if(action.failureType == 'connect')
                    message = 'Recurso indisponivel no momento, tente novamente mais tarde.';
                else
                    message = action.result.message;

                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: responseText[1]
                });
                this.destroy();
            }
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
                        allowBlank: true,
                        fieldLabel: "Observação",
                        name: "observation",
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

        planning.hiring.minutesolicitationaction.MinuteSolicitationActionWindow.superclass.constructor.call(this, cfg);
    },
});
