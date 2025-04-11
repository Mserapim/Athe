/**
 *
 **/
Ext._define('rh.movimentacao.requisicao.Restful', {
    extend: 'core.Restful',

    resource: 'RHRequisicaoRestful',

    getFields: function() {
        return rh.movimentacao.requisicao.Restful.superclass.getFields.call(this).concat([
            {name: 'pk', type: 'string'},
            {name: 'orgao_origem_unicode', type: 'string'},
            {name: 'orgao_origem', type: 'int'},
            {name: 'posse_origem_unicode', type: 'string'},
            {name: 'posse_origem', type: 'int'},
            {name: 'publicacao_movimentacao_unicode', type: 'string'},
            {name: 'publicacao_movimentacao', type: 'int'},
            {name: 'publicacao_alteracao_unicode', type: 'string'},
            {name: 'publicacao_alteracao', type: 'int'},
            {name: 'onus_display', type: 'string'},
            {name: 'onus', type: 'int'},
            {name: 'data_inicio', type: 'string'},
            {name: 'data_fim', type: 'string'},
            {name: 'anota', type: 'boolean'},
            {name: 'texto', type: 'text'},
            {name: 'category', type: 'string'},
        ]);
    }
});
