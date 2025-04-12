/**
 *
 **/
Ext._define('core.RestfulPanel', {
    extend: 'Ext.Panel',

    rest: undefined,

    width: 350,

    focusField: undefined,

    factoryRestful: function(cfg) {

        if(!this._restful)
        {
            cfg = cfg || {};
            this._restful = Ext._create(this.rest, cfg);
        }

        return this._restful;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false
            });

        return this._formPanel;
    },

    getParams: function() {
        return core.nullValue(this.params, {});
    },

    resetForm: function() {
        var form = this.getFormPanel().getForm();
        form.reset();
        setTimeout(function() {
            try {
                form.items.itemAt(0).focus();
            } catch (e) {
                console.warn('Erro de programação. Não é possivel definir foco no componente especificado.');
            }
        }, 500);
    },

    _prepareSuccessCallback: function(callback) {
        var wnd = this;
        var success = core.nullValue(callback.success, {});
        var failure = core.nullValue(callback.failure, {});

        callback.success = {
            fn: function(args) {
                core.invokeCallback(
                    success,
                    args
                );

                wnd.resetForm();
            }
        };

        callback.failure = {
            scope: this,
            fn: function(data) {
                core.invokeCallback(
                    failure,
                    args
                );

                console.debug(data);
            }
        };

        return callback;
    },

    extractDataForm: function() {
        return {};
    },

    localPersistence: function(values, oId, rest, callback) {
        var record;
        var store = (this.ownerGrid ? this.ownerGrid.getStore(): false);

        Ext.applyIf(values, this.extractDataForm());

        if(!store)
            throw 'Erro de implementação, não consegui definir o store para persistencia local.';

        if(oId) {
            record = store.getAt(store.find('pk', oId));

            for(var key in values)
                record.set(key, values[key]);

            if(!recoed.get('operation')) record.set('operation', 'U');
        }
        else {
            var MyRecord = Ext.data.Record.create(
                rest.getFields().concat([
                    {name: 'operation', type: 'auto'}
                ])
            );

            values.pk = (new Date().getTime());
            record = new MyRecord(values);
            record.modified = true;
            record.set('operation', 'C');
            store.add(record);
        }

        core.invokeCallback(callback.success);
    },

    preSave: function() {   
        return true;
    },

    save: function(close) {
        if (!this.preSave()) {
            return;
        }
        var form = this.getFormPanel().getForm();
        var rest = this.factoryRestful();

        close = core.nullValue(close, true);

        var cfg = {
            externalCallback: this._prepareSuccessCallback(this.callback, close),
            params: Ext.applyIf(
                form.getValues(),
                this.getParams()
            )
        };

        Ext.each(
            form.getEl().query('input[type=checkbox]'),
            function(el) {
                if(!cfg.params[el.name])
                    cfg.params[el.name] = 'off';
            }
        );

        if(this.ownerGrid && this.ownerGrid.driver === 'local')
            this.localPersistence(cfg.params, this.oId, rest, cfg.externalCallback);
        else {
            if(this.action == 'create')
                rest.create(
                    cfg,
                    {
                        el: this.getEl(),
                        waitMessage: 'Persistindo os dados.'
                    }
                );
            else if(this.action == 'update')
                rest.update(
                    this.oId,
                    cfg,
                    {
                        el: this.getEl(),
                        waitMessage: 'Persistindo os dados.'
                    }
                );
            else
                Ext.Msg.show({
                    title: 'Erro de implementação',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Ocorreu um erro de implementação do software, favor contacte a equipe de desenvolvimento.'
                });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [];
            if(cfg.action == 'create' && !cfg.disableSaveAndNew)
                this._buttons.push({
                    text: 'Salvar e novo',
                    scope: this,
                    handler: function() { this.save(false); }
                });
            if(!cfg.disableSave)
                this._buttons.push({
                    text: 'Salvar',
                    scope: this,
                    handler: function() { this.save(true); }
                });
            this._buttons.push(
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            );

        }

        return this._buttons;
    },

    readData: function() {
        var rest = this.factoryRestful();

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

    _postConstructor: function() {
        this.on({
            scope: this,
            render: function() {
                var scope = this;

                setTimeout(
                    function() {
                        var field;

                        if(scope.focusField !== undefined)
                            field = scope.getFormPanel().getForm().findField(scope.focusField);
                        else
                            scope.getFormPanel().getForm().items.itemAt(0);

                        try {
                            if(field !== undefined) field.focus(true);
                        }
                        catch(e) {}
                    },
                    500
                );
            }
        });

        if(this.values == 'remote' && this.oId) {
            // var oId = this.oId;

            this.on({
                scope: this,
                render: function() {
                    // this.oId = oId;
                    this.readData();
                }
            });
        }
        else this.getFormPanel().getForm().setValues(this.values);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                ownerGrid: false,
                values: {},
                params: {}
            }
        );

        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg)
            }
        );

        core.RestfulPanel.superclass.constructor.call(this, cfg);
        this._postConstructor();
    }
});
