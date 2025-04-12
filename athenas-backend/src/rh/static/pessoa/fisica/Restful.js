/**
 *
 **/
Ext._define('rh.person.naturalperson.Restful', {
    extend: 'core.Restful',

    resource: 'RHPessoaFisicaRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = rh.person.naturalperson.Restful.superclass.getFields.call(this).concat([
                {name: 'nome', type: 'string'},
                {type: "auto", name: "municipio_naturalidade", useNull: true},
                {type: "string", name: "municipio_naturalidade_unicode"},
                {type: "int", name: "grau_instrucao", useNull: true},
                {type: "string", name: "grau_instrucao_display"},
                {type: "date", name: "modified_at", dateFormat: "d/m/Y H:i"},
                {type: "int", name: "modified_by", useNull: true},
                {type: "string", name: "modified_by_unicode"},
                {type: "date", name: "created_at", dateFormat: "d/m/Y H:i"},
                {type: "int", name: "created_by", useNull: true},
                {type: "string", name: "created_by_unicode"},
                {type: "int", name: "raca_cor", useNull: true},
                {type: "string", name: "raca_cor_display"},
                {type: "string", name: "sexo"},
                {type: "string", name: "sexo_display"},
                {type: "string", name: "rg"},
                {type: "int", name: "rg_uf", useNull: true},
                {type: "string", name: "rg_uf_unicode"},
                {type: "string", name: "rg_orgao"},
                {type: "date", name: "rg_data_expedicao", dateFormat: "d/m/Y"},
                {name: 'cpf', type: 'string'},
                {type: "string", name: "nome_pai"},
                {type: "string", name: "nome_mae"},
                {type: "string", name: "nome"},
                {type: "int", name: "estado_civil", useNull: true},
                {type: "string", name: "estado_civil_display"},
                {name: 'identificador', type: 'string'}
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'rh.person.naturalperson.Restful',
    'rh.pessoa.fisica.Grid'
);
