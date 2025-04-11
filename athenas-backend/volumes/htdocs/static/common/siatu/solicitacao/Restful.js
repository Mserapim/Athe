/**
 *
 **/
Ext._define('common.siatu.solicitacao.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuSolicitacao',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.solicitacao.Restful.superclass.getFields.call(this).concat([
               {name: 'solicitante', type: 'int'},
               {name: 'solicitante_username', type: 'string'},
               {name: 'solicitante_lotacao', type: 'string'},
               {name: 'telefone', type: 'string'},
               {name: 'servico', type: 'int'},
               {name: 'servico_unicode', type: 'string'},
               {name: 'tipo', type: 'int'},
               {name: 'tipo_display', type: 'string'},
               {name: 'descricao_problema', type: 'string'},
               {name: 'reincidencia', type: 'boolean'},
               {name: 'chamado', type: 'int'},
               {name: 'chamado_anterior', type: 'int'},
            ]);

        return this._fields;
    }
});
