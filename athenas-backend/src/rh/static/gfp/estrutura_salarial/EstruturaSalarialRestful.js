/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.EstruturaSalarialRestful', {
    extend: 'core.Restful',

    resource: 'GFPEstruturaSalarialRestful',

    remote: false,

    getFields: function() {
        var fields = rh.gfp.estrutura_salarial.EstruturaSalarialRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'codigo', type: 'string'},
            {name: 'titulo', type: 'string'},
            {name: 'formatacao', type: 'string'},
            {name: 'descricao', type: 'string'},
            {name: 'meses_progressao_inicial', type: 'int'},
            {name: 'meses_progressao', type: 'int'},
            {name: 'data_vigencia_inicio', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_vigencia_fim', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'publicacao', type: 'int'},
            {name: 'publicacao_unicode', type: 'string'},
            {name: 'estrutura_revogacao', type: 'int'},
            {name: 'estrutura_revogacao_unicode', type: 'string'},
            {name: 'identifier', type: 'int'},
            {name: 'horizontal_name', type: 'string'},
            {name: 'vertical_name', type: 'string'},
            {name: 'horizontal_labels', type: 'string'},
            {name: 'vertical_labels', type: 'string'},
            {name: 'ativo', type: 'boolean'},
            {name: 'salary_unit', type: 'int'},
        ]);
    }
});
