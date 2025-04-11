/**
 *
 **/
Ext._define('common.siatu.chamado.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuChamado',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.chamado.Restful.superclass.getFields.call(this).concat([
                {name: 'identificacao', type: 'string'},
                {name: 'solicitacao', type: 'int'},
                {name: 'solicitante', type: 'int'},
                {name: 'telefone', type: 'string'},
                {name: 'solicitante_lotacao', type: 'string'},
                {name: 'solicitante_username', type: 'string'},
                {name: 'solicitante_nome', type: 'string'},
                {name: 'solicitante_cidade', type: 'string'},
                {name: 'solicitante_membro', type: 'string'},
                {name: 'servico', type: 'int'},
                {name: 'servico_atendentes', type: 'list'},
                {name: 'servico_unicode', type: 'string'},
                {name: 'transf_ativa', type: 'int'},

                {name: 'icon_status', type: 'auto'},
                {name: 'status_atual', type: 'string'},
                {name: 'tempo_decorrido', type: 'string'},

                {name: 'atendentes', type: 'list'},
                {name: 'atendente_unicode', type: 'string'},

                {name: 'terceiro_interno', type: 'list'},

                {name: 'problema_solicitante', type: 'string'},

                {name: 'avaliacao', type: 'string'},
                {name: 'avaliacao_pk', type: 'string'},
                {name: 'motivo_avaliacao', type: 'string'},
                {name: 'replicado', type: 'boolean'},

                {name: 'reincidencia', type: 'string'},
                {name: 'reincidencia_confirm_atendente', type: 'bool'},
                {name: 'reincidencia_parecer', type: 'string'},
                {name: 'chamado_anterior', type: 'string'},
                {name: 'chamado_anterior_numero', type: 'string'},
                {name: 'chamado_anterior_atendente', type: 'string'},
                {name: 'chamado_anterior_problema', type: 'string'},
                {name: 'chamado_anterior_relatorio', type: 'string'},
                {name: 'chamado_anterior_pk', type: 'int'},

                {name: 'urgente', type: 'bool'},
                {name: 'nao_urgente', type: 'bool'},
                {name: 'rank', type: 'int'},
                {name: 'motivo_urgencia', type: 'string'},
                {name: 'fila', type: 'int'},
                {name: 'tipo_fila', type: 'string'},
                {name: 'cancelado', type: 'bool'},
                {name: 'motivo_cancelado', type: 'string'},

                {name: 'solicitante_aguardando_avaliacao', type: 'string'},
                {name: 'solicitante_transferido_atendente', type: 'string'},
                {name: 'solicitante_garantia', type: 'string'},
                {name: 'solicitante_terceirizada', type: 'string'},
                {name: 'solicitante_viagem', type: 'string'},

                {name: 'atendente_transferido_atendente', type: 'string'},
                {name: 'atendente_apos_avaliacao', type: 'string'},

                {name: 'nao_institucional', type: 'boolean'},
                {name: 'relatorio', type: 'string'},
                {name: 'relatorio_display', type: 'string'},
            ]);

        return this._fields;
    },

    rendererDocument: function(pk, cbSuccess, cbFailure, cbCallback) {

        // console.log('render de chamado');
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

core.RestfulGrid.register(
    'common.siatu.chamado.Restful',
    'common.siatu.chamado.Grid'
);
