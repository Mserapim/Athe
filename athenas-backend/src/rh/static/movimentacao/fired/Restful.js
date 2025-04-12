/**
 *
 **/
Ext._define('rh.movimentacao.fired.Restful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'RHFiredMoveRestful',

    constructor: function (cfg) {
        rh.movimentacao.fired.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function () {
        if (!this._fields) {
            this._fields = rh.movimentacao.fired.Restful.superclass.getFields.call(this, {}).concat([
                { type: 'int', name: 'movimentacao_posse', useNull: true },
                { type: 'string', name: 'movimentacao_posse_unicode' },
                { type: 'int', name: 'tipo_desligamento', useNull: true },
                { type: 'string', name: 'tipo_desligamento_display' },
                { type: 'int', name: 'opcao', useNull: true },
                { type: 'string', name: 'opcao_display' },
                { type: 'date', name: 'data_desligamento', dateFormat: 'd/m/Y' },
                { type: 'bool', name: 'vacancia' },
                { type: 'bool', name: 'termination_process' },
            ]);
        }
        return this._fields;
    }
});
