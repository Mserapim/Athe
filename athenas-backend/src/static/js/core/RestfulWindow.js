/**
 *
 **/
Ext._define('core.RestfulWindow', {
    extend: 'Ext.Window',

    mixins: {'1': 'core.RestfulPanel'},

    actionTitles: {
        create: 'Novo',
        update: 'Editar',
        remove: 'Remover',
        read: 'Carregar'
    },

    getActionTitle: function(action) {
        var title = this.actionTitles[action];

        return core.nullValue(title, 'Undefined');
    },

    _prepareSuccessCallback: function(callback, closeSuccess) {
        var wnd = this;

        callback = core.nullValue(callback, {});

        var success = core.nullValue(callback.success, {});
        var failure = core.nullValue(callback.failure, {});

        callback = core.nullValue(callback, {});

        function restoreCallbacks() {
            callback.success = success;
            callback.failure = failure;
        }

        if(this.saveAndContinue === undefined || this.saveAndContinue === false) {
            callback.success = {
                fn: function(args) {
                    core.invokeCallback(
                        (success || {fn: Ext.emptyFn}),
                        args
                    );

                    if(closeSuccess)
                        wnd.destroy();
                    else
                        wnd.resetForm();

                    restoreCallbacks();
                }
            };
        }
        else {
            callback.success = {
                fn: function(args) {
                    core.invokeCallback(
                        (success || {fn: Ext.emptyFn}),
                        args
                    );

                    if(closeSuccess)
                        core.invokeCallback(
                            (wnd.saveAndContinue || {fn: Ext.emptyFn}),
                            args
                        );
                    else {
                        wnd.action = 'create';
                        wnd.oId = null;
                        wnd.resetForm();
                    }

                    restoreCallbacks();
                }
            };
        }

        callback.failure = {
            scope: this,
            fn: function(args) {
                core.invokeCallback(
                    (failure || {fn: Ext.emptyFn}),
                    args
                );

                if(args.errors) {
                    var me = this;

                    args.errors.forEach(
                        function(error) {
                            console.debug(error.field);
                            var field = me.getFormPanel().getForm().findField(error.field);
                            console.debug(field);
                            if(field != undefined && field.xtype == 'rest-autocompletefield')
                                field = field.getComboField();

                            if(field) {
                                var tpl = new Ext.XTemplate(
                                    '<ul>',
                                    '<tpl for="values">',
                                    '<li>{.}</li>',
                                    '</tpl>',
                                    '</ul>'
                                );

                                field.markInvalid(tpl.apply(error));
                            }
                        }
                    );
                }

                restoreCallbacks();
            }
        };

        return callback;
    },

    readData: function() {
        var rest = this.factoryRestful(this.resource? {resource: this.resource}: {});

        rest.get(
            this.oId,
            {
                success: {
                    scope: this,
                    fn: function(instance) {
                        this.getFormPanel().getForm().setValues(
                            instance
                        );

                        if(this.readDataCallback) this.readDataCallback.call(this, instance);
                    }
                },
                failure: {
                    scope: this,
                    fn: function(request) {
                        var message = '';

                        if(typeof(request) == 'string')
                            message = request;
                        else if(request.failureType == 'connect')
                            message = 'O recurso esta indisponível no momento. Cheque sua conectividade.';
                        else if(request.failureType == 'server')
                            message = 'O sistema não conseguiu responder sua requisição, tente novamente mais tarde.';

                        Ext.Msg.show({
                            title: 'Buscando informações',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: message,
                            scope: this,
                            fn: function() {
                                this.destroy();
                            }
                        });
                    }
                }
            },
            {
                el: this.getEl()
            }
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg.values, cfg.params);

        Ext.applyIf(
            cfg,
            {
                modal: true,
                title: this.getActionTitle(cfg.action),
                values: {},
                params: {}
            }
        );

        Ext.apply(
            cfg,
            {
                resizable: false,
                items: this.getFormPanel(cfg),
                buttons: this.getButtons(cfg)
            }
        );

        // this.callParent([cfg]);
        core.RestfulWindow.superclass.constructor.call(this, cfg);
        this._postConstructor(cfg);
    }
});
