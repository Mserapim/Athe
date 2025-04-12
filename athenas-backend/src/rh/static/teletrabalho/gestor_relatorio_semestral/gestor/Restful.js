Ext._define('rh.teletrabalho.gestor_relatorio_semestral.gestor.Restful', {
    extend: 'core.Restful',

    resource: 'GestorRelatorioSemestral',

    getFields: function () {
        var fields = rh.teletrabalho.gestor_relatorio_semestral.gestor.Restful.superclass.getFields.call(this);
        return fields.concat([
            { name: 'pk', type: 'pk' },
            { name: 'matricula', type: 'int' },
            { name: 'nome', type: 'string' },
            { name: 'lotacao', type: 'string' },
            { name: 'enviado', type: 'auto' },
            { name: 'cod_vdf', type: 'int' },
        ]);
    }
});
