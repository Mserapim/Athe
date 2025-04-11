/**
 *
 **/
Ext._define('adm.patrimonio.entrada.Restful', {
    extend: 'core.Restful',

    resource: 'PATNotaEntrada',

    getFields: function() {
        return adm.patrimonio.entrada.Restful.superclass.getFields.call(this).concat([
            {name: 'fornecedor_unicode', type: 'string'},
            {name: 'fornecedor', type: 'int'},
            {name: 'conta_unicode', type: 'string'},
            {name: 'conta', type: 'int'},
            {name: 'empenho_unicode', type: 'string'},
            {name: 'empenho', type: 'int'},
            {name: 'note_year', type: 'int'},
            {name: 'note_number', type: 'int'},
            {name: 'formated_number', type: 'string'},
            {name: 'data_cadastro', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_nota', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_compra', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_liquidacao', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'execucao_orcamentaria_display', type: 'string'},
            {name: 'execucao_orcamentaria', type: 'int'},
            {name: 'liquidacao', type: 'string'},
            {name: 'processo', type: 'string'},
            {name: 'icons', type: 'auto'},
            {name: 'type', type: 'string'},
            {name: 'suspenso', type: 'bool'}
        ]);
    }
});
