/**
 *
 **/
Ext._define('rh.pessoa.Restful', {
    extend: 'core.Restful',

    resource: 'RHPessoaRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = rh.pessoa.Restful.superclass.getFields.call(this).concat([
               {name: 'nome', type: 'string'},
               {name: 'cpf_cnpj', type: 'string'},
               {name: 'identificador', type: 'string'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'rh.pessoa.Restful',
    'rh.pessoa.Grid'
);