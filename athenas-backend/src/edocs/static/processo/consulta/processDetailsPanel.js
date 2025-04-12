/**
 *
 **/
Ext._define('edocs.processo.consulta.processDetailsPanel', {
    extend: 'core.RestfulPanel',

    height: 300,

    rest: 'edocs.processo.Restful',

    _prepareSuccessCallback: function(callback) {
        var wnd = this;
        var success = callback.success;

        function foo(args) {
            core.invokeCallback(
                success,
                args
            );
        };

        callback.success = {
            fn: foo
        };

        return callback
    },

    manageSelectProcess: function(process) {
        var tpl = new Ext.XTemplate("<p>Selecione um processo para visualizar os detalhes...</p>");
        if(this._formPanel.body != undefined)
            tpl.overwrite(this._formPanel.body, {});
        if(process != undefined)
            this.getTplDetails().overwrite(this._formPanel.body, process.data);
    },

    getTplDetails: function() {
        return new Ext.XTemplate(
            "<table class=\"property\">",
                "<tr>",
                    "<td class=\"field\"><font size=2>Num. Protocolo :</font></td>",
                    "<td><font size=2>{codigo}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Processo :</font></td>",
                    "<td><font size=2>{codigo_processo}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>P. Externo :</font></td>",
                    "<td><font size=2>{protocolo_externo}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Classe :</font></td>",
                    "<td class=\"value\"><font size=2>{tipo_documento_unicode}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Assunto :</font></td>",
                    "<td class=\"value\"><font size=2>{assunto_display}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Protocolado por :</font></td>",
                    "<td class=\"value\"><font size=2>{protocolado_por}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Volume :</font></td>",
                    "<td class=\"value\"><font size=2>{volume}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Página :</font></td>",
                    "<td class=\"value\"><font size=2>{paginas}</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Situação :</font></td>",
                    "<td class=\"value\"><font size=2>{situacao_display}</font></td>",
                "</tr>",
                '<tpl if="caixa != 0">',
                "<tr>",
                    "<td class=\"field\"><font size=2>Caixa :</font></td>",
                    "<td class=\"value\"><font size=2>{caixa}</font></td>",
                "</tr>",
                '</tpl>',
                "<tr>",
                "<td class=\"field\"><font size=2>Qtde de dias :</font></td>",
                "<td class=\"value\"><font size=2>{dias_criacao}</font></td>",
                "</tr>",
                "<tr>",
                "<td class=\"field\"><font size=2>Interessados :</font></td>",
                "<td class=\"value\"><font size=2>",
                '<tpl for="interessados">',
                    "{1} <br>",
                '</tpl>',
                "</font></td>",
                "</tr>",
                "<tr>",
                    "<td class=\"field\"><font size=2>Resumo :</font></td>",
                    "<td class=\"value\"></td>",
                "</tr>",
                "<tr>",
                    "<td colspan=\"2\" class=\"value\"><div style=\"height: 70px; width: 660px; overflow: auto; padding: 8px;\">{resumo}</div></td>",
                "</tr>",
            "</table>"
        );
    },

   getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'panel',
                        autoScroll: true,
                        border: false,
                        title: 'Detalhes',
                        bodyStyle: "border:none;",
                        html: "<p>Selecione um processo para visualizar os detalhes...</p>"
                    }]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                labelWidth:150,
                labelAlign:'right',
                action: 'update',
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                        }
                    }
                }
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        edocs.processo.consulta.processDetailsPanel.superclass.constructor.call(this, cfg);
    }
})
