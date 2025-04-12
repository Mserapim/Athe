Ext._define('corregedoria.cirdir.health.assessment.Restful', {

    extend: 'core.Restful',

    resource: 'CIRDIRHealthAssessmentRestful',

    sign: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'sign',
                false,
                'POST',
                {
                    scope: this,
                    params: {
                        pk: pk
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

    getFields: function(cfg) {
        if(!this._fields) {
          this._fields = corregedoria.cirdir.health.assessment.Restful.superclass.getFields.call(this, cfg).concat([
            {
                type: "auto",
                name: "icons"
            },
            {
                "type": "int",
                "name": "health",
                "useNull": true
            },
            {
                "type": "string",
                "name": "health_unicode"
            },
            {
                "type": "int",
                "name": "evaluator",
                "useNull": true
            },
            {
                "type": "string",
                "name": "evaluator_unicode"
            },
            {
                "type": "string",
                "name": "content"
            },
            {
                "type": "string",
                "name": "signed_by_unicode"
            },
            {
                "type": "int",
                "name": "signed_by",
                "useNull": true
            },
            {
                "type": "string",
                "name": "integrant_unicode"
            },
            {
                "type": "int",
                "name": "integrant",
                "useNull": true
            }

          ]);
        }
        return this._fields;
    },
});
