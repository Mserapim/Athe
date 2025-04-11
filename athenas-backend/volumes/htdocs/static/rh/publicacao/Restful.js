/**
 *
 **/
Ext._define('rh.publicacao.Restful', {
    extend: 'core.Restful',

    resource: 'RHPublicacaoRestful',

    sentToPublication: function(id, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute('sent_to_publication', id, 'POST', {
                params: values,
                scope: this,
                callback: function() {
                    core.invokeCallback(cbCallback || {});
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success)
                        core.invokeCallback(cbSuccess || {});
                    else
                        core.invokeCallback(cbFailure || {}, rst.message);
                },
                failure: function() {
                    core.invokeCallback((cbFailure || {}), 'Recurso indisponivel no momento.');
                }
            })
        );
    },

    confirmPublication: function(id, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute('confirm_publication', id, 'POST', {
                params: values,
                scope: this,
                callback: function() {
                    core.invokeCallback(cbCallback || {});
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success)
                        core.invokeCallback(cbSuccess || {});
                    else
                        core.invokeCallback(cbFailure || {}, rst.message);
                },
                failure: function() {
                    core.invokeCallback((cbFailure || {}), 'Recurso indisponivel no momento.');
                }
            })
        );
    },

    getFields: function() {
        var fields = rh.publicacao.Restful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'tipo', type: 'int'},
            {name: 'icons', type: 'auto'},
            {name: 'tipo_display', type: 'string'},
            {name: 'numero', type: 'string'},
            {name: 'ano', type: 'string'},
            {name: 'data_expedicao', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'lei_autorizativa', type: ''},
            {name: 'vehicle_page', type: 'int', useNull: true},
            {name: 'veiculo_publicacao', type: 'int', useNull: true},
            {name: 'veiculo_publicacao_display', type: 'string'},
            {name: 'publication_state', type: 'int', useNull: true},
            {name: 'publication_state_display', type: 'string'},
            {name: 'arquivo', type: 'int', useNull: true},
            {name: 'arquivo_unicode', type: 'string'},
            {name: 'origem', type: 'int', useNull: true},
            {name: 'origem_unicode', type: 'string'},
            {name: 'numero_publicacao', type: 'string'},
            {name: 'data_publicacao', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_vigencia', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'interno', type: 'boolean'},
            {name: 'indirect', type: 'boolean'},
            {name: 'interessado_nome', type: 'string'},
            {name: 'observacao', type: 'string'},
            {name: 'cache_unicode', type: 'string'},
            {name: 'document', type: 'string'},
            {name: 'formated_content', type: 'string'},
            {name: 'document_read_only', type: 'bool'},
        ]);
    }
});
