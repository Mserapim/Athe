Ext._define('planning.hiring.minutesolicitationmanager.SolicitationRebalancingWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitationmanager.MinuteSolicitationRebalancingRestful',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 470,
                        height: 320,
                        allowBlank: true,
                        fieldLabel: 'Descrição',
                        name: "description",
                        xtype: "ckeditor",
                    },
                    {
                        width: 470,
                        allowBlank: true,
                        fieldLabel: "Marca",
                        name: "brand",
                        xtype: "textfield"
                    },
                    {
                        width: 470,
                        allowBlank: true,
                        fieldLabel: "Valor Unitário",
                        name: "unit_value",
                        xtype: "currencyfield"
                    },
                ]
            });

        return this._formPanel;
    },

    save: function() {
        var form = this.getFormPanel().getForm();
        form.waitMsgTarget = this.getEl();
        form.submit({
            url: toolkit.util.Normalize.controller_action(
                'PHMRebalancedSolicitationItem',
                'do_post'
            ),
            params: this.params,
            scope: this,
            waitMsg: 'Salvando informações...',
            success: function(form, action) {
                var success = this.success;
                success && success.callback && success.callback.call(success.scope ? success.scope : window);
                this.destroy();
                this.params.itemgrid.getStore().reload();
            },
            failure: function(form, action) {
                
                var message = '';
                var failure = this.failure;

                failure && failure.callback && failure.callback.call(failure.scope ? failure.scope : window);

                if(action.failureType == 'connect')
                    message = action.response.responseText.split('\n')[1];
                else
                    message = action.result.message;

                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
                this.destroy();
            }
        });
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Pedido',
            width: 610,
            height: 620
        });

        planning.hiring.minutesolicitationmanager.SolicitationRebalancingWindow.superclass.constructor.call(this, cfg);
    },
});
