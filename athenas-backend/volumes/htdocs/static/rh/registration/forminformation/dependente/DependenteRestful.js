Ext._define('rh.registration.forminformation.dependente.DependenteRestful', {
    extend: 'core.Restful',

    resource: 'RegistrationDependenteRestful',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.registration.forminformation.dependente.DependenteRestful.superclass.getFields.call(this, cfg).concat([
                {type: "string",  name: "cpf_dependent"},
                {type:"bool", name:"cpf_dependent_can_edit"},
                {type: "date",  name: "data_nascimento_dependent",  dateFormat: "d/m/Y"},
                {type:"bool", name:"data_nascimento_dependent_can_edit"},
                {type: "date",  name: "data_inicio_dependent",  dateFormat: "d/m/Y"},
                {type:"bool", name:"data_inicio_dependent_can_edit"},
                {type: "int",  name: "grau_parentesco",  useNull: true},
                {type:"bool", name:"grau_parentesco_can_edit"},
                {type: "string",  name: "grau_parentesco_display",  useNull: true},
                {type: "string",  name: "sexo_dependent"},
                {type:"bool", name:"sexo_dependent_can_edit"},
                {type: "int",  name: "employee",  useNull: true},
                {type: "string",  name: "nome_dependent"},
                {type:"bool", name:"nome_dependent_can_edit"},
                {type: "int",  name: "tipo",  useNull: true},
                {type:"bool", name:"tipo_can_edit"},
                {type: "string",  name: "tipo_display",  useNull: true},
                {type: "int",  name: "id",  useNull: true},
                {type:"bool", name:"incapacity"},
            ]);
        return this._fields;
    }
});
