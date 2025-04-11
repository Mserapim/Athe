Ext._define('rh.teletrabalho.gestor_relatorio_semestral.servidor.Restful', {
    extend: 'core.Restful',

    resource: 'ServidorRelatorioSemestral',

    getFields: function () {
        var fields = rh.teletrabalho.gestor_relatorio_semestral.servidor.Restful.superclass.getFields.call(this);
        return fields.concat([
            { name: 'servidor_pk', type: 'pk' },
            { name: 'pk', type: 'pk' },
            { name: 'matricula', type: 'int' },
            { name: 'nome', type: 'string' },
            { name: 'tipo', type: 'string' },
            { name: 'data_inicio', type: 'date' ,dateFormat: "d/m/Y"},
            { name: 'data_fim', type: 'date', dateFormat: "d/m/Y" },
 
        ]);
    }
});
