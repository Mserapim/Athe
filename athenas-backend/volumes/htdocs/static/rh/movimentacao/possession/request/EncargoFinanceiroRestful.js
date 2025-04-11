/**
 *
 **/
Ext._define('rh.movimentacao.possession.request.EncargoFinanceiroRestful', {
    extend: 'core.Restful',

    resource: 'RHEncargoFinanceiro',

    getFields: function() {
        return rh.movimentacao.possession.request.EncargoFinanceiroRestful.superclass.getFields.call(this).concat([
            {name: 'requisicao_unicode', type: 'string'},
            {name: 'requisicao', type: 'int'},
            {name: 'data_inicio', type: 'string'},
            {name: 'data_fim', type: 'string'},
            {name: 'remuneracao', type: 'float'},
            {name: 'base_previdenciaria', type: 'float'}
        ]);
    }
});
