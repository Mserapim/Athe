/**
 *
 **/
Ext._define('rh.movimentacao.possession.request.PeriodoRequisicaoRestful', {
    extend: 'core.Restful',

    resource: 'RHPeriodoRequisicaoRestful',

    getFields: function() {
        return rh.movimentacao.possession.request.PeriodoRequisicaoRestful.superclass.getFields.call(this).concat([
            {name: 'requisicao_unicode', type: 'string'},
            {name: 'requisicao', type: 'int'},
            {name: 'publicacao_unicode', type: 'string'},
            {name: 'publicacao', type: 'int'},
            {name: 'data_inicio', type: 'string'},
            {name: 'data_fim', type: 'string'}
        ]);
    }
});
