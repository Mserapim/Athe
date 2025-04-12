Ext._define('edocs.processo.taxonomy.MatterRestful', {
    extend: 'core.Restful',

    resource: 'EPADProcessMatter',

    definePrincipal: function(pk, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'define_principal',
                pk,
                'POST',
                {
                    params: values,
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
            this._fields = common.saci.typology.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'icons'},
                {
                    type: "string",
                    name: "legal_matter_unicode"
                },
                {
                    type: "int",
                    name: "legal_matter",
                    useNull: true
                },
                {
                    type: "bool",
                    name: "principal"
                },
                {
                    type: "int",
                    name: "process",
                    useNull: true
                },
                {
                    type: "string",
                    name: "process_unicode"
                }
            ]);

        return this._fields;
    }
});
