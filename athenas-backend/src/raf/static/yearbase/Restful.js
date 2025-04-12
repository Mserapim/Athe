Ext._define('raf.yearbase.Restful', {
    extend: 'core.Restful',

    resource: 'RAFYearBase',

    enable: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'enable',
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

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.yearbase.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons"},
                {type: "string", name: "title"},
                {type: "date", name: "valid_of", dateFormat: "d/m/Y H:i"},
                {type: "bool", name: "activated"}
            ]);

        return this._fields;
    }
});
