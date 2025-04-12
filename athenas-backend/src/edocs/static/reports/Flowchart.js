Ext._define('edocs.reports.Flowchart', {
    extend: 'Object',

    singleton: {
        /**
         * Este método requisita a geração de um fluxograma (GraphViz) 
         * para as movimentações de um protocolo.
         * 
         * Propriedades esperadas em cfg (objeto literal):
         * 
         * @param {Object} cfg.el (optional): Objeto onde a mask será aplicado.
         * @param {String} cfg.waitMessage (optional): Texto a ser exibido durante processamento.
         * @param {Number} cfg.params.protocol (required): Uma chave-primária de Protocolo.
         * @param {String} cfg.params.output_format (required): Um formato de saída: 'svg', 'png', 'jpg' ou 'pdf'.
         */
        generate: function (cfg) {
            cfg = cfg || {};
            cfg.el = cfg.el || Ext.getBody();
            cfg.waitMessage = cfg.waitMessage || 'Processando...';
            cfg.params = cfg.params || {};

            var mask = new Ext.LoadMask(cfg.el, cfg.waitMessage);
            mask.show();

            Ext.Ajax.request({
                url: core.callAction('EDOCFlowchart', 'generate'),
                params: cfg.params,
                callback: function () {
                    mask.hide();
                },
                success: function (xhr) {
                    var result = Ext.decode(xhr.responseText);

                    Ext.Msg.show({
                        title: 'Gerando fluxograma',
                        msg: result.message,
                        icon: (result.success ? Ext.Msg.INFO : Ext.Msg.ERROR),
                        buttons: Ext.Msg.OK
                    });
                },
                failure: function () {
                    Ext.Msg.show({
                        title: 'Gerando fluxograma',
                        msg: 'Recurso indisponível no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            });
        },
    }
});
