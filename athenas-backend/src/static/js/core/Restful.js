/**
 *
 **/
Ext._define('core.Restful', {

    /**
     * Tradução de verbos
     **/
    verb: {
        read: 'GET',
        read_id: 'GET',
        create: 'POST',
        update: 'PUT',
        update_id: 'PUT',
        multi_update: 'PUT',
        remove: 'DELETE',
        remove_id: 'DELETE',
        multi_remove: 'DELETE',
    },

    /**
     * Tradução de Rotas
     **/
    definedRoutes: {
        read: '{resource}/{version}/',
        read_id: '{resource}/{version}/{id}/',
        create: '{resource}/{version}/',
        update: '{resource}/{version}/',
        update_id: '{resource}/{version}/{id}/',
        multi_update: '{resource}/{version}/',
        remove: '{resource}/{version}/',
        remove_id: '{resource}/{version}/{id}/',
        multi_remove: '{resource}/{version}/',
    },

    /**
     * Fonte do Recurso
     **/
    resource: null,

    /**
     * Versão da implementação do Restful
     **/
    version: 'v1',

    /**
     *
     **/
    defaultHeaders: {
        Accept: 'text/json',
        JSIndent: '4'
    },

    disableCaching: false,

    create: function(cfg, waitCfg) {
        var mask = false;

        Ext.apply(cfg, this.getRoute('create'));

        if(waitCfg && waitCfg.el) {
            mask = new Ext.LoadMask(
                waitCfg.el,
                {
                    msg: core.nullValue(
                        waitCfg.message,
                        'Persistindo os dados...'
                    )
                }
            );
        }

        Ext.apply(
            cfg,
            {
                success: function(request) {
                    var rst = Ext.decode(request.responseText);

                    if(rst.success)
                        core.invokeCallback (
                            cfg.externalCallback.success,
                            rst.instance
                        );
                    else {
                        Ext.Msg.show({
                            title: 'Criando',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });

                        core.invokeCallback(
                            cfg.externalCallback.failure,
                            rst
                        );
                    }
                },
                failure: function(request) {
                    var message = '';

                    if(request.failureType == 'connect')
                        message = 'O recurso esta indisponível no momento. Cheque sua conectividade.';
                    else if(request.failureType == 'server')
                        message = 'O sistema não conseguiu responder sua requisição, tente novamente mais tarde.';

                    Ext.Msg.show({
                        title: 'Criando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message
                    });
                },
                callback: function(request) {
                    if(mask) {
                        mask.hide();
                        mask = null;
                    }
                }
            }
        );

        mask != false && mask.show();
        this.doRequest(cfg);
    },

    get: function(pk, callback, msgCfg) {
        var cfg = this.getRoute('read', pk);
        var mask;

        if(msgCfg && msgCfg.el) {
            mask = new Ext.LoadMask(
                msgCfg.el,
                {
                    msg: core.nullValue(msgCfg.msg, 'Carregando informações')
                }
            );
            try {
                mask.show();
            } catch(e) {
                console.log('LoadMask não pode ser mostrado.');
                mask = null;
            }
        }

        Ext.apply(cfg, {
            callback: function() {
                try {
                    mask && mask.hide();
                } catch(e) {
                    console.log('LoadMask não pode ser ocultado.');
                }
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success)
                    core.invokeCallback(callback.success, rst.instance);
                else
                    core.invokeCallback(callback.failure, rst.message);
            },
            failure: function(request) {
                core.invokeCallback(
                    callback.failure,
                    request
                );
            }
        });

        this.doRequest(cfg);
    },

    getStore: function(autoLoad, disableCaching, headers, defaultRoute) {
        defaultRoute = (defaultRoute || 'read');

        return Ext._create('Ext.data.Store', {
            proxy: Ext._create('Ext.data.HttpProxy', {
                api: {
                    read: this.getRoute(defaultRoute)
                },
                disableCaching: core.nullValue(disableCaching, this.disableCaching),
                defaultHeaders: this.defaultHeaders,
                headers: headers
            }),
            reader: Ext._create('Ext.data.JsonReader', {
                idProperty: 'pk',
                root: 'collection',
                totalProperty: 'count',
                successProperty: 'success',
                messageProperty: 'message',
                fields: this.getFields()
            }),
            // remoteSort: true,
            autoLoad: autoLoad
        });
    },

    update: function(pk, cfg, waitCfg) {
        var mask = false;

        Ext.apply(
            cfg,
            pk === false ? this.getRoute('multi_update') : this.getRoute('update', pk)
        );

        if(waitCfg && waitCfg.el) {
            mask = new Ext.LoadMask(
                waitCfg.el,
                {
                    msg: core.nullValue(
                        waitCfg.message,
                        'Persistindo os dados...'
                    )
                }
            )
        }

        Ext.apply(
            cfg,
            {
                success: function(request) {
                    var rst = Ext.decode(request.responseText);

                    if(rst.success)
                        core.invokeCallback (
                            cfg.externalCallback.success,
                            rst.instance
                        );
                    else {
                        Ext.Msg.show({
                            title: 'Atualizando',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });

                        core.invokeCallback(
                            cfg.externalCallback.failure,
                            rst
                        );
                    }
                },
                failure: function(request) {
                    var message = '';

                    if(request.failureType == 'connect')
                        message = 'O recurso esta indisponível no momento. Cheque sua conectividade.';
                    else if(request.failureType == 'server')
                        message = 'O sistema não conseguiu responder sua requisição, tente novamente mais tarde.';

                    Ext.Msg.show({
                        title: 'Atualizando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message
                    });
                },
                callback: function(request) {
                    if(mask) {
                        mask.hide();
                        delete mask;
                    }
                }
            }
        );

        mask != false && mask.show();
        this.doRequest(cfg);
    },

    remove: function(pk, cfg, waitCfg) {
        var mask = false;

        Ext.apply(
            cfg,
            pk == false ? this.getRoute('multi_remove') : this.getRoute('remove', pk)
        );

        if(waitCfg.el) {
            mask = new Ext.LoadMask(
                waitCfg.el || Ext.getBody(),
                {
                    msg: core.nullValue(
                        waitCfg.message,
                        'Destruindo os dados...'
                    )
                }
            )
        }

        Ext.apply(
            cfg,
            {
                success: function(request) {
                    var rst = Ext.decode(request.responseText);

                    if(rst.success)
                        core.invokeCallback (
                            cfg.externalCallback.success,
                            rst.instance
                        );
                    else {
                        Ext.Msg.show({
                            title: 'Removendo',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });

                        core.invokeCallback(
                            cfg.externalCallback.failure,
                            rst.instance
                        );
                    }
                },
                failure: function(request) {
                    var message = '';

                    if(request.failureType == 'connect')
                        message = 'O recurso esta indisponível no momento. Cheque sua conectividade.';
                    else if(request.failureType == 'server')
                        message = 'O sistema não conseguiu responder sua requisição, tente novamente mais tarde.';

                    Ext.Msg.show({
                        title: 'Removendo',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message
                    });
                },
                callback: function(request) {
                    if(mask) {
                        mask.hide();
                        delete mask;
                    }
                }
            }
        );

        mask != false && mask.show();
        this.doRequest(cfg);
    },

    _definedRouteByName: function(name) {
        return this.definedRoutes[name] || null;
    },

    getRoute: function(action, pk, defaultVerb, conf) {
        var rst, resource, verb;
        pk = pk || null;

        if (pk && this._definedRouteByName(action + '_id'))
            action = action + '_id';

        if(this._definedRouteByName(action))
            resource = this.definedRoutes[action];
        else if(!pk)
            resource = '{resource}/{action}/';
        else
            resource = '{resource}/{action}/{id}/';

        if(this.verb[action] != undefined)
            verb = this.verb[action];
        else
            verb = core.nullValue(defaultVerb, 'GET');

        if(global.Context != undefined)
            resource = '/{context}/' + resource;

        var data = {
            context: global.Context,
            resource: this.resource,
            version: this.version,
            action: action
        };

        if(pk) {
            data.id = (Ext.isArray(pk) && pk !== null) ?
                pk.join('/') :
                pk;
        }


        rst = {
            method: verb,
            url: Ext._create('Ext.XTemplate', [resource]).apply(data)
        };

        if(conf) Ext.applyIf(rst, conf);

        return rst;
    },

    doRequest: function(cfg) {
        if(!cfg.externalCallback) cfg.externalCallback = {};
        if(cfg.method != 'GET') {
            var headers = core.nullValue(cfg.headers, {});

            if(cfg.upload)
                Ext.applyIf(headers, {'Content-Type': 'multipart/form-data'});
            else
                Ext.applyIf(headers, {'Content-Type': 'application/x-www-form-urlencoded'});

            cfg.headers = headers;
        }

        Ext.Ajax.request(cfg);
    },

    getFields: function() {
        return [
            {name: 'pk', type: 'int'},
            {name: 'unicode', type: 'string'}
        ];
    },

    relatedAdd: function(related, pk, items, success, failure, finish) {
        var params = {
            field: related
        };

        params[related] = items;

        this.doRequest(
            this.getRoute(
                'related',
                pk,
                'POST',
                {
                    params: params,
                    scope: this,
                    callback: function() {
                        core.invokeCallback(finish || { fn: Ext.emptyFn });
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if (rst.success) {
                            core.invokeCallback(
                                success || { fn: Ext.emptyFn },
                                rst
                            );
                        } else {
                            core.invokeCallback(
                                failure || { fn: Ext.emptyFn },
                                rst.message
                            );
                        }
                    },
                    failure: function() {
                        core.invokeCallback(
                            failure || { fn: Ext.emptyFn },
                            'Recurso indisponivel no momento, tente mais tarde.'
                        );
                    }
                }
            )
        );
    },

    relatedRemove: function (related, pk, items, success, failure, finish) {
        var params = {
            field: related
        };

        params[related] = items;

        this.doRequest(
            this.getRoute(
                'related',
                pk,
                'DELETE',
                {
                    params: params,
                    scope: this,
                    callback: function () {
                        core.invokeCallback(finish || { fn: Ext.emptyFn });
                    },
                    success: function (xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if (rst.success) {
                            core.invokeCallback(
                                success || { fn: Ext.emptyFn },
                                rst
                            );
                        } else {
                            core.invokeCallback(
                                failure || { fn: Ext.emptyFn },
                                rst.message
                            );
                        }
                    },
                    failure: function () {
                        core.invokeCallback(
                            failure || { fn: Ext.emptyFn },
                            'Recurso indisponivel no momento, tente mais tarde.'
                        );
                    }
                }
            )
        );
    },

    relatedCollection: function (related, pk, success, failure, finish) {
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {

            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        if(cfg.resource){
            Ext.apply(this, {resource: cfg.resource})
        }
        // this.callParent([cfg]);
        core.Restful.superclass.constructor.call(this, cfg);
    }
});
