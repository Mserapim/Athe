/**
 *
 **/
Ext._define('estagio.avaliador.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEstagioProbatorioAvaliadorGrid: function() {
        if(!this._estagiogrid) {
            this._estagiogrid = Ext._create('estagio.avaliador.EstagioProbatorioAvaliadorGrid', {
                region: 'center',
            });
        }

        return this._estagiogrid;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Avaliação de Estágio Probatório'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getEstagioProbatorioAvaliadorGrid(),
                ]
            }
        );

        estagio.avaliador.Manage.superclass.constructor.call(this, cfg);
    }
});
