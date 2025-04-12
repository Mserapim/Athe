/**
 *
 **/
Ext._define('edocs.processo.Restful', {
    extend: 'core.Restful',

    resource: 'EpadProcesso',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.Restful.superclass.getFields.call(this).concat([
              {name: 'status', type: 'auto'},
              {name: 'codigo', type: 'string'},
              {name: 'codigo_processo', type: 'string'},
              {name: 'protocolo_externo', type: 'string'},
              {name: 'midia_display', type: 'string'},
              {name: 'data', type: 'string'},
              {name: 'assunto_display', type: 'string'},
              {name: 'assunto_processo', type: 'int'},
              {name: 'origem', type: 'string'},
              {name: 'posicao', type: 'string'},
              {name: 'movimentacao', type: 'int'},
              {name: 'passo', type: 'int'},
              {name: 'paginas', type: 'int'},
              {name: 'situacao_display', type: 'string'},
              {name: 'volume', type: 'string'},
              {name: 'custo', type: 'string'},
              {name: 'dias_criacao', type: 'string'},
              {name: 'primeiro_interessado', type: 'string'},
              {name: 'caixa', type: 'string'},
              {name: 'id', type: 'int'},
              {name: 'orgao_geral_origem', type: 'int'},
              {name: 'midia', type: 'string'},
              {name: 'tipo_documento', type: 'int'},
              {name: 'tipo_documento_unicode', type: 'string'},
              {name: 'sigiloso', type: 'boolean'},
              {name: 'resumo', type: 'string'},
              {name: 'protocolado_por', type: 'string'},
              {name: 'interessados', type: 'list'},
              {name: 'referencias', type: 'list'},
              {name: 'referenciado_por', type: 'list'},
            ]);

        return this._fields;
  },

  rendererDocument: function(pk, cbSuccess, cbFailure, cbCallback) {
      var emptyFailure = {
          fn: function(message) {
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
          'GET',
          {
              success: function(xhr) {
                  var rst = Ext.decode(xhr.responseText);

                  if(rst.success)
                      core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst.document);
                  else
                      core.invokeCallback((emptyFailure || {fn: Ext.emptyFn}), rst.message);

              },
              failure: function(xhr) {
                  core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
              },
              callback: function() {
                  core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
              }
          }
      ));
  },
});
