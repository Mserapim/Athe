/**
 *
 **/
Ext._define('estagio.gestor.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEstagioProbatorioServidorGrid: function() {
        if(!this._estagiogrid) {
            this._estagiogrid = Ext._create('estagio.gestor.EstagioProbatorioServidorGrid', {
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
                title: 'Gestor de Estágio Probatório'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getEstagioProbatorioServidorGrid(),
                ]
            }
        );

        estagio.gestor.Manage.superclass.constructor.call(this, cfg);
    }
});
