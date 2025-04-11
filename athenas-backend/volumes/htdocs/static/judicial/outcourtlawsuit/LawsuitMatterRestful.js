
Ext._define('judicial.outcourtlawsuit.LawsuitMatterRestful', {
    extend: 'core.Restful',

    resource: 'EJudLawsuitMatter',

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
            this._fields = judicial.outcourtlawsuit.LawsuitMatterRestful.superclass.getFields.call(this, cfg).concat([
                {
                    name: 'icons'
                }, 
                {
                    type: 'bool', 
                    name: 'principal'
                }, 
                {
                    type: 'string', 
                    name: 'matter_unicode'
                },
                {
                    type: 'int', 
                    name: 'matter'
                },
                {
                    type: 'string', 
                    name: 'lawsuit_unicode'
                },
                {
                    type: 'int', 
                    name: 'lawsuit'
                }
            ]);

        return this._fields;
    }
});
