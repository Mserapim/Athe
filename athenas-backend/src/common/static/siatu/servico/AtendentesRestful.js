/**
 *
 **/
Ext._define('common.siatu.servico.AtendentesRestful', {
    extend: 'core.Restful',

    resource: 'SiatuServicoAtendentes',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.servico.AtendentesRestful.superclass.getFields.call(this).concat([
               {name: 'busy', type: 'auto'},
               {name: 'username', type: 'string'},
               {name: 'nome', type: 'string'},
               {name: 'distribuicao_automatica', type: 'boolean'},
               {name: 'icon_dist', type: 'auto'},
            ]);

        return this._fields;
    }
});
