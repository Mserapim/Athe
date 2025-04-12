
Ext._define('judicial.parts.ConfidentialAccessRestful', {
    extend: 'judicial.PartLawsuitRestful',

    markerPartLawsuit: function(pk, part, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'markerPartLawsuit',
                false,
                'POST',
                {
                    params: {
                        part: part,
                        confidentialaccess: pk
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

    unmarkerPartLawsuit: function(pk, part, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'unmarkerPartLawsuit',
                false,
                'POST',
                {
                    params: {
                        part: part,
                        confidentialaccess: pk
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


    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.parts.ConfidentialAccessRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "apply_in"
                },
            ]);

        return this._fields;
    }

});
