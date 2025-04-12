Ext._define('raf.quiz.Restful', {
    extend: 'core.Restful',

    resource: 'RAFQuiz',

    copyQuiz: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'copy_quiz',
                false,
                'POST',
                {
                    scope: this,
                    params: values,
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

    changeOrder: function(values, cbSuccess, cbFailure, cbCallback) {

        this.doRequest(
            this.getRoute(
                'change_order',
                false,
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
            this._fields = raf.quiz.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons"},
                {type: "integer", name: "typequiz", useNull: true},
                {type: "string", name: "typequiz_unicode"},
                {type: "string", name: "yearbase_unicode"},
                // {type: "string", name: "list_classes"},
                {type: "integer", name: "yearbase", useNull: true},
                {type: "bool", name: "activated"},
                {type: "integer", name: "number_order", useNull: true},
                // {type: "string", name: "list_taxonomy", useNull: true}
            ]);

        return this._fields;
    }
});
