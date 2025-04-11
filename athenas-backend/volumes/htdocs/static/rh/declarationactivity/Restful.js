/**
 *
 **/
Ext._define('rh.declarationactivity.Restful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'RHDeclarationActivityRestful',

    constructor: function(cfg) {
        rh.declarationactivity.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.declarationactivity.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "quadro", useNull: true},
                {type: "string", name: "quadro_unicode"},
                {type: "date", name: "data_exercicio", dateFormat: "d/m/Y"},
                {type: "date", name: "data_encerramento", dateFormat: "d/m/Y"},
                {type: "int", name: "lotacao", useNull: true},
                {type: "string", name: "lotacao_unicode"},
                {type: "bool", name: "ativo"},
                {type: "string", name: "turno"},
                {type: "string", name: "turno_display"},
                {type: "bool",  name: "main"},
                {type: 'date', name: 'main_schedule_date', dateFormat: 'd/m/Y' },
                { name: 'icons' },
            ]);
        }
        return this._fields;
    },

    setMain: function (pk, main, cbSuccess, cbFailure, cbCallback) {
        Ext.Ajax.request({
            scope: this,
            url: toolkit.util.Normalize.controller_action('RHDeclarationActivityRestful', 'set_main'),
            params: {
                pk: pk,
                main: main,
            },
            callback: function () {
                core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
            },
            success: function (xhr) {
                var rst = Ext.decode(xhr.responseText);

                if (rst.success)
                    core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst);
                else
                    core.invokeCallback((cbFailure || { fn: Ext.emptyFn }), rst.message);
            },
            failure: function () {
                core.invokeCallback((cbFailure || { fn: Ext.emptyFn }), 'Recurso indisponivel no momento.');
            },
        });
    },
});
