Ext._define('planning.hiring.agreement.Restful', {
    extend: 'core.Restful',

    resource: 'PHAAgreement',

    generateFromSolicitations: function(solicitationIdSet, values, successCallback, falureCallaback, commonCallback) {
        values.solicitation_set = solicitationIdSet;
        values.copiar_fiscais = values.copiar_fiscais ? values.copiar_fiscais : 'off';

        this.doRequest(
            this.getRoute(
                'generate_from_solicitations',
                false,
                'POST',
                {
                    params: values,
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            core.invokeCallback(
                                successCallback || { fn: Ext.emptyFn },
                                rst
                            );
                        } else {
                            core.invokeCallback(
                                falureCallaback || { fn: Ext.emptyFn },
                                rst.message
                            );
                        }
                    },
                    failure: function(xhr) {
                        core.invokeCallback(
                            falureCallaback || { fn: Ext.emptyFn },
                            'Recurso indisponivel nomento.'
                        );
                    },
                    callback: function(xhr) {
                        core.invokeCallback(commonCallback || { fn: Ext.emptyFn });
                    }
                }
            )
        );
    },

    rendererDocument: function (pk, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function (message) {
                Ext.Msg.show({
                    title: 'Buscando documento',
                    msg: message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        };

        this.doRequest(this.getRoute(
            'renderer_document',
            pk,
            'GET', {
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.document);
                    else
                        core.invokeCallback((emptyFailure || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function (xhr) {
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
                },
                callback: function () {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.agreement.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons"},
                {type: "string",name: "numero"},
                {type: "string",name: "main_agreementsupervisors"},
                {type: "int",name: "tipo_contrato"},
                {type: "string",name: "tipo_contrato_display"},
                {type: "string",name: "numero_processo"},
                {type: "string",name: "numero_processo_mae"},
                {type: "float",name: "valor"},
                {type: "string",name: "objeto_contrato"},
                {type: "string",name: "data_inicio"},
                {type: "string",name: "data_vencimento_flag"},
                {type: "string",name: "data_vencimento"},
                {type: "int",name: "dias_para_aviso"},
                {type: "int",name: "tipo_licitacao"},
                {type: "string",name: "numero_licitacao"},
                {type: "int",name: "tipo_medicao"},
                {type: "int",name: "file"},
                {type: "string",name: "dia_pagamento"},
                {type: "string",name: "numero_pasta"},
                {type: "string",name: "data_publicacao"},
                {type: "string",name: "status"},
                {type: "int",name: "pessoa"},
                {type: "int",name: "responsaveis"},
                {type: "int",name: "solicitation"},
                {type: "int",name: "order"},
                {type: "int",name: "index"},
                {type: "int",name: "reference_month"},
                {type: "string",name: "readjustment_anniversary"},
            ]);

        return this._fields;
    }
});
