Ext._define("rh.gestorenvioponto.Restful", {
    extend: 'core.Restful',

    resource: 'RHGestorEnvioPontos',

    getFields: function() {
        if(!this._fields){
            this._fields = rh.gestorenvioponto.Restful.superclass.getFields.call(this, {}).concat([
                { type: "string", name: "servidor_pk", useNull: true },
                { type: "boolean", name: "ativo" },
                { type: "string", name: "matricula", useNull: true },
                { type: "string", name: "nome", useNull: true },
                { type: "string", name: "lotacao", useNull: true },
                { type: "string", name: "categoria_funcional", useNull: true },
                { type: "string", name: "type_by_possession", useNull: true },
                { type: "string", name: "in_teletrabalho", useNull: true },
                { type: "string", name: "ultimo_envio", useNull: true },
                { type: "string", name: "aprovador", useNull: true },
                { type: "string", name: "status", useNull: true },
                { type: "string", name: "cod_vdf", useNull: true },
                { type: "date", name: "enviado_em", dateFormat: "d/m/Y" },
                { type: "date", name: "aprovado_em", dateFormat: "d/m/Y" },
                { type: "date", name: "efetivado_em", dateFormat: "d/m/Y" },
                { type: "string", name: "tipo_afastamento", useNull: true },
                { type: "string", name: "dt_admissao", useNull: true },
                { type: "string", name: "ano", useNull: true }, 
                { type: "string", name: "mes", useNull: true },
                { type: "int", name: "qtd_notificacoes", useNull: true },
            ]);
        }
        return this._fields;
    }
});