/**
 *
 **/
Ext._define('estagio.avaliado.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEstagioProbatorioAvaliadoGrid: function() {
        if(!this._estagiogrid) {
            this._estagiogrid = Ext._create('estagio.avaliado.EstagioAvaliacaoGrid', {
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
                title: 'Manifestação de Estágio Probatório'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getEstagioProbatorioAvaliadoGrid(),
                ]
            }
        );

        estagio.avaliador.Manage.superclass.constructor.call(this, cfg);
    }
});
