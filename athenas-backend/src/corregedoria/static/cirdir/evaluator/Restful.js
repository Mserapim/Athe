Ext._define('corregedoria.cirdir.evaluator.Restful', {

    extend: 'core.Restful',

    resource: 'CIRDIREvaluatorRestful',

    getFields: function(cfg) {
        if(!this._fields) {
          this._fields = corregedoria.cirdir.evaluator.Restful.superclass.getFields.call(this, cfg).concat([
            {
              "name": "icons"
            },
            {
                "type": "int",
                "name": "employee",
                "useNull": true
            },
            {
                "type": "string",
                "name": "employee_unicode"
            },
            {
              "type": "bool",
              "name": "enabled"
            },

          ]);
        }
        return this._fields;
    },

    delivery: function(evaluator_pks, health_pks, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'delivery',
                undefined,
                'POST',
                {
                    scope: this,
                    params: {
                        evaluators: evaluator_pks,
                        healths: health_pks
                    },
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
});
