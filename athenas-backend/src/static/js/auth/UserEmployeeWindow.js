/**
 *
 **/
Ext._define('auth.UserEmployeeWindow', {
    extend: 'Ext.Window',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'displayfield',
                        name: 'username',
                        fieldLabel: 'Usuário'
                    },
                    {
                        'xtype': 'rest-autocompletefield',
                        'fieldLabel': 'Servidor',
                        'name': 'employee',
                        'allowBlank': true,
                        'rest': 'rh.employee.Restful'
                    }
                ]
            });

        return this._formPanel;
    },

    changeUser: function() {
        var rest = Ext._create('rh.employee.Restful');
        var mask = new Ext.LoadMask(this.getEl(), 'Manipulando empregado...');

        params = Ext.apply(
            this.params || {},
            this.getFormPanel().getForm().getValues()
        );

        mask.show();
        rest.doRequest(
            rest.getRoute(
                'change_user',
                false,
                'PUT',
                {
                    scope: this,
                    params: params,
                    callback: function() {
                        mask.hide();
                        mask = null;
                    },
                    success: function(xhr) {
                        var data = Ext.decode(xhr.responseText);

                        if(!data.success)
                            Ext.Msg.show({
                                title: 'Manipular empregado',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: data.message
                            });
                        else {
                            core.invokeCallback(this.callback || {fn: function() {}});
                            this.close();
                        }
                    },
                    failure: function() {
                        Ext.Msg.show({
                            title: 'Manipular empregado',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    }
                }
            )
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Associar Usuário a Servidor'
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                width: 550,
                items: [
                    this.getFormPanel()
                ],
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: this.changeUser
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function() { this.close(); }
                    }
                ]
            }
        );

        // this.callParent([cfg]);
        auth.UserEmployeeWindow.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(cfg.values || {});
    }
});
