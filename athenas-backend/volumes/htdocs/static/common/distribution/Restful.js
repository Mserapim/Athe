Ext._define('common.distribution.Restful', {
    extend: 'core.Restful',

    resource: 'CDDistribution',

    copyPlayers: function (params, cbSuccess, cbFailure, cbCallback) {
        var route = this.getRoute('copy_players', null, 'POST', {
            params: params,
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
        if (!this._fields) {
            this._fields = common.distribution.Restful
                               .superclass
                               .getFields
                               .call(this, cfg)
                               .concat([
                {
                    type: "int",
                    name: "origin",
                    useNull: true
                },
                {
                    type: "string",
                    name: "origin_unicode"
                },
                {
                    type: "string",
                    name: "title"
                },
                {
                    type: "date",
                    name: "modified_at",
                    dateFormat: "d/m/Y H:i"
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
                    type: "date",
                    name: "created_at",
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
                }
            ]);
        }

        return this._fields;
    }
});
