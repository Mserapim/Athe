/**
 *
 **/
Ext._define('common.siatu.chamado.reincidencia.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuReincidencia',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.chamado.Restful.superclass.getFields.call(this).concat([
                {name: 'opiniao_atendente', type: 'string'},
                {name: 'confirm_atendente', type: 'bool'},
                {name: 'motivo_gerente', type: 'string'},
                {name: 'parecer', type: 'string'},

            ]);

        return this._fields;
    },

});
