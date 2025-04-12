Ext._define('common.distribution.reward.Restful', {
    extend: 'core.Restful',

    resource: 'CDReward',

    resetMatch: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'reset_match',
                pk,
                'POST',
                {
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                        core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );
    },

    distributeManually: function(player, pkset, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'distribute_manually',
                null,
                'POST',
                {
                    params: {
                        pkset: pkset,
                        player: player
                    },
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );

    },

    distribute: function(pkset, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'distribute',
                null,
                'POST',
                {
                    params: { pkset: pkset },
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );
    },

    cancelDistribution: function (pkset, cbSuccess, cbFailure, cbCallback) {
        var route = this.getRoute('cancel_distribution', null, 'POST', {
            params: {pkset: pkset},
            scope: this,
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    core.invokeCallback(
                        cbSuccess || {fn: Ext.emptyFn},
                        result);
                } else {
                    core.invokeCallback(
                        cbFailure || {fn: Ext.emptyFn},
                        result.message);
                }
            },
            failure: function () {
                core.invokeCallback(
                    cbFailure || {fn: Ext.emptyFn},
                    'Recurso indisponível no momento.');
            },
            callback: function () {
                core.invokeCallback(cbCallback || {fn: Ext.emptyFn});
            }
        });

        this.doRequest(route);
    },

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = common.distribution.reward.Restful
                               .superclass
                               .getFields
                               .call(this, cfg)
                               .concat([
                {
                    type: "date",
                    name: "distributed_at",
                    dateFormat: "d/m/Y H:i",
                    useNull: true
                },
                {
                    type: "int",
                    name: "distributed_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "distributed_by_unicode"
                },
                {
                    type: "date",
                    name: "canceled_at",
                    dateFormat: "d/m/Y H:i",
                    useNull: true
                },
                {
                    type: "int",
                    name: "canceled_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "canceled_by_unicode"
                },
                {
                    type: "int",
                    name: "modified_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "modified_by_unicode"
                },
                {
                    type: "string",
                    name: "title"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "int",
                    name: "winner",
                    useNull: true
                },
                {
                    type: "string",
                    name: "winner_unicode"
                },
                {
                    type: "date",
                    name: "modified_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "int",
                    name: "created_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "created_by_unicode"
                },
                {
                    type: "bool",
                    name: "distributed_manually"
                },
                {
                    type: "int",
                    name: "distribution",
                    useNull: true
                },
                {
                    type: "string",
                    name: "distribution_unicode"
                },
                {
                    type: "string",
                    name: "external_number"
                }
            ]);

        return this._fields;
    }
});
