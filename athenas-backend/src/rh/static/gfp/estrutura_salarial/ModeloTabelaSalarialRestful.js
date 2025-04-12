/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.ModeloTabelaSalarialRestful', {
    extend: 'core.Restful',

    resource: 'GFPModeloTabelaSalarialRestful',

    remote: false,

    getFields: function() {
        var fields = rh.gfp.estrutura_salarial.ModeloTabelaSalarialRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'pk', type: 'int'},
            {name: 'titulo', type: 'string'},
            {name: 'quantidade_horizontal', type: 'int'},
            {name: 'quantidade_vertical', type: 'int'},
            {name: 'titulo_vertical', type: 'string'},
            {name: 'titulo_horizontal', type: 'string'},
            {name: 'labels_vertical', type: 'string'},
            {name: 'labels_horizontal', type: 'string'},
        ]);
    }
});
