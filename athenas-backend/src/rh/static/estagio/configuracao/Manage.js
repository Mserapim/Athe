/**
 *
 **/
Ext._define('estagio.configuracao.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getConceitoGrid: function() {
        if(!this._conceitogrid) {
            this._conceitogrid = Ext._create('estagio.conceito.ConceitoGrid', {
                region: 'center',
                title: 'Conceito',
                minHeight: 200,
            });

        }

        return this._conceitogrid;
    },

    getConfiguracaoGrid: function() {
        if(!this._configuracaogrid) {
            this._configuracaogrid = Ext._create('estagio.configuracao.ConfiguracaoGrid', {
                region: 'south',
                height: 400,
                title: 'Configuração'
            });

        }

        return this._configuracaogrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Configuração'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getConceitoGrid(),
                    this.getConfiguracaoGrid(),
                ]
            }
        );

        estagio.configuracao.Manage.superclass.constructor.call(this, cfg);
    }
});
